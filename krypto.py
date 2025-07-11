
import os
import sys
import time
from pathlib import Path


def read_config(config_path):
    readings = dict()
    default_language = None
    with open(config_path, "r", encoding = "utf-8") as f:
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
                if "folder_path" in key and not value:
                    value = Path(__file__).parent
                elif "path" in key and value:
                    value = Path(value)
                elif not value:
                    value = None
                readings[language_tag][key] = value
    return default_language, readings


def get_language_dict(language_file_path):
    language_dict = dict()
    with open(language_file_path, "r", encoding = "utf-8") as f:
        for i, line in enumerate(f):
            if i == 0:
                languages = [item for item in line.split(";")[1:] if item]
                for language in languages:
                    language_dict[language] = dict()
                continue
            if not line.strip():
                continue
            items = line.split(";")[:len(languages) + 1]
            for language, item in zip(languages, items[1:]):
                language_dict[language][items[0]] = item
    return language_dict


def get_wordlist(wordlist_path):
    if not isinstance(wordlist_path, Path):
        wordlist_path = Path(wordlist_path)
    wordlist = []
    with open(wordlist_path, "r", encoding = "utf-8") as f:
        for line in f:
            word = line.split("\t")[0].strip().lower()
            if word:
                wordlist.append(word)
    return wordlist


def get_csv_files_in_folder(folder_path=None):
    if folder_path is None:
        folder_path = Path(__file__).parent
    return folder_path.glob("*.csv")


def get_codeword_path(path_str, folder_path=None):
    if folder_path:
        # print(f"{folder_path} exists: {folder_path.exists()}")
        possible_codeword_path = folder_path / path_str
        if possible_codeword_path.exists():
            return possible_codeword_path
        possible_codeword_path = folder_path / f"{path_str}.csv"
        if possible_codeword_path.exists():
            return possible_codeword_path
        return
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
    if correspondence_tuple is None:
        return
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
    try:
        letters_in_tuple = [char for _, char in substitution_tuple]
    except TypeError:
        letters_in_tuple = []
    for char, num in zip(word, codeword):
        expected_char = find_correspondence(num, substitution_tuple)
        if expected_char is None and char in letters_in_tuple:
            return False
        if expected_char is not None and expected_char != char:
            return False
    return True

def do_two_words_match(word1, word2, codeword1, codeword2):
    for num1, char1 in zip(codeword1, word1):
        for num2, char2 in zip(codeword2, word2):
            if num1 == num2 and char1 != char2:
                return False
            if num1 != num2 and char1 == char2:
                return False
    return True


def get_nums_and_indices_dict(codeword):
    indices = dict()
    for i, num in enumerate(codeword):
        if indices.get(num) is None:
            indices[num] = [i]
        else:
            indices[num].append(i)
    return indices


def get_matching_indices(codeword1, codeword2):
    indices1 = get_nums_and_indices_dict(codeword1)
    indices2 = get_nums_and_indices_dict(codeword2)
    matching_indices = []
    others1 = []
    for num, indices in indices1.items():
        if (index2 := indices2.get(num)) is not None:
            matching_indices.append((indices[0], index2[0]))
        else:
            others1.append(indices[0])
    others2 = []
    for num, indices in indices2.items():
        if indices1.get(num) is None:
            others2.append(indices[0])
    return tuple(matching_indices), tuple(others1), tuple(others2)


def do_words_match_to_matching_indices(word1, word2, matching_indices, indices_in_1, indices_in_2):
    for index1, index2 in matching_indices:
        if word1[index1] != word2[index2]:
            return False
    for index1 in indices_in_1:
        if word1[index1] in word2:
            return False
    for index2 in indices_in_2:
        if word2[index2] in word1:
            return False
    return True


def get_matching_words(codeword, wordlist, maximum_matched_words=None):
    if not wordlist:
        return []
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


