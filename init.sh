#!/bin/bash

echo "Create include directory"
mkdir include

echo "Compiling my protocol buffer ..."
protoc -I=proto --python_out=include proto/*.proto
touch include/__init__.py
