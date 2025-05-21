
import os
import sys
import time
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
    comments = []
    codewords = []
    with open(codeword_path, "r", encoding = "utf-8") as f:
        for line in f:
            if "#" in line:
                comment = line.strip().split("#")[1].strip()
                comments.append(comment)
                continue
            nums_str = line.strip().split(",")
            if not nums_str:
                continue
            nums_str.append("")
            nums = nums_str[:nums_str.index("")]
            if not nums:
                continue
            word = tuple(int(num) for num in nums)
            codewords.append(word)
    return comments, codewords


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


def add_whitespace(word, total_length):
    shortened_word = word[:total_length]
    final_word = f"{shortened_word}{' ' * (total_length - len(shortened_word))}"
    return final_word


def codeword_as_str(codeword):
    return ",".join([str(num) for num in codeword])


class CodewordPuzzle:

    def get_nums_in_codewords(self):
        nums_in_codewords = []
        for codeword in self.codewords:
            for num in codeword:
                if num not in nums_in_codewords:
                    nums_in_codewords.append(num)
        return tuple(sorted(nums_in_codewords))
    
    def get_substitution_tuple(self):
        substitution_tuple = tuple([(key, value) for key, value in self.substitution_dict.items() if value])
        if substitution_tuple:
            return substitution_tuple
    
    def set_matched_words(self):
        for codeword, words in self.matched_words_all.items():
            matching_indices = {i: self.substitution_dict[num] for i, num in enumerate(codeword) if self.substitution_dict[num]}
            new_matched_words = []
            for word in words:
                if does_word_match_to_fixed_index_values(word, matching_indices):
                    new_matched_words.append(word)
            self.matched_words[codeword] = new_matched_words

    
    def __init__(self, codewords, wordlist, alphabet, comments):
        self.codewords = codewords
        self.alphabet = alphabet
        self.wordlist = wordlist
        self.comments = comments

        self.nums_in_codewords = self.get_nums_in_codewords()
        self.substitution_dict = {num: "" for num in self.nums_in_codewords}

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
        self.substitution_dict = {num: "" for num in self.substitution_dict.keys()}
        self.matched_words = self.matched_words_all

    def add_to_substitution_dict(self, num, char, issues=None, override=False):
        if num not in self.substitution_dict.keys():
            if issues:
                return issues["invalid number"]
            return True
        if char == "":
            self.substitution_dict[num] = char
            self.set_matched_words()
            return False
        if char.lower() not in [c.lower() for c in self.alphabet]:
            if issues:
                return issues["invalid letter"]
            return True
        # is this needed?
        if char in self.substitution_dict.values():
            if override:
                previous_num = self.find_char_from_substitution_dict(char)
                self.substitution_dict[previous_num] = ""
                self.substitution_dict[num] = char
            if issues:
                return issues["double letter"]
            return True
        self.substitution_dict[num] = char
        self.set_matched_words()
        return False
    
    def find_char_from_substitution_dict(self, char):
        for num, value in self.substitution_dict.items():
            if value.lower() == char.lower():
                return num
    
    def find_codeword(self, codeword_str):
        try:
            codeword_index = int(codeword_str) - 1
            return self.codewords[codeword_index]
        except ValueError:
            codeword = tuple([int(item.strip()) for item in codeword_str.split(",")])
            if codeword in self.codewords:
                return codeword
            codeword = tuple([int(item.strip()) for item in codeword_str.split(" ")])
            if codeword in self.codewords:
                return codeword
    
    def get_decrypted_codeword(self, codeword, not_found_symbol="?"):
        chars = []
        for num in codeword:
            char = self.substitution_dict[num]
            if char:
                chars.append(char)
                continue
            chars.append(not_found_symbol)
        return "".join(chars)            

    def match_two_codewords(self, codeword1, codeword2, maximum_matches):
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
                    if len(matching_pairs) > maximum_matches:
                        return []
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
    
    def find_all_unique_pairs(self):
        unique_pairs = []
        codewords_to_match = sorted(self.matched_words.keys(), key=lambda c: len(self.matched_words[c]))
        for i, codeword1 in enumerate(codewords_to_match):
            for codeword2 in codewords_to_match[i + 1:]:
                matched_pairs = self.match_two_codewords(codeword1, codeword2, 1)
                if matched_pairs:
                    unique_pairs.append(((codeword1, codeword2), matched_pairs[0]))
        return unique_pairs

    def find_pairs(self):
        codewords_to_match = sorted(self.matched_words.keys(), key=lambda c: len(self.matched_words[c]))
        maximum_num_of_pairs = 1
        pairs_left = set()
        for i, codeword1 in enumerate(codewords_to_match):
            for codeword2 in codewords_to_match[i + 1:]:
                matched_pairs = self.match_two_codewords(codeword1, codeword2, maximum_num_of_pairs)
                if len(matched_pairs) == maximum_num_of_pairs:
                    yield (codeword1, codeword2), matched_pairs[0]
                else:
                    pairs_left.add((codeword1, codeword2))
        # i guess make sure this still does somethisg even if no unique pairs were found
        maximum_num_of_pairs += 1
        while pairs_left:
            pairs_still_left = set()
            for codeword1, codeword2 in pairs_left:
                matched_pairs = self.match_two_codewords(codeword1, codeword2, maximum_num_of_pairs)
                if len(matched_pairs) == maximum_num_of_pairs:
                    
                    for pair in matched_pairs:
                        yield (codeword1, codeword2), pair
                else:
                    pairs_still_left.add((codeword1, codeword2))
            pairs_left = pairs_still_left
            maximum_num_of_pairs += 1
            
                
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
        for codeword_pair, word_pair in self.find_pairs():
            print("Trying with pair:")
            print(codeword_pair, word_pair)
            substitution_tuple = get_substitution_tuple(codeword_pair, word_pair)
            for num, char in substitution_tuple:
                self.add_to_substitution_dict(num, char)
            self.set_matched_words()
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


