#!/bin/python  
import sys
import matplotlib.pyplot as plt
import numpy as np

file_name = sys.argv[1]
title = sys.argv[2]
fig_name = sys.argv[3]

nodes_runtime = []
nodes_processors = []
#nodes_intervals = []

laptop_runtime = 0.
laptop_processors = 0.
#laptop_intervals = 0.0

with open(file_name,"r") as file_:
    for line in file_:
        
        items = line.split(' ')
        if items[0] == 'nodes':
            nodes_runtime.append(float(items[1])/1000.)
            nodes_processors.append(int(items[2]))
            #nodes_intervals.append(int(items[3]))
        
        elif items[0] == 'laptop':
            laptop_runtime = float(items[1])/1000.
            laptop_processors = int(items[2])
            #laptop_intervals = int(items[3])

cluster_label = "Cluster " + str(nodes_processors[0]) + "-" + str(nodes_processors[len(nodes_processors)-1]) + " cores"
laptop_label = "Laptop " + str(laptop_processors) + " cores"

fig, ax = plt.subplots()
ax.plot(nodes_processors, nodes_runtime,'o-', label=cluster_label)
ax.plot(nodes_processors,[laptop_runtime for i in range(len(nodes_processors))],'--', label=laptop_label)
ax.set(xlabel='Processors [cores]', ylabel='Runtime [seconds]', title=title)
ax.legend()
ax.grid()

fig.savefig(fig_name)


