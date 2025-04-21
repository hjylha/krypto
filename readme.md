
# Codeword / krypto solver

This script tries to solve a codeword puzzle by matching code words to a wordlist.

At the moment this script looks for the wordlist in the file named `nykysuomensanalista2024.csv` (in the same directory), and this file is expected to be similar to [nykysuomensanalista2024.txt](https://kaino.kotus.fi/lataa/nykysuomensanalista2024.txt) (which has extension txt now for some reason), that is, this file can be handled like a tab-separated csv-file.

To use this script, just write codewords to a (actually comma-separated) csv-file and use the name of this file as an extra argument to `python -i sanoja.py`, i.e. run command of form

```
python -i sanoja.py file_with_codewords.csv
```

In the interactive shell, run `pw(dt)` to see all the codewords.