# some UI functions
def clear_screen():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac or linux
    else:
        _ = os.system('clear')


def yes_or_no_question(question_text, yes_no_tuple=("y", "n")):
    y_dash_n = f"({yes_no_tuple[0].upper()}/{yes_no_tuple[1].upper()})"
    help_text = 'Please answer Y or N for yes or no.'
    while True:
        answer = input(f'{question_text} {y_dash_n} ')
        if answer.lower() == yes_no_tuple[0]:
            return True
        if answer.lower() == yes_no_tuple[1]:
            return False
        print(help_text)


class Krypto:
    DEFAULT_CONFIG_PATH = "krypto.conf"
    NAME_KEY = "name"
    ALPHABET_KEY = "alphabet"
    WORDLIST_PATH_KEY = "wordlist_path"

    def __init__(self, config_path=DEFAULT_CONFIG_PATH, language=None, wordlist_path=None, codeword_path=None, puzzle=None):
        default_language, config = read_config(config_path)
        self.config = config
        if language is None:
            language = default_language
        self.language = language
        if wordlist_path is None:
            wordlist_path = self.config[self.language][self.WORDLIST_PATH_KEY]
        self.wordlist_path = wordlist_path
        self.codeword_path = codeword_path
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
                if add_new_language:
                    self.language = language_answer
                    return
                if not add_new_language:
                    # try_again = input("Do you want to try again? (Y/N) ")
                    try_again = yes_or_no_question("Do you want to try again?")
                    if not try_again:
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
            
    def get_command_line_arguments(self):
        language = None
        codeword_path = None
        for arg in sys.argv[1:]:
            if arg in self.config.keys():
                language = arg
                continue
            if possible_codeword_path := get_codeword_path(arg):
                codeword_path = possible_codeword_path
                continue
        return language, codeword_path


    def initialize_puzzle(self, codeword_path, wordlist_path=None):
        comments, codewords = get_codewords(codeword_path)
        # config = read_config(config_path)[language_tag.lower()]
        alphabet = self.config[self.language][self.ALPHABET_KEY]
        if wordlist_path is None:
            wordlist = get_wordlist(self.config[self.language][self.WORDLIST_PATH_KEY])
        else:
            wordlist = get_wordlist(wordlist_path)
        wordlist = [word for word in wordlist if are_letters_in_alphabet(word, alphabet)]
        self.puzzle = CodewordPuzzle(codewords, wordlist, alphabet, comments)

    def input_data_and_initialize_puzzle(self, language=None, codeword_path=None):
        if language is None:
            self.choose_language()
        if codeword_path is None:
            codeword_path = self.choose_codeword_path()
        if not codeword_path:
            return
        self.initialize_puzzle(codeword_path)
    
    def add_to_substitution_dict(self):
        issues = {
            "invalid number": 1,
            "invalid letter": 2,
            "double letter": 3 
        }
        num_input = input("Number (or numbers separated by commas): ")
        char = input("Letter (or letters separated by commas): ")
        try:
            num = int(num_input)
            nums = [num]
            chars = [char]
        except ValueError:
            nums = [int(num.strip()) for num in num_input.split(",")]
            chars = [c.strip() for c in char.split(",")]
        for num, char in zip(nums, chars):
            issue = self.puzzle.add_to_substitution_dict(num, char, issues)
            if not issues:
                continue
            if issue == 1:
                print(f"{num} is not a valid number")
                continue
            if issue == 2:
                print(f"{char} not in alphabet ({self.puzzle.alphabet})")
                continue
            if issue == 3:
                num_already = self.puzzle.find_char_from_substitution_dict(char)
                print(f"{char} already in table ({num_already})")

    def set_codeword_as_word(self):
        codeword_input = input("Codeword (index number or numbers separated by commas): ")
        try:
            codeword = self.puzzle.find_codeword(codeword_input)
        except ValueError:
            print("Cancelled")
            return
        if not codeword:
            print(f"{codeword_input} is not a valid codeword")
            return
        word = input("Word: ").lower()
        if not does_word_match(word, codeword):
            print(f"{word} and {codeword} do not match")
            return
        if word in self.puzzle.matched_words_all[codeword]:
            print(f"{word} is in wordlist")
        else:
            print(f"{word} is NOT in wordlist")
        for num, char in zip(codeword, [c for c in word]):
            self.puzzle.add_to_substitution_dict(num, char, override=True)
        self.puzzle.set_matched_words()

    def find_unique_pairs(self):
        unique_pairs = self.puzzle.find_all_unique_pairs()
        print(f"Found {len(unique_pairs)} unique pairs:")
        max_length = 0
        for codeword_pair, _ in unique_pairs:
            codeword1, codeword2 = codeword_pair
            codeword1_str = ','.join([str(num) for num in codeword1])
            codeword2_str = ','.join([str(num) for num in codeword2])
            if (new_max := max(len(codeword1_str), len(codeword2_str))) > max_length:
                max_length = new_max
        for codeword_pair, word_pair in unique_pairs:
            codeword1, codeword2 = codeword_pair
            word1, word2 = word_pair
            index1 = self.puzzle.codewords.index(codeword1) + 1
            index2 = self.puzzle.codewords.index(codeword2) + 1
            codeword1_str = ','.join([str(num) for num in codeword1])
            codeword2_str = ','.join([str(num) for num in codeword2])
            part1 = f"{add_whitespace(str(index1), 4)} {add_whitespace(codeword1_str, max_length)}"
            part2 = f"{add_whitespace(str(index2), 4)} {add_whitespace(codeword2_str, max_length)}"
            part3 = f"{add_whitespace(word1, max_length)}"
            part4 = f"{add_whitespace(word2, max_length)}"
            print(f"{part1}  {part2}    {part3}  {part4}")
        return unique_pairs

    def try_to_solve_puzzle(self, minimum_matches_wanted=None):
    # def try_to_solve_puzzle(self, minimum_matches_wanted, minimum_letter_matches_wanted, num_of_iterations):
        # solved_codewords, substitution_tuple = self.puzzle.try_to_match_words_to_numbers(minimum_matches_wanted, minimum_letter_matches_wanted, num_of_iterations)
        if minimum_matches_wanted is None:
            # TODO: what is a good default here?
            minimum_matches_wanted = len(self.puzzle.codewords) // 5
        start_time = time.time()
        solved_codewords, substitution_tuple = self.puzzle.start_matching_words(minimum_matches_wanted)
        end_time = time.time()
        print(f"Time to reach at least {minimum_matches_wanted} words: {round(end_time - start_time, 3)} seconds.")
        print(f"{len(solved_codewords)} out of {len(self.puzzle.codewords)} words found.")
        print(f"{len(substitution_tuple)} out of {len(self.puzzle.substitution_dict)} numbers deciphered.")
        for num, char in substitution_tuple:
            # self.puzzle.substitution_dict[num] = char
            self.puzzle.add_to_substitution_dict(num, char)
        return solved_codewords, substitution_tuple
    
    def print_substitution_dict(self):
        nums = sorted(self.puzzle.substitution_dict.keys())
        nums_as_str = [str(num) for num in nums]
        first_line = " | ".join(nums_as_str)
        print(first_line)
        values = []
        for num in nums:
            char = self.puzzle.substitution_dict[num].upper()
            if not char:
                char = " "
            char = add_whitespace(char, len(str(num)))
            # if char := self.puzzle.substitution_dict[num]:
            #     values.append(char.upper())
            # else:
            #     values.append(" ")
            values.append(char)
        second_line = " | ".join(values)
        print(second_line)
    
    def print_missing_chars(self):
        print("Letters yet to be included in substitution table:")
        for char in self.puzzle.alphabet:
            if char not in self.puzzle.substitution_dict.values():
                print(f"{char.upper()}", end="  ")

    def print_codeword_progress(self, codewords=None, not_found_symbol="_"):
        if codewords is None:
            codewords = self.puzzle.codewords
        self.puzzle.set_matched_words()
        num_of_chars1 = 0
        num_of_chars2 = 0
        for codeword in codewords:
            if len(codeword) > num_of_chars1:
                num_of_chars1 = len(codeword)
            codeword_str = ','.join([str(num) for num in codeword])
            if len(codeword_str) > num_of_chars2:
                num_of_chars2 = len(codeword_str)
        for codeword in codewords:
            i = self.puzzle.codewords.index(codeword)
            word = self.puzzle.get_decrypted_codeword(codeword, not_found_symbol)
            codeword_str = ','.join([str(num) for num in codeword])
            print(f"{add_whitespace(str(i + 1), 4)} {add_whitespace(word, num_of_chars1).upper()} \t {add_whitespace(codeword_str, num_of_chars2)} \t {len(self.puzzle.matched_words[codeword])} matching words")
    
    def show_matching_words(self):
        codeword_input = input("Codeword (index number or numbers separated by commas): ")
        codeword = self.puzzle.find_codeword(codeword_input)
        if codeword is None:
            print(f"Codeword corresponding to {codeword_input} not found.")
            return
        print(f"{len(self.puzzle.matched_words[codeword])} words match {codeword}:")
        for word in self.puzzle.matched_words[codeword]:
            print(word.upper())
        

    def choose_main_choice(self):
        print()
        self.print_substitution_dict()
        print()
        choices = [
            ("Set a number-letter correspondence in the substitution table", self.add_to_substitution_dict),
            ("Set a codeword as word", self.set_codeword_as_word),
            ("Show missing letters", self.print_missing_chars),
            ("Show codeword puzzle progress", self.print_codeword_progress),
            ("Show matching words for codeword", self.show_matching_words),
            ("Find unique pairs", self.find_unique_pairs),
            ("Try to solve the codeword puzzle", self.try_to_solve_puzzle),
            ("Restart (Clear the substitution table)", self.puzzle.clear_substitution_dict),
            ("Clear screen", clear_screen),
            ("Exit", exit)
        ]
        print("Choose an action:")
        for i, choice in enumerate(choices):
            if i == len(choices) -1:
                ordinal = 0
            else:
                ordinal = i + 1
            print(f"{ordinal}\t {choice[0]}")
        print()
        choice_num = None
        while choice_num is None:
            choice_input = input()
            try:
                choice_num = int(choice_input)
                if choice_num >= 0 and choice_num < len(choices):
                    break
            except ValueError:
                if choice_input.lower() == "q":
                    exit()
        print()
        if choice_num == 0:
            ans = yes_or_no_question("Are you sure you want to quit?")
            if ans:
                exit()
        return choices[choice_num - 1][1]

    def add_config(self):
        pass

    def modify_config(self):
        pass

    def save_wordlist(self):
        pass


def main_krypto():
    start_time_first = time.time()
    krypto = Krypto()
    language, codeword_path = krypto.get_command_line_arguments()
    if language:
        krypto.language = language
    
    if language and codeword_path:
        krypto.initialize_puzzle(codeword_path)
    elif language:
        krypto.input_data_and_initialize_puzzle(language=krypto.language)
    elif codeword_path:
        krypto.input_data_and_initialize_puzzle(codeword_path=codeword_path)
    else:
        krypto.input_data_and_initialize_puzzle()
    
    end_time_startup = time.time()
    print(f"\nTime taken to startup: {round(end_time_startup - start_time_first, 3)} seconds.\n")

    print(f"Language: {krypto.config[krypto.language]["name"]}")
    print(f"{len(krypto.puzzle.codewords)} codewords")
    print(f"{len(krypto.puzzle.wordlist)} words")
    if krypto.puzzle.comments:
        print("Comments about codeword puzzle:")
        for comment in krypto.puzzle.comments:
            print(f"{comment}")
    # print()
    # krypto.print_substitution_dict()

    print()

    while True:
        print()
        action = krypto.choose_main_choice()
        action()
    return krypto


if __name__ == "__main__":
    K = main_krypto()



