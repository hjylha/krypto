
from pathlib import Path


def read_config(config_path):
    readings = dict()
    default_language = None
    with open(config_path, "r", encoding = "utf-8") as f:
        # language_tag = None
        for line in f:
            filtered_line = line.split("#")[0].strip()
            if not filtered_line:
                continue
            if "[" in filtered_line:
                language_tag = filtered_line.split("[")[1].split("]")[0]
                readings[language_tag] = dict()
                if default_language is None:
                    default_language = language_tag
                continue
            if "=" in filtered_line:
                key, value = filtered_line.split("=")
                key = key.strip()
                value = value.strip()
                if "path" in key and value:
                    value = Path(value)
                elif not value:
                    value = None
                readings[language_tag][key] = value
    return default_language, readings


def get_wordlist(wordlist_path):
    if not isinstance(wordlist_path, Path):
        wordlist_path = Path(wordlist_path)
    wordlist = []
    print(f"Wordlist path: {wordlist_path}")
    with open(wordlist_path, "r", encoding = "utf-8") as f:
        for line in f:
            word = line.split("\t")[0].strip().lower()
            if word:
                wordlist.append(word)
    return wordlist


def get_codeword_path(path_str):
    possible_codeword_path = Path(path_str)
    if possible_codeword_path.exists():
        return possible_codeword_path
    possible_codeword_path = Path(path_str + ".csv")
    if possible_codeword_path.exists():
        return possible_codeword_path


def get_codewords(codeword_path):
    if not isinstance(codeword_path, Path):
        codeword_path = Path(codeword_path)
    codewords = []
    with open(codeword_path, "r", encoding = "utf-8") as f:
        for line in f:
            nums_str = line.strip("\n").split(",")
            if not nums_str:
                continue
            nums_str.append("")
            nums = nums_str[:nums_str.index("")]
            if not nums:
                continue
            word = tuple(int(num) for num in nums)
            codewords.append(word)
    return codewords


def are_letters_in_alphabet(word, alphabet):
    if alphabet is None:
        return True
    alphabet = alphabet.lower()
    for char in word.lower():
        if char not in alphabet:
            return False
    return True


def find_correspondence(num_or_char, correspondence_tuple):
    for num, char in correspondence_tuple:
        if num_or_char == num:
            return char
        if num_or_char == char:
            return num


def nums_to_letters(tuple_of_nums, substitution):
    return "".join([find_correspondence(num, substitution) for num in tuple_of_nums])


def letters_to_nums(letters, substitution):
    return tuple(find_correspondence(char, substitution) for char in letters)


def count_in_how_many_words_numbers_are(codewords):
    counts = dict()
    try:
        for num_tuple in codewords:
            for num in set(num_tuple):
                if counts.get(num) is None:
                    counts[num] = 1
                else:
                    counts[num] += 1
    except TypeError as err:
        print(err)
    return counts


def get_substitution_tuple(codewords, words, previous_substitution_tuple=None):
    substitution_pairs = [] if previous_substitution_tuple is None else list(previous_substitution_tuple)
    for codeword, word in zip(codewords, words):
        for num, char in zip(codeword, word):
            if num in [c_r for c_r, c in substitution_pairs]:
                continue
            substitution_pairs.append((num, char))
    return tuple(sorted(substitution_pairs, key=lambda p: p[0]))


def decrypt_codeword(codeword, substitution_tuple, not_found_symbol="?"):
    chars = []
    for num in codeword:
        char = find_correspondence(num, substitution_tuple)
        char = not_found_symbol if char is None else char
        chars.append(char)
    return "".join(chars)


def decrypt_codewords(codewords, substitution_tuple, not_found_symbol="?"):
    decrypted_words = []
    for codeword in codewords:
        decrypted_words.append((codeword, decrypt_codeword(codeword, substitution_tuple, not_found_symbol)))
    return tuple(decrypted_words)


def does_word_match(word, codeword):
    if len(word) != len(codeword):
        return False
    for i, chars in enumerate(zip(word, codeword)):
        char, char_r = chars
        for char_prev, char_r_prev in zip(word[:i], codeword[:i]):
            if char_r == char_r_prev and char != char_prev:
                return False
            if char_r == char_r_prev and char == char_prev:
                break
            if char_r != char_r_prev and char == char_prev:
                return False
    return True


