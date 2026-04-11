# Test Papers for Reaper Evaluation

Place PDF files here for end-to-end pipeline testing. See `evals/evals.json` for test case definitions.

## Required Test Papers

### 1. `proof-gap-paper.pdf` — Cryptographic construction with a known proof gap

Find a paper with a known proof gap (e.g., missing abort handling in a simulator, security reduction with an error). Good sources:
- IACR ePrint papers with published errata or follow-up correction papers
- Papers where a later work explicitly identifies and fixes a proof gap

### 2. `consensus-paper.pdf` — Consensus protocol (e.g., HotStuff variant)

A BFT consensus paper that makes performance and security claims against competitors. Candidates:
- HotStuff (Yin et al., PODC 2019)
- Jolteon/Ditto (Gelashvili et al.)
- BullShark (Spiegelman et al.)
- Narwhal/Tusk (Danezis et al.)

### 3. `blockchain-paper.pdf` — Blockchain paper with questionable security claims

A blockchain paper with strong security claims but limited or informal proofs. Look for:
- Papers from non-top-tier venues claiming novel security properties
- Papers where the threat model is vaguely stated
- Papers that claim asynchronous security but only prove under synchrony
