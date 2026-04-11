# Known Impossibility Results and Lower Bounds

Domain-specific reference for screening hypotheses against fundamental limits. The examples below are for cryptography and distributed systems. For other research domains, adapt this file with the relevant impossibility results and lower bounds for that field.

## Distributed Computing

- **FLP** [Fischer, Lynch, Paterson 1985]: No deterministic consensus in asynchrony with even 1 crash fault
- **DLS** [Dwork, Lynch, Stockmeyer 1988]: No partially-synchronous consensus tolerating t >= n/3 Byzantine faults
- **Byzantine agreement bound**: Requires t < n/3 without trusted setup (or t < n/2 with PKI + randomization)
- **Dolev-Strong**: Authenticated broadcast requires t < n
- **Fischer-Lynch-Merritt**: k-set agreement impossible with t >= k crash faults in async
- **Communication lower bounds**: Omega(n^2) for deterministic Byzantine agreement without threshold signatures (Dolev-Reischuk)

## Cryptography

- **Authenticated channels**: Many impossibilities disappear with a PKI — check whether the paper's model includes one
- **One-way functions**: If P = NP, no one-way functions exist (and thus no secure encryption, signatures, etc.)
- **Random oracle pitfalls**: Schemes secure in the random oracle model may be insecure when the oracle is instantiated with a concrete hash function

## How to Use

For each hypothesis, check whether it contradicts a known impossibility or lower bound from this list. If it does:

1. **Flag it explicitly** in the hypothesis with a warning
2. **Reformulate**: "Under what additional assumptions does this become possible?" or "What weaker property can be achieved?"
3. Do NOT leave it as a hypothesis for the investigate skill to waste cycles on
