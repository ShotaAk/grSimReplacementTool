# grSimReplacementTool

This is suport tool for [grsim](https://github.com/RoboCup-SSL/grSim) robots and ball replacement.

You can do replacement like [**this**](https://twitter.com/chmod_x_akasit/status/897835136380682240) 
and [**this**](https://twitter.com/chmod_x_akasit/status/897458004672434176).

## Requirements
This tool tested on Ubuntu 14.04 and python (2.7.6).

Please install some libraries following...

* [**toml**](https://github.com/uiri/toml) - Python library for TOML.
* [**Google Protocol Buffers**](https://github.com/google/protobuf) - Google's data interchange format.


## Installation

```zsh
# Compile .proto files
$ ./init.sh
```

Before using this tool, please rewrite multicast address and port 
in Sender and Receiver class.


*main.py*
```python
class Sender:
    def __init__(self):
        # initialize a socket
        self._addr = "127.0.0.1"
        self._port = 20012
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
```

```python
class Receiver:
    def __init__(self):
        self._addr = "224.5.23.2"
        self._port = 10006
        self._collecting_time = 1.5
```

## Usage (example)

```zsh
# Usage :python main.py FILE [--set] [--log] [--help]

# Set replacement robots and ball from config file to grSim.
$ python main.py config/test.toml -s

# Log replacement robots and ball from grSim to config file.
$ python main.py config/read.toml -l
```

