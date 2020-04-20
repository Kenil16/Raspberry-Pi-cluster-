#!/bin/python  

import sys
import matplotlib.pyplot as plt
import numpy as np

fig_name = sys.argv[1]
number_of_tests = sys.argv[2]

nodes_best_runtime = []
laptop_best_runtime = []

for i in range(3,(int(number_of_tests) + 3)):
    with open(sys.argv[i],"r") as file_:
        for line in file_:
        
            items = line.split(' ')
            if (items[0] == "nodes") and (int(items[2]) == 12):
                nodes_best_runtime.append(float(items[1])/1000.)
                print(line)

            elif items[0] == 'laptop':
                laptop_best_runtime.append(float(items[1])/1000.)

diff = []

print(nodes_best_runtime)
print(laptop_best_runtime)

for i in range(int(number_of_tests)):
    diff.append(nodes_best_runtime[i]-laptop_best_runtime[i])

bar = [nodes_best_runtime[0],laptop_best_runtime[0]]
cluster_label = "Cluster " + str(12) + " cores"
laptop_label = "Laptop " + str(4) + " cores"

x = ['Cluster 12 cores','Laptop 4 cores']

fig, ax = plt.subplots()
ax.bar(x,bar)
ax.legend()
ax.grid()
ax.set(ylabel='Runtime [seconds]', title="Runtime of 12 cores cluster in regard to 4 cores laptop")
fig.savefig(fig_name)

