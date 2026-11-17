# Research Methods

These methods support cryptography and distributed systems research. You use only the checks that apply to the stated claim.

## Proof Verification

You check each logical step against its definitions, assumptions, and cited results.
You test boundary cases within the stated model. A case outside that model tests a different claim.
You distinguish a false theorem from a failed proof. You retain useful negative results and unresolved gaps.
You can combine proof techniques when you justify their interfaces. A simulation argument can use a sequence of games.

For game transitions, you can consult [Shoup's tutorial](https://eprint.iacr.org/2004/332).
For simulation arguments, you can consult [Lindell's tutorial](https://eprint.iacr.org/2016/046).
You read the relevant sections when needed. These references do not require a full reread for each proof.

## Security Definitions and Composition

You state the adversary, network, corruption threshold, setup, computation model, and claimed property.
You distinguish computational, statistical, and perfect security. You use the simulator runtime required by the selected definition.
A simulation can receive permitted ideal-world inputs, outputs, leakage, and functionality access. You do not assume that it receives only the output.

For standard UC security, the quantifier order is: for every adversary A, there exists a simulator S, such that every environment Z has indistinguishable real and ideal executions.
The simulator can depend on A. It cannot depend on the choice of Z. You check the precise formulation in [Canetti's UC definition](https://par.nsf.gov/servlets/purl/10256860). You cite the equivalence conditions if you use a different quantifier order.
The simulator cannot rewind an external environment. You check what execution the proof rewinds and whether the model permits that operation.
The use of rewinding alone does not establish that a protocol lacks composable security.
You apply a composition theorem only after checking its setup, session, corruption, and subroutine conditions. Shared setup may require a different theorem.

## Reduction Quality Gate

Before confirming a reduction argument, you check these items:

1. The challenge embedding has the required distribution.
2. The simulation handles every permitted query and corruption event.
3. The extraction covers the winning conditions in the security definition.
4. The advantage bound includes query counts, parameters, loss, and runtime. You distinguish an asymptotic proof from a useful concrete bound.
5. The model permits any rewinding and oracle or setup programming.
6. The argument handles aborts and bounds the probability of failure.
7. The conclusion follows under the stated hardness assumption and parameter choices.

You justify each inapplicable item. An unresolved necessary step makes the result inconclusive.

## Counterexamples

You start with a small admissible instance. You specify the inputs, parameters, adversary behavior, and execution trace.
You verify that the trace follows the protocol and violates the stated property.
A counterexample outside the allowed assumptions does not refute the original claim.
You explore relaxed assumptions only as separate questions.

## Distributed Proof Methods

| Method | Required check |
|---|---|
| Safety invariant | You prove initialization and preservation under every permitted step. You show that the invariant implies safety. |
| Liveness | You state scheduling, fairness, timing, and probability assumptions. You separate safety before stabilization from eventual termination. |
| Indistinguishability | You account for every observation available to each relevant party, including timing. |
| Bivalence | You show a bivalent initial state and a schedule that preserves bivalence. You do not claim that every next step preserves it. |
| Quorum intersection | You prove the required number of honest parties in the intersection under the stated fault threshold. |

You check [impossibility-results.md](impossibility-results.md) before applying a lower bound.
FLP concerns deterministic termination in its asynchronous crash model. A changed model, such as a failure detector, can change the result.

## Performance and Comparisons

You compare the same task, threat model, validity condition, parameters, and cost unit.
You distinguish messages, signatures, words, and bits. You separate worst-case, expected, amortized, and observed costs.
You compare latency and throughput separately. You identify setup costs and cryptographic assumptions.
You check parameter ranges and lower-bound assumptions before claiming a contradiction.
A threshold signature alone does not settle whether a communication lower bound applies.

## When Progress Stops

You select an option that addresses the current obstacle within the remaining budget:

- You reread the relevant source or definition.
- You inspect earlier failures for a common missing assumption.
- You search for a result about the precise unresolved step.
- You change proof method or construct a counterexample.
- You propose a clearly labeled weaker claim or different model.

Qian's [idea-generation advice](https://medium.com/digital-diplomacy/how-to-look-for-ideas-in-computer-science-research-7a3fa6f4696f) suggests design-space gaps, reusable techniques, and small starting cases.
These are candidate-generation methods. A gap does not establish novelty, feasibility, or importance.
You stop when no distinct useful method remains. You do not repeat a fixed escalation sequence without new evidence.
