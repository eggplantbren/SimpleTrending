import bigfloat as bf

# NOTE: Use deweys

HALF_LIFE = 400

def soften(lbc: float):
    assert lbc >= 0
    return lbc ** (1.0/3.0)

CONTEXT = bf.Context(precision=64, emax=1000000)
bf.setcontext(CONTEXT)

def inflate_units(height):
    return bf.pow(bf.BigFloat(2.0), height/HALF_LIFE)

def squash(value):
    """
    Input: a bigfloat
    Output: A regular float, after passing through a transformation to reduce the range
    """
    if value >= 0.0:
        return float(bf.log(1.0 + value))
    else:
        return -float(bf.log(1.0 - value))

def unsquash(value):
    """
    The inverse of squash()
    """
    if value >= 0.0:
        return bf.exp(value) - 1.0
    else:
        return 1.0 - bf.exp(-value)


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
        huge = inflate_units(height)*spike_mass(0, self.total_deweys)
        self.trending_score = squash(huge)

    def claim_update(self, new_bid, height):
        """
        Claim update that potentially changes the bid
        """
        old_deweys = self.total_deweys
        self.bid = new_bid

        huge = unsquash(self.trending_score)
        huge += inflate_units(height)*spike_mass(old_deweys, self.total_deweys)
        self.trending_score = squash(huge)


    def support_added(self, txo_amount_of_support, height):
        """
        support_amount is the ADDED support amount
        """
        old_deweys = self.total_deweys
        self.support_amount += txo_amount_of_support
        huge = unsquash(self.trending_score)
        huge += inflate_units(height)*spike_mass(old_deweys, self.total_deweys)
        self.trending_score = squash(huge)

    def support_abandoned(self, txo_amount_of_support, height):
        """
        Pass in the positive amount of the support that is being abandoned
        """
        old_deweys = self.total_deweys
        self.support_amount -= txo_amount_of_support
        huge = unsquash(self.trending_score)
        huge += inflate_units(height)*spike_mass(old_deweys, self.total_deweys)
        self.trending_score = squash(huge)

    @property
    def total_deweys(self):
        return self.bid + self.support_amount

    def __str__(self):
        return str(dict(claim_hash=self.claim_hash,
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
    for height in range(2, 2000):
        if height == 20:
            claim.support_added(100.0*COIN, height)
        if height % 1000 == 0:
            claim.support_added(100.0*COIN, height)
            print(height, claim.trending_score)

        xs.append(height)
        ys.append(claim.trending_score)


    # Transform to exponential for viewing. Will blow up if simulation is too long.
    xs, ys = np.array(xs), np.array(ys)
    ys[ys >= 0.0] = np.exp(ys[ys >= 0.0]) - 1.0
    ys[ys <  0.0] = 1.0 - np.exp(-ys[ys < 0.0])
    ys /= 2.0**(xs/HALF_LIFE)

    plt.plot(xs, ys)
    plt.show()


if __name__ == "__main__":
    simulate()
