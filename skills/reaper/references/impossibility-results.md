# Impossibility Results and Lower Bounds

You treat this list as a source guide. You inspect the exact theorem before using it to reject a claim.
You record its task, validity condition, fault model, network, setup, randomization, cost unit, and parameter range.

## Distributed Computing

- FLP rules out guaranteed termination for deterministic consensus in its asynchronous message-passing model with a possible crash. It does not rule out safety or all randomized termination guarantees. You consult [Fischer, Lynch, and Paterson](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf).
- Byzantine resilience depends on synchrony, authentication, validity, and the task. You do not use one universal threshold. You inspect the relevant theorem in [Dwork, Lynch, and Stockmeyer](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf).
- Authenticated broadcast and consensus can have different validity requirements. You do not transfer a threshold between them without checking the definitions.
- Saks and Zaharoglou prove that deterministic wait-free k-set agreement is impossible for k < n in their asynchronous shared-memory model. You consult their [paper](https://courses.csail.mit.edu/6.852/08/papers/SaksZaharoglu.pdf). You verify the separate resilience reduction before claiming a general t-fault result.
- Dolev and Reischuk distinguish worst-case messages from signature counts. Their classical deterministic authenticated setting gives an Ω(n + t²) message bound and an Ω(nt) signature bound. Their unauthenticated setting gives an Ω(nt) message bound. You check the original model before applying these bounds. Quadratic growth requires a corresponding relation between t and n. You consult the [original publication](https://research.ibm.com/publications/bounds-on-information-exchange-for-byzantine-agreement--1).

## Cryptography

You check the exact hardness assumption and setup model. A PKI can change an impossibility result's premises; it does not remove every impossibility.
A random-oracle proof does not by itself prove security for a specific concrete hash function.

## Effect on the Research Question

A verified matching impossibility can resolve the user's question negatively.
You preserve the original claim and its evidence. You propose changed assumptions or weaker properties separately.
An uncertain model match remains unresolved. You do not discard a hypothesis based on this summary alone.
