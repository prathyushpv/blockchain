#!/usr/bin/python
from os import system
from json import dumps
from time import sleep
nodes = 5

for node in range(nodes):
    system("pipenv run python blockchain.py -p %d &" % (5000 + node))

system("pipenv run python blockchain_adversary.py -p %d &" % (5000 + nodes))

sleep(5)

data = {"nodes": []}

for node in range(nodes+1):
    data["nodes"].append("http://localhost:%d" % (5000 + node))

for node in range(nodes+1):
    system("curl -X POST -H \"Content-Type: application/json\" -d '%s'  'http://localhost:%d/nodes/register'"
           % (dumps(data), (5000+node)))

