---
title: 'dexamine: A Python Package to Examine Decentralized Exhange Data'
tags:
  - Python
  - Ethereum
  - Decentralized Finance
  - Open Science
authors:
  - name: Magnus Hansson
    orcid: 0009-0004-4318-5145
    affiliation: "1,2"
affiliations:
 - name: Stockholm Business School, Stockholm University
   index: 1
 - name: Swedish House of Finance
   index: 2
date: 26 January 2024
bibliography: paper.bib
---

# Summary

"dexamine" is a Python package designed to streamline and facilitate the parsing of
decentralized exchange (DEX) data on the Ethereum blockchain. Developed in response to
the growing complexity and volume of DEX transactions, this tool provides researchers,
developers, and analysts with a means to efficiently access, interpret, and analyze
Ethereum-based DEX data. The package leverages the fundamental principles outlined in
the Ethereum white paper [@buterin2013] and yellow paper [@wood2014], as well as
documentation and white papers for specific DEXes such as Unsiwap
[@adams2020,@adams2023].

By integrating functionalities compatible with Ethereum client implementations like
Erigon [@erigon2022], and drawing on the data indexing capabilities akin to Trueblocks
[@trueblocks2022], "dexamine" offers a comprehensive solution for DEX data parsing.

# Statement of need

The Ethereum blockchain, since its inception [@buterin2013], has evolved into a complex
ecosystem, especially with the proliferation of DeFi applications. [@wood2014] further
expains Ethereum’s capabilities through the Ethereum Yellow Paper, describing a robust
platform for smart contract deployment and execution. However, with this evolution comes
the challenge of effectively parsing and analyzing the vast and intricate data generated
by DeFi protocols. Existing solutions like [@erigon2022] provide optimized Ethereum
client implementations, while tools like [@trueblocks] offer efficient blockchain data
indexing. Nevertheless, there remains a gap in the form of a dedicated tool specifically
designed for parsing DEX data within the Ethereum ecosystem.

The "dexamine" package addresses this gap by providing a tailored solution that
simplifies the complexities involved in parsing DEX transaction data. It is not only a response to
the technical needs identified in the DeFi space but also an embodiment of the open-source ethos
that Ethereum was built upon. The tool is designed to be user-friendly,
adaptable, and efficient, making it an invaluable asset for anyone working with decentralized exchange
data.

Research project utilizing "dexamine"
Mention (if applicable) a representative set of past or ongoing research projects using the
software and recent scholarly publications enabled by it.

# "dexamine" example

A basic example of how to parse all events (swaps, mints, burns) from a Uniswap v3 transaction
receipt:

```python
# Import packages
from dexamine.parsers.uniswap_v3 import parse_uni_v3_events
from dexamine.shared import general_helpers
from dexamine.shared import constants

# Test transaction
tx_hash = "0xf16f579a54c0d5700310ca54948d315b65b3f7d224a4af621ebfbaf29fcae8d5"

# Get logs from the transaction
receipt_data = general_helpers.get_receipt_data_by_hash(tx_hash)
logs = receipt_data['logs']

# Load ABIs
erc20_abi = general_helpers.load_abi(constants.path_erc20_abi)
uniswap_v3_pair_abi = general_helpers.load_abi(constants.path_uniswap_v3_pair_abi)

# Parse all events from Uniswap v3 transaction
events = parse_uni_v3_events.parse_all_v3_events(logs, erc20_abi, uniswap_v3_pair_abi)
```

# Acknowledgements

The research leading to these results has received funding from the European Union's HORIZON 2020
Programme under grant agreement no. 101102016 (RECeSS, HORIZON MSCA Postdoctoral Fellowships -
European Fellowships, C.R.).

# References
