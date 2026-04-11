# Venue Tiers and Author Weighting

Domain-specific reference for assessing the credibility and weight of academic sources. The tiers below are for cryptography and distributed systems. For other research domains, adapt this file with the relevant top venues and author criteria for that field.

## Venue Tiers

Weight results heavily toward top venues. A peer-reviewed top-conference paper is far more trustworthy than an unreviewed preprint.

| Tier | Venues | Weight |
|------|--------|--------|
| **Tier 1 (flagship)** | CRYPTO, EUROCRYPT, ASIACRYPT, CCS, S&P (Oakland), NDSS, USENIX Security, PODC, DISC, STOC, FOCS, SODA, TCC | Strongest signal. Prefer these over all others. |
| **Tier 2 (strong)** | PKC, CT-RSA, FC, ACNS, SCN, OPODIS, SSS, Journal of Cryptology, Distributed Computing (journal), JACM, SICOMP | Strong signal. Treat nearly as tier 1. |
| **Tier 3 (preprint/other)** | IACR ePrint (unreviewed), arXiv (unreviewed), workshops, lesser conferences | Use for recency and breadth, but verify claims independently. Do not treat unreviewed results as established. |

## Author Weighting

Give additional weight to papers by:
- **Program committee members and editors** of top venues in the relevant area (they shape what gets accepted and reflect community expertise)
- **Established researchers** with a strong publication record in the specific sub-area (not just generally prolific authors)
- **Original authors** of foundational results being built upon (they understand the subtleties best)

## Conflict Resolution

When two papers make competing claims, prefer the one from the higher-tier venue by authors with more domain-specific expertise. When an ePrint preprint contradicts a published top-conference result, flag it but do not treat the preprint as authoritative without independent verification.
