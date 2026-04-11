# Paper Analysis Guide

Reference for extracting structured information from academic papers in cryptography, distributed systems, and blockchain.

## Reading Strategy

Don't read linearly. Use three passes:

**Pass 1 — Skeleton (5 min)**
- Abstract, introduction, conclusion, theorem statements
- Identify: what does the paper claim? What problem does it solve? What are the main results?
- Read the contribution list carefully — this is what the authors think matters

**Pass 2 — Construction & Proof Sketches (15 min)**
- Protocol/construction details, proof sketches, figures and diagrams
- Understand the high-level approach: what building blocks are used? What's the key technical idea?
- Map the dependency chain: which lemmas feed into which theorems?

**Pass 3 — Full Proofs & Details (as needed)**
- Full formal proofs, appendices, security reductions
- Verify each logical step — don't trust "it is easy to see"
- Check boundary cases: what happens with 1 party? With f = 0? With f = n-1?

**Critical distinction**: Separate what the paper *claims* from what it *actually proves*. Authors sometimes claim security under model X but prove it under model Y, or claim a property in the introduction that the theorem statement doesn't quite capture.

## What to Extract

### Metadata
- Title, authors, affiliations, venue, year
- Paper ID (ePrint number, arXiv ID, DOI)

### Problem Statement
- What problem does this paper solve?
- Why does it matter? What's the motivation?
- What was the state of the art before this paper?

### System Model
- **Network model**: synchronous, asynchronous, partially synchronous? What are the timing assumptions? (known bound Δ, unknown bound, eventual synchrony after GST)
- **Adversary model**: static or adaptive corruption? Rush or non-rush? Computational bound (PPT)?
- **Trust assumptions**: corruption threshold (t < n/3, t < n/2, etc.)? Honest majority assumption? Trusted setup?
- **Communication model**: point-to-point, broadcast, authenticated channels? PKI assumed?
- **Cryptographic assumptions**: what hardness assumptions are made? (CDH, DDH, LWE, random oracle, CRS)

### Construction Overview
- High-level protocol description (what messages are sent, in what order)
- Number of phases/rounds
- Key data structures
- What building blocks are used (threshold signatures, VRFs, erasure codes, etc.)

### Claimed Security Properties
- List each theorem/claim **verbatim** — do not paraphrase
- Note the exact model each claim is made under
- Distinguish between: safety (agreement, consistency), liveness (termination, progress), fairness, privacy

### Proof Technique
- Game-based, simulation-based (UC/standalone), reduction, direct argument?
- What is the reduction from? (e.g., "security reduces to CDH in the random oracle model")
- Key lemmas and their role in the overall proof
- Where does the proof use the corruption threshold? The network model?

### Complexity Claims
- Communication complexity (per-round, total, amortized)
- Round complexity (best case, worst case, expected)
- Computation complexity
- State/storage requirements

### Limitations
- What do the authors acknowledge as limitations?
- What assumptions are required that might not hold in practice?
- What's left as future work?

### Key Definitions and Notation
- Non-standard notation used in the paper
- Formal definitions that other analysis will reference

## Section-by-Section Guide

### Introduction
- Extract: motivation, claimed contributions (usually a numbered/bulleted list), comparison to prior work
- Look for: the "gap" the paper claims to fill, the improvement over prior work (quantitative if possible)
- Watch for: vague contributions ("we analyze..."), overclaiming ("first to achieve..."), missing comparisons to obvious related work

### Preliminaries
- Extract: formal definitions, notation conventions, building blocks assumed
- Look for: non-standard definitions that differ from common ones, assumptions on building blocks
- Watch for: definitions that are subtly weaker/stronger than standard (e.g., a weaker notion of "validity")

### Construction / Protocol
- Extract: protocol steps, message formats, state transitions, pseudocode
- Look for: the key technical idea — what makes this construction work? What's the "trick"?
- Watch for: implicit assumptions (e.g., reliable broadcast used but not stated), race conditions, missing error handling

### Security Proof
- Extract: theorem statements (verbatim), proof structure, key lemmas, reduction chain
- Look for: where the corruption threshold is used, where the network model matters, the tightest step in the reduction
- Watch for: gaps between proof sketch and full proof, hand-waving at critical steps, tightness of security bounds

### Evaluation / Comparison
- Extract: concrete numbers, asymptotic bounds, experimental setup and results
- Look for: fair comparison criteria, hidden constants in O-notation, assumptions in benchmarks
- Watch for: comparisons that use different models for different protocols, missing error bars, cherry-picked metrics

## Red Flags in Security Arguments

These patterns warrant extra scrutiny:

- **"It is easy to see that..."** or **"It follows directly that..."** without proof — often hides the hardest part
- **Simulator that doesn't handle abort/early termination** — a classic gap in simulation-based proofs; the simulator must handle every possible adversary behavior
- **Reduction with large security loss** — if the reduction loses a factor of 2^n or q^k, the concrete security may be meaningless
- **"Full proof in appendix"** but the appendix is hand-wavy or missing — check that the appendix actually delivers what the main body promises
- **Synchrony/asynchrony mismatch** — proof assumes synchrony but the paper claims security under partial synchrony or asynchrony
- **Missing liveness/termination argument** — proving safety is often easier; liveness under partial synchrony is where many protocols fail
- **Circular dependencies** — definition A uses B, definition B uses A
- **Trusted setup assumed but not discussed** — CRS, PKI, or dealer assumed without acknowledging the trust implication
- **Idealized model without justification** — random oracle, algebraic group model, generic group model used without discussing instantiation
- **"Without loss of generality"** — sometimes used to skip cases that are actually different
- **Proof by picture** — a diagram is shown to "illustrate" security but no formal argument follows
- **Adaptive security claimed but only static adversary handled in proof** — corruption timing matters enormously
