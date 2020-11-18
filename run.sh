#!/bin/bash
./redis-6.0.6/src/redis-server --port 6379 &
redis-commander --port 40009 &
jupyter lab --port 40011 --allow-root --ip 0.0.0.0 --NotebookApp.token=''