def mass_replace(word, *replacements):
    final_word = word
    for i, text in enumerate(replacements):
        final_word = final_word.replace(f"%{i + 1}%", str(text))
    return final_word


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
        substitution_tuple = self.get_substitution_tuple()
        for codeword, words in self.matched_words_all.items():
            # matching_indices = {i: self.substitution_dict[num] for i, num in enumerate(codeword) if self.substitution_dict[num]}
            new_matched_words = []
            for word in words:
                if does_word_match_to_substitution_tuple(word, codeword, substitution_tuple):
                    new_matched_words.append(word)
                # if does_word_match_to_fixed_index_values(word, matching_indices):
                #     new_matched_words.append(word)
            self.matched_words[codeword] = new_matched_words

    def is_codeword_solved(self, codeword):
        for num in codeword:
            if not self.substitution_dict[num]:
                return False
        return True
    
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
        
        self.matched_words_all = {codeword: get_matching_words(codeword, self.wordlists.get(len(codeword))) for codeword in self.codewords}
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
    
    def find_codeword_with_least_matches(self):
        the_codeword = None
        least_matches = len(self.wordlist)
        for codeword, words in self.matched_words.items():
            if self.is_codeword_solved(codeword):
                continue
            if words and len(words) < least_matches:
                the_codeword = codeword
                least_matches = len(words)
        return the_codeword
    
    def get_decrypted_codeword(self, codeword, not_found_symbol="_"):
        chars = []
        for num in codeword:
            char = self.substitution_dict[num]
            if char:
                chars.append(char)
                continue
            chars.append(not_found_symbol)
        return "".join(chars)            

    def match_two_codewords(self, codeword1, codeword2, maximum_matches):
        # matching_indices = dict()
        # for char in codeword1:
        #     if matching_indices.get(char) is None:
        #         matching_indices[char] = [i for i, c in enumerate(codeword2) if c == char]
        matching_indices, others1, others2 = get_matching_indices(codeword1, codeword2)

        matching_pairs = []
        for word1 in self.matched_words[codeword1]:
            # extra_substitution_dict = {num: char for num, char in zip(codeword1, word1)}
            # chars_in_word1 = tuple(extra_substitution_dict.values())
            # extra_substitution_tuple = get_substitution_tuple([codeword1], [word1])
            # m_indices = dict()
            # for i, char in enumerate(word1):
            #     if m_indices.get(char) is None:
            #         m_indices[char] = [i]
            #     else:
            #         m_indices[char].append(i)
                # m_indices[char] = matching_indices[codeword1[i]]
            for word2 in self.matched_words[codeword2]:
                if do_words_match_to_matching_indices(word1, word2, matching_indices, others1, others2):
                    matching_pairs.append((word1, word2))
                    if len(matching_pairs) > maximum_matches:
                        return []
                # if does_word_match_to_substitution_tuple(word2, codeword2, extra_substitution_tuple):
                #     matching_pairs.append((word1, word2))
                #     if len(matching_pairs) > maximum_matches:
                #         return []
                # for num, char in zip(codeword2, word2):
                #     expected_char = extra_substitution_dict.get(num)
                #     if expected_char is None and char in chars_in_word1:
                #         break
                #     if expected_char is None:
                #         continue
                #     if expected_char != char:
                #         break
                # else:
                #     matching_pairs.append((word1, word2))
                #     if len(matching_pairs) > maximum_matches:
                #         return []
                # if does_word_match_to_matching_indices(word2, m_indices):
                # if do_two_words_match(word1, word2, codeword1, codeword2):
                #     matching_pairs.append((word1, word2))
                #     if len(matching_pairs) > maximum_matches:
                #         return []
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
        # print("codewords sorted")
        # checked_things = 0
        # good_things = 0
        for i, codeword1 in enumerate(codewords_to_match):
            is_codeword1_solved = self.is_codeword_solved(codeword1)
            for codeword2 in codewords_to_match[i + 1:]:
                # checked_things += 1
                is_codeword2_solved = self.is_codeword_solved(codeword2)
                if is_codeword1_solved and is_codeword2_solved:
                    continue
                matched_pairs = self.match_two_codewords(codeword1, codeword2, 1)
                if matched_pairs:
                    # good_things += 1
                    # print(f"{checked_things} pair is good number {good_things}")
                    unique_pairs.append(((codeword1, codeword2), matched_pairs[0]))
        return unique_pairs

    def find_a_unique_pair(self, sorted_codewords):
        maximum_num_of_pairs = 1
        for i, codeword1 in enumerate(sorted_codewords):
            is_solved1 = self.is_codeword_solved(codeword1)
            for codeword2 in sorted_codewords[i + 1:]:
                if is_solved1 and self.is_codeword_solved(codeword2):
                    continue
                matched_pairs = self.match_two_codewords(codeword1, codeword2, maximum_num_of_pairs)
                if len(matched_pairs) == maximum_num_of_pairs:
                    return (codeword1, codeword2), matched_pairs[0]

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
        # i guess make sure this still does something even if no unique pairs were found
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
            # TODO: is this information useful?
            # print("Trying with pair:")
            # print(codeword_pair, word_pair)
            substitution_tuple = get_substitution_tuple(codeword_pair, word_pair)
            for num, char in substitution_tuple:
                self.add_to_substitution_dict(num, char)
            self.set_matched_words()
            codewords = [codeword for codeword in self.matched_words.keys() if codeword not in codeword_pair]
            codewords = sorted(codewords, key=lambda c: len(self.matched_words[c]))
            matched_codewords, substitution_tuple = self.try_more_words(codewords, codeword_pair, substitution_tuple, minimum_matches_wanted)
            if len(matched_codewords) >= minimum_matches_wanted:
                return matched_codewords, substitution_tuple
    
    def try_to_solve_by_guessing(self):
        codewords_to_match = sorted(self.matched_words.keys(), key=lambda c: len(self.matched_words[c]))
        guesses = []
        pair_of_pairs = self.find_a_unique_pair(codewords_to_match)
        while pair_of_pairs is not None:
            guesses.append(pair_of_pairs)
            codeword_pair, word_pair = pair_of_pairs
            substitution_tuple = get_substitution_tuple(codeword_pair, word_pair)
            for num, char in substitution_tuple:
                self.add_to_substitution_dict(num, char)
            pair_of_pairs = self.find_a_unique_pair(codewords_to_match)
        return guesses
            
    def try_to_solve_using_unique_pairs(self):
        unique_pairs = self.find_all_unique_pairs()
        while unique_pairs:
            # choose the (new) codeword-word that appears the most
            number_of_appearances = dict()
            for codeword_pair, word_pair in unique_pairs:
                for codeword, word in zip(codeword_pair, word_pair):
                    if not self.is_codeword_solved(codeword):
                        if number_of_appearances.get((codeword, word)) is None:
                            number_of_appearances[(codeword, word)] = 1
                        else:
                            number_of_appearances[(codeword, word)] += 1
            best_choice = None
            max_num_of_appearances = 0
            for match, num in number_of_appearances.items():
                if num > max_num_of_appearances:
                    max_num_of_appearances = num
                    best_choice = match
            # maybe show this?
            yield best_choice

            codeword, word = best_choice
            for num, char in zip(codeword, [c for c in word]):
                self.add_to_substitution_dict(num, char, override=True)
            # self.set_matched_words()
            unique_pairs = self.find_all_unique_pairs()

    
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


