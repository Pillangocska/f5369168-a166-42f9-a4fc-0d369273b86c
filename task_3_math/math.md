# Problem 1: How many digits does 2ⁿ contain?

The number of digits of a positive integer $k$ in base 10 is given by $\lfloor \log_{10}(k) \rfloor + 1$.

**Warum?**
A number $k$ has $d$ digits precisely when $10^{d-1} \leq k < 10^d$. Taking $\log_{10}$ of all sides gives $d - 1 \leq \log_{10}(k) < d$, which means $d = \lfloor \log_{10}(k) \rfloor + 1$.

So for $k = 2^n$:

$$d(n) = \lfloor \log_{10}(2^n) \rfloor + 1 = \lfloor n \cdot \log_{10}(2) \rfloor + 1$$

Since $\log_{10}(2) \approx 0.30103$, we get:

$$d(n) = \lfloor 0.30103 \cdot n \rfloor + 1$$

**Kurzcheck:** $2^{10} = 1024$ (4 digs). Our formula gives $\lfloor 10 \cdot 0.30103 \rfloor + 1 = \lfloor 3.0103 \rfloor + 1 = 3 + 1 = 4$. ✓

---

## Problem 2: Probability that at least one person gets their own name tag

We want $P(\text{at least one match})$, and it's easiest to compute via the complement:

$$P(\text{at least one match}) = 1 - P(\text{no one gets their own tag})$$

A permutation where *nobody* is in their correct position is called a **derangement**. The number of derangements $D_n$ is found using inclusion-exclusion.

**Inclusion-Exclusion derivation:** Let $A_i$ be the event that person $i$ gets their own tag. We want $P\left(\bigcup_{i=1}^n A_i\right)$.

$$P\!\left(\bigcup_{i=1}^n A_i\right) = \sum_{k=1}^{n} (-1)^{k+1} \binom{n}{k} \frac{(n-k)!}{n!}$$

Since $\binom{n}{k} \frac{(n-k)!}{n!} = \frac{1}{k!}$, this simplifies to:

$$P(\text{at least one match}) = \sum_{k=1}^{n} (-1)^{k+1} \frac{1}{k!} = 1 - \frac{1}{2!} + \frac{1}{3!} - \frac{1}{4!} + \cdots + (-1)^{n+1}\frac{1}{n!}$$

Equivalently:

$$P(\text{at least one match}) = \sum_{k=1}^{n} \frac{(-1)^{k+1}}{k!} = 1 - \sum_{k=0}^{n} \frac{(-1)^{k}}{k!}$$

Since $e^{-1} = \sum_{k=0}^{\infty} \frac{(-1)^k}{k!}$, the probability of *no* match converges to $1/e \approx 0.3679$ very quickly. So:

$$P(\text{at least one match}) \approx 1 - \frac{1}{e} \approx 0.6321$$

Some checks:

| $n$ | $P(\text{at least one match})$ |
|---|---|
| 2 | $1/2 = 0.500$ |
| 3 | $2/3 \approx 0.667$ |
| 4 | $5/8 = 0.625$ |
| 5 | $19/30 \approx 0.633$ |
| 10 | $\approx 0.6321$ |

So no matter how many people are in the room (as long as $n \geq 3$ or so), there's roughly a **63.2%** chance that at least one person ends up with their own name tag.
