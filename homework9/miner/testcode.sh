#!/bin/sh
xterm -e "python miner.py localhost:10021 localhost:10020,localhost:10022,localhost:10023;read" & 
xterm -e "python miner.py localhost:10022 localhost:10021,localhost:10020,localhost:10023;read" & 
xterm -e "python miner.py localhost:10023 localhost:10021,localhost:10022,localhost:10020;read" & 
xterm -e "python miner.py localhost:10020 localhost:10021,localhost:10022,localhost:10023 genesis;read" & 