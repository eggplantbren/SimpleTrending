import math

# NOTE: Use deweys for amounts, except in the soften() function where the conversion
# to LBC is assumed to have already occurred.

LOG_TWO = math.log(2.0)
HALF_LIFE = 399.2527760025285

def soften(lbc: float):
    assert lbc >= 0
    return lbc ** (1.0/3.0)

def logsumexp(x, y):
    top = max(x, y)
    return top + math.log(math.exp(x - top) + math.exp(y - top))

def logdiffexp(big, small):
    assert big > small
    return big + math.log(1.0 - math.exp(small - big))

def squash(x):
    if x < 0.0:
        return -math.log(1.0 - x)
    else:
        return math.log(x + 1.0)

def unsquash(x):
    if x < 0.0:
        return 1.0 - math.exp(-x)
    else:
        return math.exp(x) - 1.0


def squashed_add(x, y):
    """
    squash(unsquash(x) + unsquash(y)) but avoiding overflow.
    """

    # Cases where the signs are the same
    if x < 0.0 and y < 0.0:
        return -logsumexp(-x, logdiffexp(-y, 0.0))
    if x >= 0.0 and y >= 0.0:
        return logsumexp(x, logdiffexp(y, 0.0))

    # Where the signs differ
    if x >= 0.0 and y < 0.0:
        if abs(x) >= abs(y):
            return logsumexp(0.0, logdiffexp(x, -y))
        else:
            return -logsumexp(0.0, logdiffexp(-y, x))
    if x < 0.0 and y >= 0.0:
        # Addition is commutative, hooray for new math
        return squashed_add(y, x)

    return None

def squashed_multiply(x, y):
    """
    squash(unsquash(x)*unsquash(y)) but avoiding overflow.
    """
    sign = 1 if x*y >= 0.0 else -1
    return sign*logsumexp(squash_to_log(abs(x)) + squash_to_log(abs(y)), 0.0)


def log_to_squash(x):
    return logsumexp(x, 0.0)


def squash_to_log(x):
    assert x > 0.0
    return logdiffexp(x, 0.0)


def inflate_units(height):
    """
    Log of inflated units.
    """
    return height/HALF_LIFE * LOG_TWO

def inflate_units2(height):
    """
    Squash of inflated units.
    """
    return log_to_squash(inflate_units(height))


def spike_mass(old_deweys, new_deweys):
    """
    Returns spike mass
    """
    old_lbc, lbc = 1E-8*old_deweys, 1E-8*new_deweys

    softened_change = soften(abs(lbc - old_lbc))
    change_in_softened = abs(soften(lbc) - soften(old_lbc))

    if lbc < 50.0:
        power = 0.5
    elif lbc < 85.0:
        power = lbc/100.0
    else:
        power = 0.85

    mass = change_in_softened**power * softened_change**(1.0 - power)

    # Handle negative spikes
    if lbc < old_lbc:
        mass *= -1.0

    return mass



class Claim:

    def __init__(self, claim_hash, bid, height):
        """
        Claim creation
        """
        self.claim_hash, self.bid = claim_hash, bid
        self.support_amount = 0

        y = spike_mass(0.0, self.total_deweys)
        self.trending_score = squashed_multiply(inflate_units2(height),
                                                squash(y))

    def claim_update(self, new_bid, height):
        """
        Claim update that potentially changes the bid
        """
        old_deweys = self.total_deweys
        self.bid = new_bid

        y = spike_mass(old_deweys, self.total_deweys)
        self.trending_score = squashed_add\
                                (self.trending_score,
                                 squashed_multiply(inflate_units2(height), squash(y)))


    def support_added(self, txo_amount_of_support, height):
        """
        txo_amount_of_support is the ADDED support amount
        """
        old_deweys = self.total_deweys
        self.support_amount += txo_amount_of_support

        y = spike_mass(old_deweys, self.total_deweys)
        self.trending_score = squashed_add\
                                (self.trending_score,
                                 squashed_multiply(inflate_units2(height), squash(y)))

    def support_abandoned(self, txo_amount_of_support, height):
        """
        Pass in the positive amount of the support that is being abandoned
        """
        old_deweys = self.total_deweys
        self.support_amount -= txo_amount_of_support

        y = spike_mass(old_deweys, self.total_deweys)
        self.trending_score = squashed_add\
                                (self.trending_score,
                                 squashed_multiply(inflate_units2(height), squash(y)))


    @property
    def total_deweys(self):
        return self.bid + self.support_amount

    def __str__(self):
        return str(dict(claim_hash=self.claim_hash,
                        bid=self.bid,
                        support_amount=self.support_amount,
                        trending_score=self.trending_score))



def simulate():
    import matplotlib.pyplot as plt
    import numpy as np

    COIN = int(1E8)

    claim = Claim("abc", 1.0*COIN, 1)
    xs, ys = [], []
    xs.append(1.0)
    ys.append(claim.trending_score)
    for height in range(2, 100001):

        if height == 20:
            claim.support_added(100.0*COIN, height)

        if height == 500:
            claim.support_abandoned(100.0*COIN, height)

        if height % 1000 == 0:
            claim.support_added(100.0*COIN, height)

        xs.append(height)
        ys.append(claim.trending_score)
        print(height, claim.trending_score)


    # Transform first 10K blocks to exponential for viewing.
    xs, ys = np.array(xs), np.array(ys)
    xs, ys = xs[0:10000], ys[0:10000]
    ys[ys >= 0.0] = np.exp(ys[ys >= 0.0]) - 1.0
    ys[ys <  0.0] = 1.0 - np.exp(-ys[ys < 0.0])
    ys /= 2.0**(xs/HALF_LIFE)

    plt.plot(xs, ys)
    plt.show()

def test_jack():
    claim = Claim("abc", 10*1E8, 99000)
    print(claim.trending_score)
    claim.claim_update(100*1E8, 99001)
    print(claim.trending_score)
    claim.claim_update(1000000*1E8, 99100)
    print(claim.trending_score)
    claim.claim_update(1*1E8, 99200)
    print(claim.trending_score)

def test_squash():
    import numpy as np
    import numpy.random as rng

    for _ in range(1000):
        x, y = 10.0*rng.randn(2)
        print("(x, y) =", (x, y))
        result1 = squash(unsquash(x) + unsquash(y))
        result2 = squashed_add(x, y)
        print("Should be ~= 0:", result2 - result1)
        result1 = squash(unsquash(x)*unsquash(y))
        result2 = squashed_multiply(x, y)
        print("Should be ~= 0:", result2 - result1)
        print("")


if __name__ == "__main__":
    simulate()
