
import sys
from time import perf_counter_ns

import krypto


def show_time(description, start_time, end_time, unit=""):
    elapsed_time = end_time - start_time
    if unit == "micro":
        print(f"{description}  {round(elapsed_time / 1000, 3)} microseconds")
        return elapsed_time
    if unit == "milli":
        print(f"{description}  {round(elapsed_time / 1_000_000, 3)} milliseconds")
        return elapsed_time
    print(f"{description}  {round(elapsed_time / 1_000_000_000, 3)} seconds")
    return elapsed_time


def time_get_wordlist(wordlist_path):
    start_time = perf_counter_ns()
    wordlist = krypto.get_wordlist(wordlist_path)

    end_time = perf_counter_ns()

    description = f"get_wordlist (from '{wordlist_path}')"
    return show_time(description, start_time, end_time, "milli")


def time_get_codewords(codeword_path):
    start_time = perf_counter_ns()
    codewords = krypto.get_codewords(codeword_path)

    end_time = perf_counter_ns()

    description = f"get_codewords (from '{codeword_path}')"
    return show_time(description, start_time, end_time, "micro")

def time_set_matched_words(codewords, wordlist, extra_description=""):
    start_time = perf_counter_ns()
    matched_words = dict()
    for codeword in codewords:
        words = krypto.get_matching_words(codeword, wordlist)
        matched_words[codeword] = words

    end_time = perf_counter_ns()
    description = f"set_matched_words ({extra_description})"
    return show_time(description, start_time, end_time)


def time_find_all_unique_pairs(codewordpuzzle, extra_description=""):
    start_time = perf_counter_ns()
    unique_pairs = codewordpuzzle.find_all_unique_pairs()

    end_time = perf_counter_ns()
    description = f"find_all_unique_pairs ({extra_description})"
    return show_time(description, start_time, end_time)



if __name__ == "__main__":
    ALPHABET = "abcdefghijklmnopqrstuvwxyzåäö"
    wordlist_path = "wordlist_fi.txt"
    t1 = time_get_wordlist(wordlist_path)

    codeword_path = "k24-51-52.csv"
    t2 = time_get_codewords(codeword_path)

    wordlist = krypto.get_wordlist(wordlist_path)
    comments, codewords = krypto.get_codewords(codeword_path)
    paths = f"{codeword_path}; {wordlist_path}"
    t3 = time_set_matched_words(codewords, wordlist, paths)

    puzzle = krypto.CodewordPuzzle(codewords, wordlist, ALPHABET, comments)
    t4 = time_find_all_unique_pairs(puzzle, paths)
