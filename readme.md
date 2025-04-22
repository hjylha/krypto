
# Codeword / krypto solver

This script tries to solve a codeword puzzle by matching code words to a wordlist.

The script requires a file with a list of words. To take advantage of such a file the script checks the file `config`, which contains three sections: the default language, the different "alphabets" for languages (to filter out words with characters not in the "alphabet") and paths to wordlists for languages. Make sure that the wordlist file is correct in `config`.

Currently, the default `config` has entries for Finnish and English pointing to downloaded versions of wordlists [nykysuomensanalista2024.txt](https://kaino.kotus.fi/lataa/nykysuomensanalista2024.txt) and `words_alpha.txt` from [List of English words](https://github.com/dwyl/english-words), respectively.

<!-- At the moment this script looks for the wordlist in the file named `nykysuomensanalista2024.txt` (in the same directory), and this file is expected to be similar to [nykysuomensanalista2024.txt](https://kaino.kotus.fi/lataa/nykysuomensanalista2024.txt), that is, this file can be handled like a tab-separated csv-file.

As for English words, this has been tested by using the file `words_alpha.txt` from [List of English words](https://github.com/dwyl/english-words). -->

To use this script, just write codewords to a (actually comma-separated) csv-file and use the name of this file (as well as language tag, if not the default language in `config`) as an extra argument to `python sanoja.py`, i.e. run command of form

```
python sanoja.py file_with_codewords.csv en
```

Since it can happen that not all words in the codeword puzzle are in the wordlist used, it can be useful to run the script with the interactive shell:
```
python -i sanoja.py file_with_codewords.csv en
```
