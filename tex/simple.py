import matplotlib.pyplot as plt
import numpy as np

# Fonts for plot
plt.rc("font", size=14, family="serif", serif="Computer Sans")
plt.rc("text", usetex=True)

ts = np.arange(1, 1001)
kernel1 = np.zeros(len(ts))
kernel1[ts >= 50] += np.exp(-ts[ts >= 50]/576)
kernel1 = kernel1/np.max(kernel1)
kernel2 = np.zeros(len(ts))
kernel2[ts >= 550] += np.exp(-ts[ts >= 550]/576)
kernel2 = 3*kernel2/np.max(kernel2)
ys = kernel1 + kernel2

plt.plot(ts, ys, "-")
plt.xlabel("Block Height $t$")
plt.ylabel("Trending Score $Y$")
plt.savefig("figures/simple.pdf")
