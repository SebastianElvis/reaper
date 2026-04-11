# Research Methodology Patterns

Reference for conducting theoretical computer science research in cryptography, distributed systems, and blockchain.

## Key References

- **Shoup, "Sequences of Games: A Tool for Taming Complexity in Security Proofs"** (ePrint 2004/332, https://eprint.iacr.org/2004/332.pdf) — canonical tutorial on game-based (sequence of games) proofs. Covers the three transition types: indistinguishability-based, failure-event-based (with the Difference Lemma), and bridging steps. Required reading for any game-based security argument.
- **Lindell, "How To Simulate It — A Tutorial on the Simulation Proof Technique"** (ePrint 2016/046, https://eprint.iacr.org/2016/046.pdf) — canonical tutorial on simulation-based proofs. Covers semantic security, simulation for semi-honest and malicious adversaries, zero-knowledge, secure computation, and the CRS model. Required reading for any simulation-based security argument.

Consult these tutorials when constructing or verifying any cryptographic security proof. The proof techniques catalog below provides a quick-reference summary.

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

## Proof Techniques Catalog

Choose the proof technique that matches the claim type. The technique determines the proof structure — don't mix paradigms within a single argument.

### Cryptographic Proof Techniques

See Shoup [ePrint 2004/332] for game-based proofs and Lindell [ePrint 2016/046] for simulation-based proofs.

| Technique | When to Use | Core Idea | Key Pitfalls |
|-----------|-------------|-----------|--------------|
| **Game-based (sequence of games / game hopping)** | Proving IND-CPA, IND-CCA, EUF-CMA, and similar computational security notions | Define a sequence of games G₀, G₁, ..., Gₖ where G₀ is the real security game and Gₖ is trivially secure. Bound the distinguishing advantage between each consecutive pair. Total advantage ≤ Σ advantages. | Each hop must be justified (syntactic change, computational assumption, or statistical argument). The sum of advantages must remain negligible. Don't lose track of which game you're in. |
| **Simulation-based (ideal/real paradigm)** | Proving security of MPC protocols, commitment schemes, zero-knowledge proofs — any setting where "security" means "the adversary learns nothing beyond the output" | Construct a simulator S that, given only the ideal-world output, produces a view indistinguishable from the adversary's real-world view. Security means: for every PPT adversary A, there exists PPT simulator S such that REAL_A ≈ IDEAL_S. | The simulator must handle ALL adversary behaviors including abort. Simulator must run in expected PPT. Rewinding is allowed in standalone but NOT in UC. The simulation must be indistinguishable — state precisely whether computationally, statistically, or perfectly. |
| **UC (Universal Composability)** | Proving security that holds under arbitrary concurrent composition with other protocols | Define an ideal functionality F. Prove that for every environment Z and adversary A, there exists a simulator S such that Z cannot distinguish the real protocol from the ideal interaction with F and S. | No rewinding allowed — use equivocation or straight-line extraction instead. The environment Z is the distinguisher and is the most powerful entity. Composition theorem gives security for free but proving UC security is strictly harder than standalone. |
| **Reduction** | Proving hardness-based security — "breaking the scheme implies solving a hard problem" | Given adversary A that breaks property P with advantage ε, construct algorithm B that solves hard problem H with advantage related to ε. | Check tightness (see Reduction Quality Gate below). Reduction must handle ALL oracle queries. Watch for exponential security loss in multi-instance settings. Programming random oracle / CRS must produce correct distribution. |
| **Hybrid argument** | Bounding advantage across many instances or many rounds | Define hybrid distributions H₀, ..., Hₙ that interpolate between two endpoints. Show adjacent hybrids are indistinguishable. | Security loss is typically linear in the number of hybrids (n). For n exponential in security parameter, the argument gives nothing useful. Consider tight reductions or complexity leveraging. |

### Distributed Computing Proof Techniques

| Technique | When to Use | Core Idea | Key Pitfalls |
|-----------|-------------|-----------|--------------|
| **Safety by invariant** | Proving agreement, consistency, validity | Define a predicate Inv over global states. Show: (1) Inv holds initially, (2) every protocol step preserves Inv, (3) Inv implies the safety property. | The invariant must be inductive — it must be preserved by EVERY possible step, including adversarial ones. A common error is proving the invariant holds for honest steps but not for Byzantine behavior. |
| **Liveness by eventual argument** | Proving termination, progress, fairness | Show that under the timing/fault assumptions, some progress measure eventually increases or some good event eventually occurs. Often: after GST, honest messages arrive within Δ, so a decision is reached within f(Δ, n, t) time. | Liveness proofs under partial synchrony must be explicit about what happens before GST (nothing is guaranteed) vs after GST. Don't assume synchrony holds globally. FLP means you need randomization or partial synchrony — be clear which you use. |
| **Indistinguishability / partitioning** | Proving impossibility results, lower bounds | Construct two executions that are indistinguishable to some party or set of parties, yet require different outputs — a contradiction. Classic: partition n parties into groups that can't tell which partition they're in. | The indistinguishability argument must account for ALL information available to the parties, including message timing in synchronous models. |
| **Bivalence / valency** | Proving FLP-style impossibility | Show that an initial configuration is bivalent (both 0 and 1 are reachable). Show that every deterministic step from a bivalent configuration leads to another bivalent configuration or a contradiction with fault tolerance. | Only applies to deterministic protocols. Randomized protocols circumvent FLP via probabilistic termination. |
| **Counting / quorum intersection** | Proving properties of quorum-based protocols | Show that any two quorums intersect in enough honest parties to guarantee consistency. For n = 3t+1: any two sets of 2t+1 intersect in t+1, of which at least 1 is honest. | The intersection argument fails if the corruption threshold is violated. Be precise about whether you need "at least one honest in intersection" vs "honest majority in intersection." |

## Reduction Quality Gate

Every reduction-based argument must answer ALL of the following before being marked `confirmed`. If any answer is "unclear" or "not applicable" without justification, the cycle outcome must be `inconclusive`, not `confirmed`.

1. **Embedding**: How is the challenge instance embedded in the protocol? Is the embedding perfect, statistical, or computational?
2. **Simulation**: Does the simulator handle ALL adversary queries? List the query types (signing, corruption, random oracle, etc.) and how each is answered.
3. **Extraction**: How is the solution extracted from a successful adversary? Does extraction work for ALL winning conditions in the security game?
4. **Tightness**: What is the concrete security loss? Express as ε_scheme ≤ f(ε_assumption, q, ...). Is f polynomial in all parameters? If the loss is superpolynomial, the reduction gives no meaningful concrete security.
5. **Rewinding**: Does the reduction rewind the adversary? If yes, is rewinding valid in the stated composition model? (Rewinding is NOT valid in UC.)
6. **Abort analysis**: What happens if the adversary aborts mid-protocol? Does the reduction still extract or must it restart?
7. **Programming**: Does the reduction program the random oracle / CRS? If so, is the programmed distribution indistinguishable from the real one?

## Performance Sanity Checks

Before accepting any performance or complexity claim:

- **Lower bounds**: Compare against known lower bounds for the problem class. A claim of O(n) communication for Byzantine agreement without threshold signatures contradicts Dolev-Reischuk (Ω(n²)).
- **Concrete instantiation**: Plug in small concrete values (n=4, n=10, n=100). Does the concrete number make sense? Does it exceed trivially achievable bounds?
- **Comparison**: Compare against the performance of existing solutions to the same problem under the same model. A claimed improvement must actually improve.
- **Units**: Check units carefully — bits vs words vs field elements; per-round vs total; per-decision vs amortized; worst-case vs expected.
