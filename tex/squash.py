import matplotlib.pyplot as plt
import numpy as np

# Fonts for plot
plt.rc("font", size=14, family="serif", serif="Computer Sans")
plt.rc("text", usetex=True)

xs = np.linspace(-100.0, 100.0, 10001)
ys = np.empty(len(xs))
rhs = xs >= 0.0
ys[rhs] = np.log(xs[rhs] + 1.0)
ys[~rhs] = -np.log(1.0 - xs[~rhs])
plt.plot(xs, ys, "k-", label="Squashed $S(x)$")
plt.plot(xs[xs > 0.0], np.log(xs[xs > 0.0]), "b--", alpha=0.5, label="$\log(x)$")
plt.plot(xs[xs < 0.0], -np.log(-xs[xs < 0.0]), "r--", alpha=0.5, label="-$\log(-x)$")
plt.xlabel("Value $x$")
plt.ylabel("Transformed Value")
plt.legend()
plt.savefig("figures/squash.pdf")