def yes_or_no_question(question_text, yes_no_tuple=("y", "n"), help_text="Please answer Y or N for yes or no."):
    y_dash_n = f"({yes_no_tuple[0].upper()}/{yes_no_tuple[1].upper()})"
    while True:
        answer = input(f'{question_text} {y_dash_n} ')
        if answer.lower() == yes_no_tuple[0]:
            return True
        if answer.lower() == yes_no_tuple[1]:
            return False
        print(help_text)


class Krypto:
    DEFAULT_LANGUAGE_FILE_PATH = "language_file"
    DEFAULT_CONFIG_PATH = "krypto.conf"
    NAME_KEY = "name"
    ALPHABET_KEY = "alphabet"
    WORDLIST_PATH_KEY = "wordlist_path"
    CODEWORD_FOLDER_PATH_KEY = "codeword_folder_path"

    SOLUTION_SUCCESS_THRESHOLD = 0.75

    def __init__(self, language_file_path=DEFAULT_LANGUAGE_FILE_PATH, config_path=DEFAULT_CONFIG_PATH, language=None, wordlist_path=None, codeword_path=None, puzzle=None):
        self.language_dict = get_language_dict(language_file_path)
        default_language, config = read_config(config_path)
        self.config = config
        self.default_language = default_language
        if language is None:
            language = default_language
        self.language = language
        try:
            self.current_language_dict = self.language_dict[self.language]
        except KeyError:
            self.current_language_dict = self.language_dict[default_language]
        if wordlist_path is None:
            wordlist_path = self.config[self.language][self.WORDLIST_PATH_KEY]
        self.wordlist_path = wordlist_path
        self.codeword_path = codeword_path
        self.puzzle = puzzle
        self.max_codeword_length = 0
        self.max_word_length = 0
        self.max_num_size = 0

    def get_yes_no_tuple(self):
        return (self.current_language_dict["yes"][0], self.current_language_dict["no"][0])

    def yes_no_question(self, question_text):
        yes_no_tuple = self.get_yes_no_tuple()
        help_text = self.current_language_dict["help_text"]
        return yes_or_no_question(question_text, yes_no_tuple, help_text)

    def try_again_question(self):
        question_text = self.current_language_dict["try_again_question"]
        return self.yes_no_question(question_text)

    def set_language(self, language):
        self.language = language
        try:
            self.current_language_dict = self.language_dict[language]
        except KeyError:
            self.current_language_dict = self.language_dict[self.default_language]

    def choose_language(self):
        choose_prompt = mass_replace(self.current_language_dict["choose_language"], ", ".join(self.config.keys()))
        while True:
            language_answer = input(f"{choose_prompt} ")
            if language_answer.lower() in self.config.keys():
                # self.language = language_answer
                self.set_language(language_answer.lower())
                return
            if not language_answer and self.language:
                return
            not_confirmed = True
            while not_confirmed:
                question_text = mass_replace(self.current_language_dict["add_new_language_question"], language_answer)
                add_new_language = self.yes_no_question(question_text)
                # add_new_language = yes_or_no_question(f"Do you want to add a new language, {language_answer}? [NOTE: This has not been implemented yet]")
                if add_new_language:
                    self.set_language(language_answer)
                    return
                if not add_new_language:
                    # try_again = yes_or_no_question("Do you want to try again?")
                    try_again = self.try_again_question()
                    if not try_again:
                        return
                    
    def choose_codeword_path(self):
        while True:
            found_csv_files_text = self.current_language_dict["found_csv_files_text"]
            print(found_csv_files_text)
            for csv_path in get_csv_files_in_folder(self.config[self.language][self.CODEWORD_FOLDER_PATH_KEY]):
                print(f"\t{csv_path.name}")
            prompt_text = self.current_language_dict["codeword_path_prompt"]
            # print(prompt_text)
            path_answer = input(f"{prompt_text} ")
            # path_answer = input()
            codeword_path = get_codeword_path(path_answer, self.config[self.language][self.CODEWORD_FOLDER_PATH_KEY])
            if codeword_path is not None:
                return codeword_path
            question_text = mass_replace(self.current_language_dict["file_not_found_try_again"], path_answer)
            try_again = self.yes_no_question(question_text)
            if not try_again:
                exit()
            
    def get_command_line_arguments(self):
        language = None
        codeword_path = None
        for arg in sys.argv[1:]:
            if arg in self.config.keys():
                language = arg
                continue
            if possible_codeword_path := get_codeword_path(arg, self.config[self.language][self.CODEWORD_FOLDER_PATH_KEY]):
                codeword_path = possible_codeword_path
                continue
        return language, codeword_path


    def initialize_puzzle(self, codeword_path, wordlist_path=None):
        self.codeword_path = codeword_path
        comments, codewords = get_codewords(codeword_path)
        # config = read_config(config_path)[language_tag.lower()]
        alphabet = self.config[self.language][self.ALPHABET_KEY]
        if wordlist_path is None:
            self.wordlist_path = self.config[self.language][self.WORDLIST_PATH_KEY]
            wordlist = get_wordlist(self.wordlist_path)
        else:
            wordlist = get_wordlist(wordlist_path)
        # print(self.language, self.wordlist_path)
        wordlist = [word for word in wordlist if are_letters_in_alphabet(word, alphabet)]
        self.puzzle = CodewordPuzzle(codewords, wordlist, alphabet, comments)
        
        for codeword in self.puzzle.codewords:
            if len(codeword) > self.max_word_length:
                self.max_word_length = len(codeword)
            codeword_str = codeword_as_str(codeword)
            if len(codeword_str) > self.max_codeword_length:
                self.max_codeword_length = len(codeword_str)
        self.max_num_size = len(str(len(self.puzzle.codewords)))

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
        num_prompt = self.current_language_dict["number_prompt"]
        num_input = input(num_prompt)
        char_prompt = self.current_language_dict["letter_prompt"]
        char = input(char_prompt).strip()
        try:
            num = int(num_input)
            nums = [num]
            chars = [char]
        except ValueError:
            nums = [int(num.strip()) for num in num_input.split(",")]
            chars = [c.strip() for c in char.split(",")]
        for num, char in zip(nums, chars):
            issue = self.puzzle.add_to_substitution_dict(num, char.lower(), issues)
            if not issues:
                continue
            if issue == 1:
                text = mass_replace(self.current_language_dict["invalid_number_text"], num)
                print(text)
                # print(f"{num} is not a valid number")
                continue
            if issue == 2:
                text = mass_replace(self.current_language_dict["not_in_alphabet_text"], char, self.puzzle.alphabet)
                print(text)
                # print(f"{char} not in alphabet ({self.puzzle.alphabet})")
                continue
            if issue == 3:
                num_already = self.puzzle.find_char_from_substitution_dict(char)
                text = mass_replace(self.current_language_dict["already_in_table_text"], char, num_already)
                print(text)
                # print(f"{char} already in table ({num_already})")

    def set_codeword_as_word(self):
        codeword_prompt = self.current_language_dict["codeword_prompt"]
        # codeword_input = input("Codeword (index number or numbers separated by commas): ")
        codeword_input = input(codeword_prompt)
        try:
            codeword = self.puzzle.find_codeword(codeword_input)
        except ValueError:
            print(self.current_language_dict["cancelled"])
            # print("Cancelled")
            return
        if not codeword:
            invalid_codeword_text = mass_replace(self.current_language_dict["invalid_codeword_text"], codeword_input)
            print(invalid_codeword_text)
            # print(f"{codeword_input} is not a valid codeword")
            return
        word_prompt = self.current_language_dict["word_prompt"]
        word = input(word_prompt).lower()
        if not does_word_match(word, codeword):
            no_match_text = mass_replace(self.current_language_dict["no_match_text"], word, codeword)
            print(no_match_text)
            # print(f"{word} and {codeword} do not match")
            return
        if word in self.puzzle.matched_words_all[codeword]:
            word_in_wordlist_text = mass_replace(self.current_language_dict["word_in_wordlist_text"], word)
            print(word_in_wordlist_text)
            # print(f"{word} is in wordlist")
        else:
            word_not_in_wordlist_text = mass_replace(self.current_language_dict["word_not_in_wordlist_text"], word)
            print(word_not_in_wordlist_text)
            # print(f"{word} is NOT in wordlist")
        for num, char in zip(codeword, [c for c in word]):
            self.puzzle.add_to_substitution_dict(num, char, override=True)
        self.puzzle.set_matched_words()

    def print_pairs(self, codeword_pair, word_pair, max_codeword_length=None, max_word_length=None, solved_char="*"):
        codeword1, codeword2 = codeword_pair
        if max_codeword_length is None:
            max_codeword_length = max(len(codeword_as_str(codeword1)), len(codeword_as_str(codeword2)))
        word1, word2 = word_pair
        if max_word_length is None:
            max_word_length = max(len(word1), len(word2)) + 1
        if self.puzzle.is_codeword_solved(codeword1):
            word1 = f"{word1}{solved_char}"
        if self.puzzle.is_codeword_solved(codeword2):
            word2 = f"{word2}{solved_char}"
        index1 = self.puzzle.codewords.index(codeword1) + 1
        index2 = self.puzzle.codewords.index(codeword2) + 1
        codeword1_str = ','.join([str(num) for num in codeword1])
        codeword2_str = ','.join([str(num) for num in codeword2])
        part1 = f"{add_whitespace(str(index1), 4)} {add_whitespace(codeword1_str, max_codeword_length)}"
        part2 = f"{add_whitespace(str(index2), 4)} {add_whitespace(codeword2_str, max_codeword_length)}"
        part3 = f"{add_whitespace(word1.upper(), max_word_length)}"
        part4 = f"{add_whitespace(word2.upper(), max_word_length)}"
        print(f"{part1}   {part2}   {part3}  {part4}")

    def find_unique_pairs(self, solved_char="*"):
        start_time = time.time()
        unique_pairs = self.puzzle.find_all_unique_pairs()
        end_time = time.time()
        unique_pairs_found_text = mass_replace(self.current_language_dict["unique_pairs_found_text"], len(unique_pairs), round(end_time - start_time, 3))
        print(unique_pairs_found_text)
        # solved_char = "*"
        solved_words_note = mass_replace(self.current_language_dict["solved_words_note"], solved_char)
        print(solved_words_note)
        # print(f"Found {len(unique_pairs)} unique pairs:")
        max_codeword_length = 0
        max_word_length = 0
        for codeword_pair, _ in unique_pairs:
            codeword1, codeword2 = codeword_pair
            if (new_max := max(len(codeword1), len(codeword2))) > max_word_length:
                max_word_length = new_max + 1
            codeword1_str = codeword_as_str(codeword1)
            codeword2_str = codeword_as_str(codeword2)
            if (new_max := max(len(codeword1_str), len(codeword2_str))) > max_codeword_length:
                max_codeword_length = new_max
        for codeword_pair, word_pair in unique_pairs:
            self.print_pairs(codeword_pair, word_pair, max_codeword_length, max_word_length, solved_char)
        return unique_pairs
    
    def print_solving_stats(self, elapsed_time):
        print()
        solving_time_text = mass_replace(self.current_language_dict["solving_time_with_steps_text"], round(elapsed_time, 3))
        print(solving_time_text)
        
        num_of_solved_codewords = 0
        num_of_found_words = 0
        for codeword in self.puzzle.codewords:
            if self.puzzle.is_codeword_solved(codeword):
                num_of_solved_codewords += 1
            word = self.puzzle.get_decrypted_codeword(codeword)
            if word in self.puzzle.matched_words_all[codeword]:
                num_of_found_words += 1
        found_codewords_text = mass_replace(self.current_language_dict["found_codewords_text"], num_of_solved_codewords, len(self.puzzle.codewords))
        print(found_codewords_text)
        found_codewords_in_wordlist_text = mass_replace(self.current_language_dict["found_codewords_in_wordlist_text"], num_of_found_words)
        print(found_codewords_in_wordlist_text)

        num_of_solved_numbers = len([value for value in self.puzzle.substitution_dict.values() if value])
        substitution_table_decipher_text = mass_replace(self.current_language_dict["substitution_table_decipher_text"], num_of_solved_numbers, len(self.puzzle.substitution_dict))
        print(substitution_table_decipher_text)

    def try_to_solve_puzzle(self, minimum_matches_wanted=None):
    # def try_to_solve_puzzle(self, minimum_matches_wanted, minimum_letter_matches_wanted, num_of_iterations):
        # solved_codewords, substitution_tuple = self.puzzle.try_to_match_words_to_numbers(minimum_matches_wanted, minimum_letter_matches_wanted, num_of_iterations)
        if minimum_matches_wanted is None:
            # TODO: what is a good default here?
            minimum_matches_wanted = len(self.puzzle.codewords) // 5
        start_time = time.time()
        solved_codewords, substitution_tuple = self.puzzle.start_matching_words(minimum_matches_wanted)
        end_time = time.time()

        solving_time_text = mass_replace(self.current_language_dict["solving_time_text"], minimum_matches_wanted, round(end_time - start_time, 3))
        print(solving_time_text)
        # print(f"Time to reach at least {minimum_matches_wanted} words: {round(end_time - start_time, 3)} seconds.")

        num_of_actually_solved_codewords = len([codeword for codeword in self.puzzle.codewords if self.puzzle.is_codeword_solved(codeword)])
        found_codewords_text = mass_replace(self.current_language_dict["found_codewords_text"], num_of_actually_solved_codewords, len(self.puzzle.codewords))
        print(found_codewords_text)
        # print(f"{len(solved_codewords)} out of {len(self.puzzle.codewords)} words found.")

        found_codewords_in_wordlist_text = mass_replace(self.current_language_dict["found_codewords_in_wordlist_text"], len(solved_codewords))
        print(found_codewords_in_wordlist_text)

        substitution_table_decipher_text = mass_replace(self.current_language_dict["substitution_table_decipher_text"], len(substitution_tuple), len(self.puzzle.substitution_dict))
        print(substitution_table_decipher_text)
        # print(f"{len(substitution_tuple)} out of {len(self.puzzle.substitution_dict)} numbers deciphered.")

        for num, char in substitution_tuple:
            # self.puzzle.substitution_dict[num] = char
            self.puzzle.add_to_substitution_dict(num, char)
        return solved_codewords, substitution_tuple
    
    def try_to_solve_puzzle_methodically(self, start_time=None):
        if start_time is None:
            start_time = time.time()
        found_words = 0
        for codeword, word in self.puzzle.try_to_solve_using_unique_pairs():
            found_words += 1
            codeword_str = codeword_as_str(codeword)
            part1 = f"{add_whitespace(str(self.puzzle.codewords.index(codeword) + 1), 4)} {add_whitespace(codeword_str, self.max_codeword_length)}"
            part2 = f"{add_whitespace(word.upper(), self.max_word_length)}"
            print(f"{add_whitespace(str(found_words), self.max_num_size)} {self.current_language_dict["best_match_text"]}{part1}  {part2}")
        end_time = time.time()
        self.print_solving_stats(end_time - start_time)

    
    def try_to_solve_puzzle_with_steps(self):
        # max_codeword_length = 0
        # max_word_length = 0
        # for codeword in self.puzzle.codewords:
        #     if len(codeword) > max_word_length:
        #         max_word_length = len(codeword)
        #     codeword_str = codeword_as_str(codeword)
        #     if len(codeword_str) > max_codeword_length:
        #         max_codeword_length = len(codeword_str)
        
        # only using best pairs
        # start_time = time.time()
        # found_words = 0
        # max_num_size = len(str(len(self.puzzle.codewords)))
        # for codeword, word in self.puzzle.try_to_solve_using_unique_pairs():
        #     found_words += 1
        #     codeword_str = codeword_as_str(codeword)
        #     part1 = f"{add_whitespace(str(self.puzzle.codewords.index(codeword) + 1), 4)} {add_whitespace(codeword_str, max_codeword_length)}"
        #     part2 = f"{add_whitespace(word.upper(), max_word_length)}"
        #     print(f"{add_whitespace(str(found_words), max_num_size)} {self.current_language_dict["best_match_text"]}{part1}  {part2}")
        # end_time = time.time()
        # self.print_solving_stats(end_time - start_time)

        # try to guess first
        original_substitution_dict = self.puzzle.substitution_dict.copy()
        print(self.current_language_dict["guessing_text"])
        start_time = time.time()
        guesses = self.puzzle.try_to_solve_by_guessing()
        end_time = time.time()

        # stop if "successful"
        percentage_of_numbers_deciphered = len(set(self.puzzle.substitution_dict.values())) / len(self.puzzle.substitution_dict)
        if percentage_of_numbers_deciphered >= self.SOLUTION_SUCCESS_THRESHOLD:
            for codeword_pair, word_pair in guesses:
                self.print_pairs(codeword_pair, word_pair, self.max_codeword_length, self.max_word_length)
            self.print_solving_stats(end_time - start_time)
            return
        
        print(self.current_language_dict["guessing_fail_text"])
        self.puzzle.substitution_dict = original_substitution_dict.copy()
        self.puzzle.set_matched_words()
        self.try_to_solve_puzzle_methodically(start_time)

        # guess the first pair and then go on
        # original_substitution_dict = self.puzzle.substitution_dict.copy()
        # start_time = time.time()
        # max_num_size = len(str(len(self.puzzle.codewords)))
        # for codeword_pair, word_pair in self.puzzle.find_pairs():
        #     found_words = 2
        #     print(self.current_language_dict["first_guess_text"])
        #     self.print_pairs(codeword_pair, word_pair)
        #     substitution_tuple = get_substitution_tuple(codeword_pair, word_pair)
        #     for num, char in substitution_tuple:
        #         self.puzzle.add_to_substitution_dict(num, char)
        #     self.puzzle.set_matched_words()
        #     print()
        #     print(self.current_language_dict["solution_continues_text"])
        #     for codeword, word in self.puzzle.try_to_solve_using_unique_pairs():
        #         found_words += 1
        #         codeword_str = codeword_as_str(codeword)
        #         part1 = f"{add_whitespace(str(self.puzzle.codewords.index(codeword) + 1), 4)} {add_whitespace(codeword_str, max_codeword_length)}"
        #         part2 = f"{add_whitespace(word.upper(), max_word_length)}"
        #         print(f"{add_whitespace(str(found_words), max_num_size)} {self.current_language_dict["best_match_text"]}{part1}  {part2}")
        #     end_time = time.time()
        #     self.print_solving_stats(end_time - start_time)

        #     # stop if "successful"
        #     percentage_of_numbers_deciphered = len(set(self.puzzle.substitution_dict.values())) / len(self.puzzle.substitution_dict)
        #     if percentage_of_numbers_deciphered >= self.SOLUTION_SUCCESS_THRESHOLD:
        #         return

        #     print()
        #     go_on = self.yes_no_question(self.current_language_dict["guess_again_question"])
        #     if not go_on:
        #         return
        #     self.puzzle.substitution_dict = original_substitution_dict.copy()
        #     start_time = time.time()
            
            
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
            values.append(char)
        second_line = " | ".join(values)
        print(second_line)

    def print_initial_info(self):
        language_line = mass_replace(self.current_language_dict["language"], self.config[self.language]["name"])
        print(language_line)
        # print(f"Language: {self.config[self.language]["name"]}")
        codewords_line = mass_replace(self.current_language_dict["codewords_in_file"], len(self.puzzle.codewords), self.codeword_path)
        print(codewords_line)
        # print(f"{len(self.puzzle.codewords)} codewords")
        words_line = mass_replace(self.current_language_dict["words_in_file"], len(self.puzzle.wordlist), self.wordlist_path)
        print(words_line)
        # print(f"{len(self.puzzle.wordlist)} words")
        if self.puzzle.comments:
            comments_line = self.current_language_dict["comments"]
            print(comments_line)
            for comment in self.puzzle.comments:
                print(f"{comment}")
    
    def print_missing_chars(self):
        missing_chars_text = self.current_language_dict["missing_letters_text"]
        # print("Letters yet to be included in substitution table:")
        print(missing_chars_text)
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
            part1 = add_whitespace(str(i + 1), 4)
            part2 = add_whitespace(word, num_of_chars1).upper()
            part3 = add_whitespace(codeword_str, num_of_chars2)
            part4 = mass_replace(self.current_language_dict["matching_words_text"], len(self.puzzle.matched_words[codeword]))
            print(f"{part1} {part2} \t {part3} \t {part4}")
    
    def choose_progress_to_show(self, not_found_symbol="_"):
        # default is the first, shown as 1
        default_option = 1
        options = [
            self.current_language_dict["show_unsolved_text"],
            self.current_language_dict["show_all_text"],
            self.current_language_dict["show_solved_text"]
        ]
        print(mass_replace(self.current_language_dict["choose_progress_shown_text"], default_option))
        for i, option in enumerate(options):
            ordinal = i + 1
            print(f"{add_whitespace(str(ordinal), 3)} {option}")
        try:
            choice = int(input())
        except ValueError:
            choice = default_option
        if choice == 2:
            self.print_codeword_progress(codewords=None, not_found_symbol=not_found_symbol)
            return
        if choice == 3:
            solved_codewords = [codeword for codeword in self.puzzle.codewords if self.puzzle.is_codeword_solved(codeword)]
            self.print_codeword_progress(solved_codewords, not_found_symbol=not_found_symbol)
            return
        unsolved_codewords = [codeword for codeword in self.puzzle.codewords if not self.puzzle.is_codeword_solved(codeword)]
        self.print_codeword_progress(unsolved_codewords, not_found_symbol=not_found_symbol)
    
    def show_matching_words(self):
        codeword_prompt = self.current_language_dict["codeword_prompt"]
        codeword_input = input(codeword_prompt)
        # codeword_input = input("Codeword (index number or numbers separated by commas): ")
        if codeword_input == "":
            codeword = self.puzzle.find_codeword_with_least_matches()
        else:
            codeword = self.puzzle.find_codeword(codeword_input)
        if codeword is None:
            invalid_codeword_text = mass_replace(self.current_language_dict["invalid_codeword_text"], codeword_input)
            print(invalid_codeword_text)
            # print(f"Codeword corresponding to {codeword_input} not found.")
            return
        c_index = self.puzzle.codewords.index(codeword) + 1
        words_matching_codeword_text = mass_replace(self.current_language_dict["words_matching_codeword_text"], len(self.puzzle.matched_words[codeword]), c_index, codeword)
        print(words_matching_codeword_text)
        # print(f"{len(self.puzzle.matched_words[codeword])} words match {codeword}:")
        for word in self.puzzle.matched_words[codeword]:
            print(word.upper())
        

    def choose_main_choice(self):
        print()
        self.print_substitution_dict()
        print()
        choices = [
            (self.current_language_dict["set_number_letter"], self.add_to_substitution_dict),
            (self.current_language_dict["set_codeword_word"], self.set_codeword_as_word),
            (self.current_language_dict["missing_letters"], self.print_missing_chars),
            # (self.current_language_dict["show_progress"], self.print_codeword_progress),
            (self.current_language_dict["show_progress"], self.choose_progress_to_show),
            (self.current_language_dict["show_matching_words"], self.show_matching_words),
            (self.current_language_dict["find_unique_pairs"], self.find_unique_pairs),
            # (self.current_language_dict["solve"], self.try_to_solve_puzzle),
            (self.current_language_dict["solve_with_steps"], self.try_to_solve_puzzle_with_steps),
            (self.current_language_dict["solve_methodically"], self.try_to_solve_puzzle_methodically),
            (self.current_language_dict["restart"], self.puzzle.clear_substitution_dict),
            # (self.current_language_dict["clear_screen"], clear_screen),
            (self.current_language_dict["exit"], exit)
        ]
        # print("Choose an action:")
        print(self.current_language_dict["choose_action"])
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
            choice_num = None
        print()
        if choice_num == 0:
            ans = yes_or_no_question(self.current_language_dict["exit_confirmation"])
            # ans = yes_or_no_question("Are you sure you want to quit?")
            if ans:
                exit()
        return choices[choice_num - 1][1]

    def change_language(self):
        pass

    def add_config(self):
        pass

    def modify_config(self):
        pass

    def save_wordlist(self):
        pass


def main_krypto():
    # start_time_first = time.time()
    krypto = Krypto()
    language, codeword_path = krypto.get_command_line_arguments()
    if language:
        krypto.set_language(language)
    
    if language and codeword_path:
        krypto.initialize_puzzle(codeword_path)
    elif language:
        krypto.input_data_and_initialize_puzzle(language=krypto.language)
    elif codeword_path:
        krypto.input_data_and_initialize_puzzle(codeword_path=codeword_path)
    else:
        krypto.input_data_and_initialize_puzzle()
    
    # end_time_startup = time.time()
    # startup_time_text = mass_replace(krypto.current_language_dict["startup_time_text"], round(end_time_startup - start_time_first, 3))
    # print(f"\nTime taken to startup: {round(end_time_startup - start_time_first, 3)} seconds.\n")
    # print(f"{startup_time_text}")

    krypto.print_initial_info()

    print()

    while True:
        print()
        action = krypto.choose_main_choice()
        action()
    return krypto


if __name__ == "__main__":
    K = main_krypto()



