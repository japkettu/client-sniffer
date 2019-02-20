# client-sniffer

A poor man's Kismet for detecting wireless network clients and probe requests. Written in Python 2.7.15. 

## Usage:

Set a wireless interface to monitor mode (e.g):

```sh
$ airmon-ng start <interface>
```

Launch client-sniffer:

```sh
$ python2 main.py <interface in monitor mode>
```


## Dependencies:

- ncurses


## ToDo:

- GPS support
- sqlite3 database
