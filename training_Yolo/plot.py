import os
from os.path import dirname, realpath
import sys
import matplotlib.pyplot as plt

dir_of_file = dirname(realpath(__file__))
dir_of_file = dir_of_file.replace("\\", '/')

print(dir_of_file)
log_file_path = dir_of_file + '/logFile_05_22.log'
print(log_file_path)

f = open(log_file_path)
lines = [line.rstrip("\n") for line in f.readlines()]
#print(lines)

numbers = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}

iters = []
loss = []

prev_line = ""
for line in lines:
    args = line.split(' ')
    if len(args) > 1:
        if args[1][-1:] == ':' and args[1][0] in numbers:
            # print('=====', args[1][-1:], args[1][0])
            iters.append(int(args[1][:-1]))
            loss.append(float(args[2].replace(",","")))

fig, ax = plt.subplots()
ax.plot(iters, loss)
plt.xlabel('iters')
plt.ylabel('loss')
plt.grid()

ticks = range(0, 250, 10)

# ax.set_yticks(ticks)
plt.show()

