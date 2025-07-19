
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


class PerformanceTest:
    DEFAULT_CONFIG_PATH = "krypto.conf"
    NAME_KEY = "name"
    ALPHABET_KEY = "alphabet"
    WORDLIST_PATH_KEY = "wordlist_path"
    CODEWORD_FOLDER_PATH_KEY = "codeword_folder_path"

    def __init__(self, language_tag, codewords_path):
        self.language = language_tag
        self.default_language, self.config = krypto.read_config(self.DEFAULT_CONFIG_PATH)
        self.alphabet = self.config[self.language][self.ALPHABET_KEY]
        self.wordlist_path = self.config[self.language][self.WORDLIST_PATH_KEY]
        self.codeword_path = codewords_path


    def time_get_wordlist(self):
        start_time = perf_counter_ns()
        self.wordlist = krypto.get_wordlist(self.wordlist_path)

        end_time = perf_counter_ns()

        description = f"get_wordlist (from '{self.wordlist_path}')"
        # print(f"{len(self.wordlist)} words")
        return show_time(description, start_time, end_time, "milli")
    
    def time_get_codewords(self):
        start_time = perf_counter_ns()
        comments, codewords = krypto.get_codewords(self.codeword_path)

        self.codewords = codewords
        self.comments = comments

        end_time = perf_counter_ns()

        description = f"get_codewords (from '{self.codeword_path}')"
        # print(f"{len(self.codewords)} codewords")
        return show_time(description, start_time, end_time, "micro")

    def time_set_matched_words(self, codewords, wordlist, extra_description=""):
        start_time = perf_counter_ns()
        self.matched_words = dict()
        for codeword in codewords:
            words = krypto.get_matching_words(codeword, wordlist)
            self.matched_words[codeword] = words

        end_time = perf_counter_ns()
        description = f"set_matched_words ({extra_description})"
        return show_time(description, start_time, end_time)


    def time_find_all_unique_pairs(self, codewordpuzzle, extra_description=""):
        start_time = perf_counter_ns()
        self.unique_pairs = codewordpuzzle.find_all_unique_pairs()

        end_time = perf_counter_ns()
        description = f"find_all_unique_pairs ({extra_description})"
        return show_time(description, start_time, end_time)

    def run_all_performance_tests(self):

        print(f"\n Language: {self.language} \n Wordlist path: {self.wordlist_path} \n Codewords path: {self.codeword_path}")

        t1 = self.time_get_wordlist()

        t2 = self.time_get_codewords()

        t3 = self.time_set_matched_words(self.codewords, self.wordlist)

        self.codewordpuzzle = krypto.CodewordPuzzle(self.codewords, self.wordlist, self.alphabet, self.comments)

        t4 = self.time_find_all_unique_pairs(self.codewordpuzzle)

        total_time = t1 + t2 + t3 + t4
        print(f"{round(total_time / 1_000_000_000, 3)} seconds overall\n")


if __name__ == "__main__":
    do_fi = True
    do_en = True
    if "fi" in sys.argv and "en" not in sys.argv:
        do_en = False
    elif "fi" not in sys.argv and "en" in sys.argv:
        do_fi = False

    if do_fi:
        language_tag = "fi"
        codeword_path = "k24-51-52.csv"
        pt_fi = PerformanceTest(language_tag, codeword_path)
        pt_fi.run_all_performance_tests()

        codeword_path = "k25-16-17.csv"
        pt_fi = PerformanceTest(language_tag, codeword_path)
        pt_fi.run_all_performance_tests()

    if do_en:
        language_tag = "en"
        codeword_path = "cw25-05-12.csv"
        pt_en = PerformanceTest(language_tag, codeword_path)
        pt_en.run_all_performance_tests()

        codeword_path = "cw25-05-22.csv"
        pt_en = PerformanceTest(language_tag, codeword_path)
        pt_en.run_all_performance_tests()

        codeword_path = "cw25-05-23.csv"
        pt_en = PerformanceTest(language_tag, codeword_path)
        pt_en.run_all_performance_tests()
