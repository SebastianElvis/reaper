# Trust and System Model Dimensions

Domain-specific reference for pinning down the dimensions of a research problem's trust and system model. The examples below are for cryptography and distributed systems. For other research domains, adapt this file with the relevant model dimensions for that field.

## Trust Assumption Checklist

Every dimension must have a concrete answer, not "TBD":

- **Communication**: point-to-point / broadcast / both? Authenticated channels? Reliable delivery?
- **Timing**: synchronous (known Delta) / partially synchronous (unknown Delta, known GST) / asynchronous?
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

Which cells in this matrix are empty? Those are candidate hypotheses.

## Importance Filter Examples

Prioritize hypotheses by consequence:
- A security proof gap that invalidates a deployed protocol > a tighter constant in a complexity bound
- An impossibility result that rules out an entire approach > an incremental improvement
- A finding that changes how practitioners build systems > a purely theoretical curiosity
