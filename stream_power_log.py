#!/usr/bin/env python3

import subprocess
import time
import threading
import queue


USED_PLUG_IDS = ('test', )

RING_BUFFER_SIZE = 5

# Set your plugs' Bluetooth MAC addresses (BD_ADDR) here.
ALL_PLUG_IDS = {
    'test':         '00:00:00:00:00:00',
    'desk':         '00:00:00:00:00:00',
    'kitchen':      '00:00:00:00:00:00',
    'living_room,': '00:00:00:00:00:00',
}

ACTIVE_PLUG_IDS = {
    name: ALL_PLUG_IDS[name] for name in (USED_PLUG_IDS)
}


# Implement here the connection to your database or logging solution.
def log_to_database(result):
    print(f"I am writing {result} to the database!")


def measure_stream_function(device: str, the_queue: queue.SimpleQueue):

    # Set your paths to expect and sem-6000.exp here.
    exe = '/usr/bin/expect'
    measure_script = '/home/christian/small_stuff/voltcraft-sem-6000/sem-6000.exp'

    while True:
        process = subprocess.Popen(
            [exe, measure_script, ALL_PLUG_IDS[device], '0000',  '--measure'], stdout=subprocess.PIPE
        )
        power_ringbuffer = queue.deque(maxlen=RING_BUFFER_SIZE)
        sent_power_ringbuffer = queue.deque(maxlen=RING_BUFFER_SIZE)
        invalid_ringbuffer = queue.deque(maxlen=RING_BUFFER_SIZE)
        n_repetitions = 0

        while True:
            line = process.stdout.readline()

            line = line.decode().strip()
            columns = line.split('\t')
            try:
                power = columns[4]
            except IndexError:
                print(f'# No power reading found for {device}, terminating.')
                process.kill()
                break

            real_power = float(power)

            if real_power >= 0.0:
                power_ringbuffer.append(real_power)
            else:
                invalid_ringbuffer.append(real_power)
                print(f'# Not sending because of invalid value: {device} {power}')

                if len(invalid_ringbuffer) == RING_BUFFER_SIZE:
                    if min(invalid_ringbuffer) == max(invalid_ringbuffer):
                        print(f'# Got same invalid value for {device} {RING_BUFFER_SIZE} times, terminating.')
                        process.kill()
                        break

                continue

            if len(power_ringbuffer) == RING_BUFFER_SIZE:
                if min(power_ringbuffer) == max(power_ringbuffer):
                    n_repetitions += 1
                    print(f'# Not sending because of repetition {n_repetitions}: {device} {power}')
                else:
                    n_repetitions = 0
                    the_queue.put((time.time(), device, line, power))
                    sent_power_ringbuffer.append(real_power)

            else:
                the_queue.put((time.time(), device, line, power))

            if process.poll() is not None:
                break

            if n_repetitions >= RING_BUFFER_SIZE:
                n_repetitions = 0
                the_queue.put((time.time(), device, line, power))
                sent_power_ringbuffer.append(real_power)

                if len(sent_power_ringbuffer) == RING_BUFFER_SIZE:
                    if min(sent_power_ringbuffer) == max(sent_power_ringbuffer):
                        print(f'# Sent same signal for {device} {RING_BUFFER_SIZE} times, terminating.')
                        process.kill()
                        break

        print(f'# Thread for {device} terminated, trying to restart.')
        time.sleep(2.0)


if __name__ == '__main__':
    john_de_lancie = queue.SimpleQueue()
    threads = list()

    for device in ACTIVE_PLUG_IDS:
        x = threading.Thread(target=measure_stream_function, args=(device, john_de_lancie, ))
        threads.append(x)
        x.start()

    while True:
        try:
            t1, device, line, power = john_de_lancie.get()
            print(line, device)
            result = {
                'measurement': 'power',
                'value': power,
                'time': f'{1000 * t1:.0f}',
                'sensor': ALL_PLUG_IDS[device],
                'precision': 'ms',
                'extra_tags': f'location={device}',
            }
            log_to_database(result)
        except Exception as e:
            print('Error parsing line:', e)
