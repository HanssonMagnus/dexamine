# Miscellaneous docs

## Lists
This repository does not include MEV contract lists.

## When You Have Queried Your Data
Dexamine delivers the data in parquet format. Parquet is becoming the standard for high
performance data storage, however one disadvantage is that you cannot view the data file
in your editor. One way to inspect the data from the command line is to use
`parquet-cli`, which is installed through pip and then run in the command line.

```
pip3 install parquet-cli
parq your_file.parquet --head 10
```