def does_word_match_to_substitution_tuple(word, codeword, substitution_tuple):
    letters_in_tuple = [char for _, char in substitution_tuple]
    for char, num in zip(word, codeword):
        expected_char = find_correspondence(num, substitution_tuple)
        if expected_char is None and char in letters_in_tuple:
            return False
        if expected_char is not None and expected_char != char:
            return False
    return True


def get_matching_words(codeword, wordlist, maximum_matched_words=None):
    matched_words = []
    if maximum_matched_words is not None:
        for word in wordlist:
            if does_word_match(word, codeword):
                matched_words.append(word)
                if len(matched_words) > maximum_matched_words:
                    return matched_words
        return matched_words
    for word in wordlist:
        if does_word_match(word, codeword):
            matched_words.append(word)
    return matched_words


def does_word_match_to_matching_indices(word, matching_indices_dict):
    for char, indices in matching_indices_dict.items():
        for i in indices:
            if char != word[i]:
                return False
    return True

def does_word_match_to_fixed_index_values(word, matching_indices_dict):
    for i, char in matching_indices_dict.items():
        if word[i] != char:
            return False
    return True


class CodewordPuzzle:

    def get_nums_in_codewords(self):
        nums_in_codewords = []
        for codeword in self.codewords:
            for num in codeword:
                if num not in nums_in_codewords:
                    nums_in_codewords.append(num)
        return tuple(sorted(nums_in_codewords))
    
    def get_substitution_tuple(self):
        substitution_tuple = tuple([(key, value) for key, value in self.substitution_dict.items() if value is not None])
        if substitution_tuple:
            return substitution_tuple
    
    def set_matched_words(self):
        for codeword, words in self.matched_words.items():
            matching_indices = {i: self.substitution_dict[num] for i, num in enumerate(codeword) if self.substitution_dict[num] is not None}
            new_matched_words = []
            for word in words:
                if does_word_match_to_fixed_index_values(matching_indices):
                    new_matched_words.append(word)
            self.matched_words[codeword] = new_matched_words

    
    def __init__(self, codewords, wordlist, alphabet):
        self.codewords = codewords
        self.alphabet = alphabet
        self.wordlist = wordlist

        self.nums_in_codewords = self.get_nums_in_codewords()
        self.substitution_dict = {num: None for num in self.nums_in_codewords}

        self.wordlists = dict()
        for word in self.wordlist:
            num = len(word)
            if self.wordlists.get(num) is None:
                self.wordlists[num] = [word]
                continue
            self.wordlists[num].append(word)
        
        self.matched_words_all = {codeword: get_matching_words(codeword, self.wordlists[len(codeword)]) for codeword in self.codewords}
        self.matched_words = {codeword: words for codeword, words in self.matched_words_all.items() if words}

    def clear_substitution_dict(self):
        self.substitution_dict = {num: None for num in self.substitution_dict.keys()}
        self.matched_words = self.matched_words_all

    def add_to_substitution_dict(self, num, char):
        if num not in self.substitution_dict.keys():
            return False
        self.substitution_dict[num] = char
        return True

    def match_two_codewords(self, codeword1, codeword2):
        matching_indices = dict()
        for char in codeword1:
            if matching_indices.get(char) is None:
                matching_indices[char] = [i for i, c in enumerate(codeword2) if c == char]

        matching_pairs = []
        for word1 in self.matched_words[codeword1]:
            m_indices = dict()
            for i, char in enumerate(word1):
                m_indices[char] = matching_indices[codeword1[i]]
            for word2 in self.matched_words[codeword2]:
                if does_word_match_to_matching_indices(word2, m_indices):
                    matching_pairs.append((word1, word2))
        return matching_pairs
    
    def match_all_codeword_pairs(self, max_unique_pairs = 5):
        codewords_to_match = sorted(self.matched_words.keys(), key=lambda c: len(self.matched_words[c]))
        matched_pairs = dict()
        num_of_pairs = 0
        num_of_unique_pairs = 0
        for i, codeword1 in enumerate(codewords_to_match):
            for codeword2 in codewords_to_match[i + 1:]:
                matched_pairs[(codeword1, codeword2)] = self.match_two_codewords(codeword1, codeword2)
                num_of_pairs += 1
                if  num_of_pairs % 100 == 0:
                    print(f"{num_of_pairs} pairs checked")
                if len(matched_pairs[(codeword1, codeword2)]) == 1:
                    print(f"Found unique pair:")
                    print(f"{codeword1}, {codeword2}")
                    print(f"{matched_pairs[(codeword1, codeword2)]}")
                    num_of_unique_pairs += 1
                if num_of_unique_pairs >= max_unique_pairs:
                    return matched_pairs
        return matched_pairs

    def find_unique_pairs(self):
        codewords_to_match = sorted(self.matched_words.keys(), key=lambda c: len(self.matched_words[c]))
        for i, codeword1 in enumerate(codewords_to_match):
            for codeword2 in codewords_to_match[i + 1:]:
                matched_pairs = self.match_two_codewords(codeword1, codeword2)
                if len(matched_pairs) == 1:
                    yield (codeword1, codeword2), matched_pairs[0]

    def try_more_words(self, codewords, matched_codewords, substitution_tuple, minimum_matches_wanted):
        if not codewords:
            return matched_codewords, substitution_tuple
        for i, codeword in enumerate(codewords):
            for word in self.matched_words[codeword]:
                if not does_word_match_to_substitution_tuple(word, codeword, substitution_tuple):
                    continue
                new_matched_codewords = tuple([*matched_codewords, codeword])
                words = tuple([word for _, word in decrypt_codewords(matched_codewords, substitution_tuple)])
                new_substitution_tuple = get_substitution_tuple(new_matched_codewords, [*words, word])
                new_matched_codewords, new_substitution_tuple = self.try_more_words(codewords[i + 1:], new_matched_codewords, new_substitution_tuple, minimum_matches_wanted)
                if len(new_matched_codewords) >= minimum_matches_wanted:
                    return new_matched_codewords, new_substitution_tuple
        return matched_codewords, substitution_tuple

    def start_matching_words(self, minimum_matches_wanted):
        for codeword_pair, word_pair in self.find_unique_pairs():
            substitution_tuple = get_substitution_tuple(codeword_pair, word_pair)
            codewords = [codeword for codeword in self.matched_words.keys() if codeword not in codeword_pair]
            codewords = sorted(codewords, key=lambda c: len(self.matched_words[c]))
            matched_codewords, substitution_tuple = self.try_more_words(codewords, codeword_pair, substitution_tuple, minimum_matches_wanted)
            if len(matched_codewords) >= minimum_matches_wanted:
                return matched_codewords, substitution_tuple
    
    def try_to_match_more_words(self, codewords, start_index, matched_codewords, substitution_tuple, minimum_matches_wanted):
        if start_index < 1:
            return matched_codewords, substitution_tuple
        # print(f"Index {start_index}")
        for i in range(start_index, -1, -1):
            current_codeword = codewords[i]
            if self.matched_words.get(current_codeword) is None:
                continue
            for word in self.matched_words[current_codeword]:
                if matched_codewords is None:
                    substitution_tuple = get_substitution_tuple([current_codeword], [word])
                    new_matched_codewords, new_substitution_tuple = self.try_to_match_more_words(codewords, i - 1, tuple([current_codeword]), substitution_tuple, minimum_matches_wanted)
                    if len(new_matched_codewords) >= minimum_matches_wanted:
                        return new_matched_codewords, new_substitution_tuple
                    continue
                if not does_word_match_to_substitution_tuple(word, current_codeword, substitution_tuple):
                    continue
                new_matched_codewords = tuple([*matched_codewords, current_codeword])
                words = tuple([w for _, w in decrypt_codewords(matched_codewords, substitution_tuple)])
                new_substitution_tuple = get_substitution_tuple(new_matched_codewords, [*words, word])
                new_matched_codewords, new_substitution_tuple = self.try_to_match_more_words(codewords, i - 1, new_matched_codewords, new_substitution_tuple, minimum_matches_wanted)
                if len(new_matched_codewords) >= minimum_matches_wanted:
                    return new_matched_codewords, new_substitution_tuple
        return matched_codewords, substitution_tuple
    
    def try_to_match_words_to_numbers(self, minimum_matches_wanted, minimum_letter_matches_wanted, num_of_iterations):
        # codewords = sorted(self.matched_words.keys(), key=lambda t: len(self.matched_words[t]), reverse=True)
        codewords = sorted(self.matched_words.keys(), key=lambda t: len(t))
        print(f"{len(codewords)} codewords with possible matches")
        matched_codewords0, substitution_tuple0 = self.try_to_match_more_words(codewords, len(codewords) - 1, None, None, minimum_matches_wanted)

        matched_codewords = matched_codewords0
        substitution_tuple = substitution_tuple0
        not_done = num_of_iterations

        print(f"Initially found {len(matched_codewords0)} words.")

        while not_done:
            counts = count_in_how_many_words_numbers_are(matched_codewords)
            substitution_tuple = tuple(pair for pair in substitution_tuple if counts[pair[0]] >= minimum_letter_matches_wanted)

            filtered_wordlists = dict()
            matched_codewords = []
            matched_words = []

            for codeword, words in self.matched_words.items():
                filtered_words = [word for word in words if does_word_match_to_substitution_tuple(word, codeword, substitution_tuple)]
                if filtered_words:
                    filtered_wordlists[codeword] = filtered_words
                    if len(filtered_words) == 1:
                        matched_codewords.append(codeword)
                        matched_words.append(filtered_words[0])
            decoding_tuple = get_substitution_tuple(matched_codewords, matched_words)
            if all([len(words) == 1 for words in filtered_wordlists.values()]):
                return matched_codewords, decoding_tuple
            not_done -= 1
        counts = count_in_how_many_words_numbers_are(matched_codewords)
        # decoding_tuple = tuple(pair for pair in decoding_tuple if counts[pair[0]] >= min_letter_matches_wanted)
        for num, char in substitution_tuple:
            self.substitution_dict[num] = char
        return matched_codewords, substitution_tuple


