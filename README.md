# powerlogger

A simple Python script to log measurements taken from a Voltcraft SEM-6000 smart
plug sold by *Conrad Elektronik* in Germany.

## voltcraft-sem-6000

All the hard work of actually talking to the SEM-6000 is done by this software,
[written in Expect by Heckie75](https://github.com/Heckie75/voltcraft-sem-6000).

The voltcraft-sem-6000 script, as well as Expect and gatttool have to be
available on the system. If you have more than one Bluetooth device on your
machine, you might need to set it inside `sem-6000.exp`. For example, change

`spawn -noecho /usr/bin/gatttool -I`

to

`spawn -noecho /usr/bin/gatttool -i hci0 -I`

Replace hci0 with hci1 etc. if necessary.

## Python requirements

Tested on Python 3.12, 3.13, and 3.14. No extra dependencies apart from the
standard library. However, the paths to `sem-6000.exp` as well as expect have
to be set inside the Python code. For the latter, the default is probably fine
though.

You will find further details on how to set your devices up in the excellent
documentation of voltcraft-sem-6000.

## Bluetooth MAC addresses

Set the BT_ADDRs inside the Python script as well. You can find them out by
plugging in your SEM-6000s one piece at a time and performing a Bluetooth scan.

## Actually doing something with the measurements

The script just prints the dictionary representing the measurement to the
screen. In my full setup, left out for simplicity here, the measurement is sent
to an InfluxDB time series database.
