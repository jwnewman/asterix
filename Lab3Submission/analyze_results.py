import numpy as np
import os
import matplotlib.pyplot as plt

pull_dir = "/Users/aaronschein/Documents/courses/spring14/systems/labs/asterix/latencies/pull"
push_dir = "/Users/aaronschein/Documents/courses/spring14/systems/labs/asterix/latencies/push"

things = {}
for subdir in os.listdir(push_dir):
	latencies = []
	fulldir = os.path.join(push_dir, subdir)
	for txt in os.listdir(fulldir):
		latencies += [float(x) for x in open(os.path.join(fulldir, txt), "r").readlines()]
	things[subdir] = (np.mean(latencies), np.std(latencies))

keys = sorted([int(x) for x in things.keys()])
vals = [things[str(x)][0] for x in keys]

plt.plot(keys[:5], vals[:5], 'go-', lw=2, label="push")
plt.ylabel("Avg. latency (sec)")
plt.xlabel("Num. of clients")
# plt.title("Latency of Server Push Architecture")


things = {}
for subdir in os.listdir(pull_dir):
	latencies = []
	fulldir = os.path.join(pull_dir, subdir)
	for txt in os.listdir(fulldir):
		latencies += [float(x) for x in open(os.path.join(fulldir, txt), "r").readlines()]
	things[subdir] = (np.mean(latencies), np.std(latencies))

keys = sorted([int(x) for x in things.keys()])
vals = [things[str(x)][0] for x in keys]

plt.plot(keys, vals, 'mo-', lw=2, label="pull")
plt.legend(("push", "pull"), loc="upper left")
plt.title("Comparison of latency in pull vs. push architectures")
plt.show()