def yes_or_no_question(question_text):
    help_text = 'Please answer Y or N for yes or no.'
    while True:
        answer = input(f'{question_text} (Y/N) ')
        if answer.lower() == 'y':
            return 'y'
        if answer.lower() == 'n':
            return 'n'
        print(help_text)


class Krypto:
    DEFAULT_CONFIG_PATH = "krypto.conf"
    NAME_KEY = "name"
    ALPHABET_KEY = "alphabet"
    WORDLIST_PATH_KEY = "wordlist_path"

    def __init__(self, config_path=DEFAULT_CONFIG_PATH, language=None, puzzle=None, codeword_path=None):
        default_language, config = read_config(config_path)
        self.config = config
        if language is None:
            language = default_language
        self.language = language
        self.puzzle = puzzle

    def choose_language(self):
        choose_prompt_en = "Choose language (available:"
        choose_prompt_fi = "Valitse kieli (vaihtoehdot:"
        while True:
            language_answer = input(f"{choose_prompt_en} {", ".join(self.config.keys())}): ")
            if language_answer.lower() in self.config.keys():
                self.language = language_answer
                return
            if not language_answer and self.language:
                return
            not_confirmed = True
            while not_confirmed:
                add_new_language = yes_or_no_question(f"Do you want to add a new language, {language_answer}? [NOTE: This has not been implemented yet]")
                # yes_or_no = input(f"Do you want to add a new language, {language_answer}? (Y/N) ")
                if add_new_language.lower() == "y":
                    self.language = language_answer
                    return
                if add_new_language.lower() == "n":
                    # try_again = input("Do you want to try again? (Y/N) ")
                    try_again = yes_or_no_question("Do you want to try again?")
                    if try_again.lower() == "n":
                        return
                    
    def choose_codeword_path(self):
        while True:
            path_answer = input(f"Type the path to the csv file with codewords: ")
            codeword_path = get_codeword_path(path_answer)
            if codeword_path is not None:
                return codeword_path
            # codeword_path = Path(path_answer)
            # if codeword_path.exists():
            #     return codeword_path
            # codeword_path = Path(path_answer + ".csv")
            # if codeword_path.exists():
            #     return codeword_path
            try_again = yes_or_no_question(f"File {path_answer} does not exist. Do you want to try again?")
            if not try_again:
                return

    def initialize_puzzle(self, codeword_path, wordlist_path=None):
        codewords = get_codewords(codeword_path)
        # config = read_config(config_path)[language_tag.lower()]
        alphabet = self.config[self.language][self.ALPHABET_KEY]
        if wordlist_path is None:
            wordlist = get_wordlist(self.config[self.language][self.WORDLIST_PATH_KEY])
        else:
            wordlist = get_wordlist(wordlist_path)
        wordlist = [word for word in wordlist if are_letters_in_alphabet(word, alphabet)]
        self.puzzle = CodewordPuzzle(codewords, wordlist, alphabet)

    def input_data_and_initialize_puzzle(self, language=None, codeword_path=None):
        if language is None:
            self.choose_language()
        if codeword_path is None:
            codeword_path = self.choose_codeword_path()
        self.initialize_puzzle(codeword_path)

    def try_to_solve_puzzle(self, minimum_matches_wanted, minimum_letter_matches_wanted, num_of_iterations):
        solved_codewords, substitution_tuple = self.puzzle.try_to_match_words_to_numbers(minimum_matches_wanted, minimum_letter_matches_wanted, num_of_iterations)
        print(f"{len(solved_codewords)} out of {len(self.puzzle.codewords)} words found.")
        print(f"{len(substitution_tuple)} out of {len(self.puzzle.substitution_dict)} numbers deciphered.")
        for num, char in substitution_tuple:
            self.puzzle.substitution_dict[num] = char
        return solved_codewords, substitution_tuple

    def add_config(self):
        pass

    def modify_config(self):
        pass

    def save_wordlist(self):
        pass


