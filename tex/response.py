import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append("../")
from simple_trending import *

# Fonts for plot
plt.rc("font", size=14, family="serif", serif="Computer Sans")
plt.rc("text", usetex=True)

COIN = 1E8

claim = Claim("abc", 1.0*COIN, 1)
xs, ys = [], []
xs.append(1.0)
ys.append(claim.trending_score)
for height in range(2, 1000):

    if height == 20:
        claim.support_added(100.0*COIN, height)

    if height == 500:
        claim.support_added(1000.0*COIN, height)

    if height == 700:
        claim.support_abandoned(1000.0*COIN, height)

    xs.append(height)
    ys.append(claim.trending_score)


plt.plot(xs, ys, label="Squashed $S(Z)$")

# Transform first 10K blocks to exponential for viewing.
xs, ys = np.array(xs), np.array(ys)
ys[ys >= 0.0] = np.exp(ys[ys >= 0.0]) - 1.0
ys[ys <  0.0] = 1.0 - np.exp(-ys[ys < 0.0])

plt.plot(xs, ys, label="Sparse $Z$")
ys /= 2.0**(xs/HALF_LIFE)

plt.plot(xs, ys, label="Original $Y$")

plt.xlabel("Time $t$ (blocks)")
plt.ylabel("Trending Score")
plt.legend()
plt.show()

