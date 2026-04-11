# Research Methodology Patterns

Reference for conducting theoretical computer science research in cryptography, distributed systems, and blockchain.

## Key References

- **Shoup, "Sequences of Games: A Tool for Taming Complexity in Security Proofs"** (ePrint 2004/332, https://eprint.iacr.org/2004/332.pdf) — canonical tutorial on game-based (sequence of games) proofs. Covers the three transition types: indistinguishability-based, failure-event-based (with the Difference Lemma), and bridging steps. Required reading for any game-based security argument.
- **Lindell, "How To Simulate It — A Tutorial on the Simulation Proof Technique"** (ePrint 2016/046, https://eprint.iacr.org/2016/046.pdf) — canonical tutorial on simulation-based proofs. Covers semantic security, simulation for semi-honest and malicious adversaries, zero-knowledge, secure computation, and the CRS model. Required reading for any simulation-based security argument.

Consult these tutorials when constructing or verifying any cryptographic security proof. The proof techniques catalog in `investigate/SKILL.md` provides a quick-reference summary.

## Proof Verification

How to systematically verify an existing proof:

- **Check logical flow**: Does each step follow from the previous? Are there implicit "it follows that" jumps?
- **Identify assumptions**: List every assumption used (stated and unstated). Check if each is necessary.
- **Test boundary cases**: What happens at the corruption threshold exactly (t = n/3, t = n/2)? What about n = 1, n = 2?
- **Verify reductions**: Does the reduction actually work? Check:
  - The reduction receives the challenge correctly
  - The simulation is indistinguishable from the real execution
  - The reduction extracts the solution correctly
  - The security loss is acceptable (not exponential in a security parameter)
- **Check simulator constructions** (simulation-based security):
  - Does the simulator handle every possible adversary behavior?
  - Does the simulator handle abort / early termination?
  - Does the simulator run in expected polynomial time?
  - Can the simulator rewind? If so, is rewinding valid in the model (standalone vs UC)?
  - Does the environment/distinguisher see the same distribution in real vs ideal?
- **Verify game hops**: For game-based proofs, check each transition:
  - Is the change between games syntactic or computational?
  - Is the distinguishing advantage correctly bounded?
  - Do the games compose correctly (hybrid argument)?

## Security Analysis

### Threat Model Enumeration

Systematically vary the threat model dimensions:

| Dimension | Options |
|-----------|---------|
| Adversary type | Static, adaptive, mobile |
| Network | Synchronous, partially synchronous (known/unknown Δ), asynchronous |
| Corruption | t < n/3, t < n/2, t < n, dishonest majority |
| Adversary power | Crash, omission, Byzantine |
| Setup | PKI, CRS, trusted dealer, nothing |
| Computation | PPT, unbounded |

For each combination relevant to the investigation: does the claimed property still hold?

### Reduction Arguments

When constructing or verifying a reduction:

1. **Identify the hard problem**: What computational assumption underlies security?
2. **Build the reduction**: Given an adversary A that breaks property P, construct an algorithm B that solves the hard problem
3. **Check tightness**: What's the relationship between A's advantage and B's? Loose reductions (factor of q^k, 2^n) may give meaningless concrete security
4. **Check the model**: Does the reduction use the random oracle? The algebraic group model? Does it program the CRS?

### Common Pitfalls

- Abort handling: The simulator/reduction must handle the adversary aborting at any point
- Rewinding in UC: Rewinding is not allowed in the UC framework (use equivocation or straight-line extraction instead)
- Adaptive corruption: If the proof only handles static corruption, it does NOT apply to adaptive adversaries — the simulator must handle corruption queries at any time
- Network model mismatch: A proof under synchrony doesn't hold under partial synchrony unless explicitly shown
- Composition: Security in isolation doesn't imply security in composition (unless using UC or similar framework)

## Counterexample Construction

Systematic approach to disproving a claim:

### Start Small
1. Try n = 2 parties (or the minimum for the protocol)
2. Try f = 1 corrupted party
3. Try 1 round of communication
4. If a counterexample exists, it often exists in the smallest case

### Relax Assumptions One at a Time
- The claim holds under synchrony — does it hold under partial synchrony?
- The claim holds for static adversary — does it hold for adaptive?
- The claim holds for t < n/3 — does it hold for t = n/3?

### Adversary Strategy Enumeration
For the given protocol, what can the adversary do?
- Send contradictory messages to different parties
- Equivocate (send different values in the same round)
- Withhold messages (omission)
- Corrupt specific parties at specific times (adaptive)
- Manipulate message ordering (asynchrony)
- Delay messages up to the bound (partial synchrony)

### Execution Trace Construction
Build a concrete execution:
1. Fix the number of parties and the corrupted set
2. Specify the adversary's strategy (what messages it sends/withholds)
3. Trace the protocol execution step by step
4. Show that the claimed property is violated

## Protocol Comparison

When comparing protocols, use consistent dimensions:

| Dimension | How to Compare |
|-----------|---------------|
| Communication complexity | Per-round and total; words vs bits; best/worst/amortized case |
| Round complexity | Best case, worst case, expected; latency vs throughput |
| Trust assumptions | Corruption threshold, setup requirements, cryptographic assumptions |
| Security properties | Which properties are achieved? Under what model? |
| Finality | Probabilistic vs deterministic; latency to finality |
| Responsiveness | Does the protocol proceed at network speed or require known bounds? |
| Fairness | Is there leader bias? Can the adversary influence the output? |

**Fair comparison requires same model**: Comparing protocol A (async, t < n/3) with protocol B (sync, t < n/2) on communication complexity alone is misleading.

## When Stuck: 8-Step Escalation

When an investigation cycle is going nowhere:

1. **Re-read the paper.** Focus on sections you skimmed. The details you glossed over often contain the key insight or the hidden assumption.

2. **Re-read current-understanding.md.** What are you taking for granted? What assumptions haven't been questioned? Is there a hidden "of course" that might be wrong?

3. **Re-read results.md.** Look across discard cycles. Two dead ends might point to the same underlying issue. Patterns in failures are informative.

4. **Search for related work.** The specific technical question you're stuck on may have been answered elsewhere. Search for the precise sub-problem.

5. **Try a radically different approach.** Been trying direct proof? Try reduction. Been trying construction? Try impossibility. Been working top-down? Try bottom-up.

6. **Formulate a new hypothesis.** Maybe the original question is the wrong question. What has the investigation taught you? What's the *real* question?

7. **Invert the problem (Hamming).** Can't prove it? Try to disprove it. Can't find a counterexample? Ask: what is the *weakest* assumption that makes the proof work? The obstruction often IS the insight.

8. **Apply Qian's idea generation patterns:**
   - *Fill in the blank*: Map the design space (threat models × techniques × properties). What cell is empty?
   - *Start small then generalize*: What's the simplest non-trivial case? Solve that first. n=2, f=1, 1 round.
   - *Build a hammer*: Take a technique that worked in a previous cycle. Can it apply here differently?