if __name__ == "__main__":

    import sys
    import time

    language = "fi"
    # language = "en"
    krypto_path = "krypto51-52.csv"
    K = Krypto()
    # have_language_and_codeword_path = False
    language_selected = False
    codeword_path = None
    for item in sys.argv[1:]:
        if item in K.config.keys():
            K.language = item
            language_selected = True
            continue
        # if K.language is None:
            
        if codeword_path is None:
            codeword_path = get_codeword_path(item)
            if codeword_path is not None:
                continue
    # K.choose_language()
    # print(f"Chosen {K.language}")
    # codeword_path = K.choose_codeword_path()
    # print(f"Chosen {codeword_path}")
    if language_selected and codeword_path:
        K.initialize_puzzle(codeword_path)
    elif language_selected:
        K.input_data_and_initialize_puzzle(language=K.language)
    elif codeword_path:
        K.input_data_and_initialize_puzzle(codeword_path=codeword_path)
    else:
        K.input_data_and_initialize_puzzle()
    print(f"Language: {K.language}")
    print(f"{len(K.puzzle.codewords)} codewords")
    print(f"{len(K.puzzle.wordlist)} words")

    # start_time = time.time()
    # cw, st = K.try_to_solve_puzzle(10, 3, 5)
    # end_time = time.time()

    # print(f"\nTime elapsed: {round(end_time - start_time, 3)} seconds.\n")

    # print("Substitution table:")
    # for num, char in K.puzzle.substitution_dict.items():
    #     if char:
    #         print(f"{num}\t{char}")

    print()
    print(f"Trying to solve using pairs...")
    start_time = time.time()
    cw1, st1 = K.puzzle.start_matching_words(7)
    end_time = time.time()
    print(f"{len(cw1)} codewords solved.")
    print(f"{len(st1)} out of {len(K.puzzle.substitution_dict)} numbers deciphered.")

    print(f"Time elapsed: {round(end_time - start_time, 3)} seconds.\n")
    print("Substitution table:")
    for num, char in st1:
        if char:
            print(f"{num}\t{char}")
    # good_pairs = {cws: ps for cws, ps in m_p.items() if len(ps) == 1}
    # print(f"Found {len(good_pairs)} pairs with unique match.")



