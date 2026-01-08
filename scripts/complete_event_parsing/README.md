# Update Trueblocks Index
Before running Dexamine, it is a good idea to update the Trueblocks index, such that
we get the latest data. This can be done by first removing the old monitor files and
then downloading the index,

```bash
rm -rf /media/m2_4tb/trueblocks/cache/mainnet/monitors/*
chifra init --all
```

The reason this is not included in the `main.sh` script that runs both Trueblocks and
dexamine is because we potentially do not want to remove the monitors each time we run
the script.

## Run several `dexamine` parsing queries
```bash
./run_several.sh
```
