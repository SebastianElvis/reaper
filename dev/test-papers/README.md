# Test Papers for Reaper Evaluation

You can stage source PDFs here. You place each evaluation input in `evals/fixtures/<skill>/<case>/inputs/`. The adjacent `spec.yaml` defines the task and expectations.
These paper suggestions are optional. They do not represent executed tests.

## Suggested Test Papers

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
- The paper makes security claims that need independent verification.
- Papers where the threat model is vaguely stated
- Papers that claim asynchronous security but only prove under synchrony
