# grSimReplacementTool

This is suport tool for [grsim](https://github.com/RoboCup-SSL/grSim) robots and ball replacement.

You can do replacement like [**this**](https://twitter.com/chmod_x_akasit/status/897458004672434176).

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


## Usage (example)

```zsh
# Usage :python main.py FILE [--set] [--log] [--help]

# Set replacement robots and ball from config file to grSim.
$ python main.py config/test.toml -s

# Log replacement robots and ball from grSim to config file.
$ python main.py config/read.toml -l
```

