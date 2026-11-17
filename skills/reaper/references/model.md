# Trust and System Model Dimensions

Domain-specific reference for pinning down the dimensions of a research problem's trust and system model. The examples below are for cryptography and distributed systems. For other research domains, adapt this file with the relevant model dimensions for that field.

## Trust Assumption Checklist

You specify each applicable dimension. You identify missing assumptions rather than inventing them.

- **Communication**: point-to-point / broadcast / both? Authenticated channels? Reliable delivery?
- **Timing**: synchronous (known Delta) / partially synchronous (unknown fixed bounds, or known bounds after an unknown stabilization time) / asynchronous?
- **PKI/setup**: plain model / PKI / CRS / trusted dealer / random oracle / algebraic group model?
- **Corruption timing**: static (before execution) / adaptive (during execution) / mobile (between epochs)?
- **Corruption power**: crash / omission / Byzantine / covert?
- **Corruption bound**: exact expression (e.g., t < n/3, t < n/2). State whether the bound is strict.
- **Computation**: PPT / information-theoretic (unbounded adversary)?
- **Composition**: standalone / sequential / UC / GUC?
- **Cryptographic assumptions**: e.g., DDH, CDH, LWE, random oracle model. List all.
- **Protocol-specific assumptions**: e.g., honest dealer in setup phase, synchronous bootstrap period.

## Gap-Finding Matrix

Map the dimensions of existing work and find unexplored combinations. Example dimensions for crypto/distributed systems:

- Threat models (static/adaptive x sync/async/partial-sync x corruption thresholds)
- Protocol families (leader-based, leaderless, DAG-based, etc.)
- Security properties (safety, liveness, fairness, accountability, etc.)

An empty cell suggests a candidate question. You check its relevance, feasibility, and prior work before assigning value.

## Priorities

You rank questions by the user's goal and the consequence of resolving them.
A practical flaw, a tighter bound, or a theoretical result can matter under different goals. You do not use one universal ranking.
You use [Hamming's advice](https://www.cs.virginia.edu/~robins/YouAndYourResearch.html) as a prompt to explain importance, not as permission to replace the user's question.
The partial-synchrony examples follow the two models in [Dwork, Lynch, and Stockmeyer](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf).
