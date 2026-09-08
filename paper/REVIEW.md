# JOSS submission readiness review

Reviewed on 8 September 2026. This is an AI-assisted author preparation review by
OpenAI Codex (GPT-6), not an independent JOSS referee report or editorial decision.
The scope was the manuscript, supporting documentation, relevant implementation,
repository metadata, and existing offline tests. It was not a full software audit.

## Findings requiring author action

1. **Repository access and public history.** GitHub reports `isPrivate: true` for
   `HanssonMagnus/dexamine`. The local history begins on 25 November 2023 and contains
   subsequent development, but private commits do not establish public development.
   Establish public access and evidence of more than six months of public development
   before submission. Repository visibility was not changed by this revision.
2. **AI disclosure is incomplete.** The manuscript discloses this revision. The author
   must supply earlier tools/models, scope of use in code, documentation and writing,
   and verification practices. The required assertion of human review and ownership of
   core design decisions must follow actual author review; it cannot be supplied by
   the editing assistant. Replace the final provisional sentence before submission.
3. **Funding and conflicts.** Confirm financial support, sponsor involvement, and any
   relevant conflicts. None have been inferred from affiliations or acknowledgements.
4. **Research-use evidence.** The claim that the package constructed datasets for
   Hansson (2024) is retained from the original manuscript. The SSRN record confirms
   the paper and research topic, but its abstract does not establish use of this
   package. Identify the software version or predecessor used and provide a methods
   reference or replication materials demonstrating that connection. Do not imply
   that version 1.0.0, dated 2026, was used in 2024. External adoption is not claimed.
5. **Final software archive.** Create the reviewed release and obtain an archival DOI
   during the final JOSS review steps, then include the archive reference. The GitHub
   repository link in this draft is not a substitute for that archive.

The public-access finding prevents submission now. The disclosures and research-use
provenance also require author input before this can be described as publication-ready.

## Manuscript revisions and evidence

| Area | Finding and correction |
| --- | --- |
| Audience and tone | Summary defines the setting before describing the package. Promotional language and unsupported generalizations were removed. |
| Required structure | Summary, statement of need, state of the field, software design, research impact, AI disclosure, acknowledgements and references are present. |
| Length | `pandoc paper/paper.md -t plain \| wc -w` reports 1,133 words, including headings and citation markers but excluding metadata and rendered bibliography. This is within the current 750–1,750-word guidance. The compiled draft has four pages including references. The guidance gives no fixed page maximum. |
| Related work | Comparisons acknowledge web3.py event decoding, cryo signature-based decoding, and self-hosted Graph Node. The justification concerns a shared Uniswap research schema rather than claiming that alternatives cannot decode or reproduce data. |
| Design | Describes separation of retrieval, metadata, parsing and output, with explicit tradeoffs. Removed API tutorial and illustrative routing/workflow figures from the manuscript; figure source files remain available. |
| Numerical interpretation | Corrected ambiguous “base units” terminology to decimal-scaled token units. Identifies floating-point arithmetic, transaction-level gas attribution and the meaning of virtual reserves. |
| Routing | Describes destination labels accurately; they do not reconstruct a call path or identify MEV. Checked against `parse_to_type` and the bundled address list. |
| Reproducibility | Qualifies repeatability because metadata queries use latest state. Checked the metadata resolver and contract calls. Cache memory grows with distinct contracts. |
| References | Checked related-tool documentation and research publication records. Corrected Barbon and Ranaldo to the publisher's 2026 publication year and “Centralized vs. Decentralized Exchanges” title. |
| Punctuation | No double-hyphen or dash punctuation remains in manuscript prose. YAML delimiters and BibTeX page-range syntax are retained because they are markup. |
| PDF workflow | Removed restoration of the entire paper directory from a cache. This could overwrite checked-out sources, and the key omitted bibliography changes. Every push now builds the checked-out paper. |

## Validation

- JOSS `openjournals/inara` Docker build completed successfully with the installed
  image `341ae8f00b95`; the tracked PDF was regenerated.
- Extracted text checked for resolved citations and complete sections; first and third
  pages inspected visually for title, affiliations, prose and references. Standard
  JOSS draft watermark, dummy DOI and publication metadata are template placeholders.
- Existing offline suite: **91 passed, 6 skipped** under Python 3.10. The skipped tests
  require a live endpoint, which was not supplied. One dependency deprecation warning.
- No source-code changes or new tests were needed for the manuscript revision.

## Sources consulted

- [JOSS paper format](https://joss.readthedocs.io/en/latest/paper.html)
- [JOSS submission requirements and AI policy](https://joss.readthedocs.io/en/latest/submitting.html)
- [JOSS review criteria](https://joss.readthedocs.io/en/latest/review_criteria.html)
- [web3.py documentation](https://web3py.readthedocs.io/en/stable/)
- [Ethereum ETL](https://github.com/blockchain-etl/ethereum-etl)
- [cryo, including event-signature decoding](https://github.com/paradigmxyz/cryo)
- [Graph Node](https://github.com/graphprotocol/graph-node)
- [Hansson (2024), SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4582649)
- [Barbon and Ranaldo (2026), publisher record](https://doi.org/10.1287/mnsc.2024.07703)
- [Lehar and Parlour (2025), publisher record](https://doi.org/10.1111/jofi.13405)
