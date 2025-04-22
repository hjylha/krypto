
import string
import sys


DEFAULT_LANGUAGE = "fi"


def get_alphabet_and_wordlist_path(language_tag=None):
    a = "alphabet"
    p = "wordlist"
    section = None
    alphabet = None
    # wordlist_path = None
    with open("config", "r") as f:
        for line in f:
            if language_tag is None and "default_language" in line:
                language_tag = line.strip().split("=")[1].strip()
            if f"[{a}]" in line:
                section = a
                continue
            if f"[{p}]" in line:
                section = p
                continue
            if language_tag.lower() in line:
                value = line.strip().split("=")[1].strip()
                if section == a:
                    alphabet = value
                    continue
                if section == p:
                    wordlist_path = value
                    continue
    return alphabet, wordlist_path


SUOMALAISET_AAKKOSET = "abcdefghijklmnopqrstuvwxyzåäö"

def are_letters_in_alphabet(word, alphabet):
    if alphabet is None:
        return True
    alphabet = alphabet.lower()
    for char in word.lower():
        if char not in alphabet:
            return False
    return True


# WORDLISTPATH = "nykysuomensanalista2024.csv"
WORDLISTPATH = "nykysuomensanalista2024.txt"


def get_wordlist(wordlistpath):
    wordlist = []
    with open(wordlistpath, "r") as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            word = line.split("\t")[0].strip().lower()
            if word:
                wordlist.append(word)
    return wordlist

# FULL_WORDLIST = []

# with open(WORDLISTPATH, "r") as f:
#     for i, line in enumerate(f):
#         if i == 0:
#             continue
#         word = line.split("\t")[0].lower()
#         if word:
#             FULL_WORDLIST.append(word)
FULL_WORDLIST = get_wordlist(WORDLISTPATH)

WORDLIST = [word for word in FULL_WORDLIST if are_letters_in_alphabet(word, SUOMALAISET_AAKKOSET)]

wordlists = dict()

for word in WORDLIST:
    num = len(word)
    if wordlists.get(num) is None:
        wordlists[num] = [word]
        continue
    wordlists[num].append(word)


# crypto_path = "krypto51-52.csv"
crypto_path = "krypto16-17.csv"

def get_crypto_words(crypto_path):
    crypto_words = []
    with open(crypto_path, "r") as f:
        for line in f:
            nums_str = line.strip("\n").split(",")
            if not nums_str:
                continue
            nums_str.append("")
            nums = nums_str[:nums_str.index("")]
            if not nums:
                continue
            word = tuple(int(num) for num in nums)
            crypto_words.append(word)
    return crypto_words

CRYPTO_WORDS = get_crypto_words(crypto_path)
# with open(crypto_path, "r") as f:
#     for line in f:
#         nums_str = line.strip("\n").split(",")
#         if not nums_str:
#             continue
#         nums_str.append("")
#         nums = nums_str[:nums_str.index("")]
#         if not nums:
#             continue
#         word = tuple(int(num) for num in nums)
#         CRYPTO_WORDS.append(word)


def get_nums_in_crypto_words(crypto_words):
    nums_in_crypto_words = []
    for crypto_word in crypto_words:
        for num in crypto_word:
            if num not in nums_in_crypto_words:
                nums_in_crypto_words.append(num)
    return tuple(sorted(nums_in_crypto_words))


CORRESPONDENCE = tuple((num, string.ascii_letters[i]) for i, num in enumerate(get_nums_in_crypto_words(CRYPTO_WORDS)))


# num_of_letters = 28

# correspondence = tuple((i + 1, string.ascii_letters[i]) for i in range(num_of_letters))


def find_correspondence(num_or_char, correspondence_tuple=CORRESPONDENCE):
    for num, char in correspondence_tuple:
        if num_or_char == num:
            return char
        if num_or_char == char:
            return num


def nums_to_letters(tuple_of_nums, correspondence=CORRESPONDENCE):
    return "".join([find_correspondence(num, correspondence) for num in tuple_of_nums])


def letters_to_nums(letters, correspondence=CORRESPONDENCE):
    return tuple(find_correspondence(char, correspondence) for char in letters)


def count_in_how_many_words_numbers_are(encrypted_words):
    counts = dict()
    try:
        for num_tuple in encrypted_words:
            for num in set(num_tuple):
                if counts.get(num) is None:
                    counts[num] = 1
                else:
                    counts[num] += 1
    except TypeError as err:
        print(err)
    return counts


def break_up_word(the_full_word, references):
    words = []
    remaining_word = the_full_word
    # current_index = 0
    for ref in references:
        cutoff_index = len(ref)
        words.append(remaining_word[:cutoff_index])
        remaining_word = remaining_word[cutoff_index:]
        if not remaining_word:
            return tuple(words)
    raise Exception(f"Something is wrong with breaking up {the_full_word} according to {references}")


def get_decoding_tuple(references, words, previous_decoding_tuple=None):
    decoding_pairs = [] if previous_decoding_tuple is None else list(previous_decoding_tuple)
    for ref, word in zip(references, words):
        for char_r, char in zip(ref, word):
            if char_r in [c_r for c_r, c in decoding_pairs]:
                continue
            decoding_pairs.append((char_r, char))
    return tuple(sorted(decoding_pairs, key=lambda p: p[0]))


def decrypt_crypto_word(crypto_word, decoding_tuple, not_found_symbol="?"):
    chars = []
    for num in crypto_word:
        char = find_correspondence(num, decoding_tuple)
        char = not_found_symbol if char is None else char
        chars.append(char)
    return "".join(chars)


def decrypt_crypto_words(crypto_words, decoding_tuple, not_found_symbol="?"):
    decoded_words = []
    for c_word in crypto_words:
        # chars = []
        # for num in c_word:
        #     char = find_correspondence(num, decoding_tuple)
        #     char = not_found_symbol if char is None else char
        #     chars.append(char)
        # decoded_words.append((c_word, "".join(chars)))
        decoded_words.append((c_word, decrypt_crypto_word(c_word, decoding_tuple, not_found_symbol)))
    return tuple(decoded_words)


def match_word(word, reference):
    if len(word) != len(reference):
        return False
    for i, chars in enumerate(zip(word, reference)):
        char, char_r = chars
        for char_prev, char_r_prev in zip(word[:i], reference[:i]):
            if char_r == char_r_prev and char != char_prev:
                return False
            if char_r == char_r_prev and char == char_prev:
                break
            if char_r != char_r_prev and char == char_prev:
                return False
    return True


def match_word_to_decoding_tuple(word, reference, decoding_tuple):
    letters_in_tuple = [char for _, char in decoding_tuple]
    for char, num in zip(word, reference):
        expected_char = find_correspondence(num, decoding_tuple)
        if expected_char is None and char in letters_in_tuple:
            return False
        if expected_char is not None and expected_char != char:
            return False
    return True


def get_matching_words(reference, wordlist):
    return [word for word in wordlist if match_word(word, reference)]


def match_word_to_matching_indices(word, matching_indices_dict):
    for char, indices in matching_indices_dict.items():
        for i in indices:
            if char != word[i]:
                return False
    return True

def match_wordlists(reference1, reference2, wordlist1, wordlist2):
    matching_indices = dict()
    for char in reference1:
        if matching_indices.get(char) is None:
            matching_indices[char] = [i for i, c in enumerate(reference2) if c == char]

    matching_pairs = []
    for word1 in wordlist1:
        m_indices = dict()
        for i, char in enumerate(word1):
            m_indices[char] = matching_indices[reference1[i]]
        for word2 in wordlist2:
            if match_word_to_matching_indices(word2, m_indices):
                matching_pairs.append((word1, word2))
    return matching_pairs


def match_new_wordlist(references, matches, new_reference, new_wordlist):
    if not isinstance(references[0], tuple):
        return tuple(match_wordlists(references, matches, new_reference, new_wordlist))
    reference1 = "".join(references)
    wordlist1 = tuple("".join(matching_words) for matching_words in matches)
    new_unformatted_matches = match_wordlists(reference1, new_reference, wordlist1, new_wordlist)
    new_matches = tuple((*break_up_word(w1, references), w2) for w1, w2 in new_unformatted_matches)
    return new_matches


def match_from_references(reference1, reference2):
    wordlist1 = [word for word in WORDLIST if match_word(word, reference1)]
    wordlist2 = [word for word in WORDLIST if match_word(word, reference2)]
    return match_wordlists(reference1, reference2, wordlist1, wordlist2)


# def match_word1(word):
#     if word[0] == word[3] and word[1] == word[4] and word[0] != word[2] and word[1] != word[2]:
#         return True
#     return False

# # def match_word2(word):
# #     if word[0] == word[3] and word[1] == word[2] and word[0] != word[4] and word[1] != word[4]:
# #         return True
# #     return False 

# def match_word2(word):
#     if word[1] == word[2] and word[0] != word[1] and word[1] != word[3]:
#         return True
#     return False

# def matching_2words():
#     pairs = []
#     words1 = [word for word in wordlists[5] if match_word1(word)]
#     words2 = [word for word in wordlists[4] if match_word2(word)]
#     for word1 in words1:
#         for word2 in words2:
#             # if word1[0] == word2[4] and word1[1] == word2[0] and word1[2] != word2[1]:
#             if word1[0] == word2[0] and word1[1] == word2[3] and word1[2] != word2[1]:
#                 pairs.append((word1, word2))
#     return pairs


def try_to_match_more_words(crypto_words, wordlists, start_index, matched_crypto_words=None, decoding_tuple=None, min_matches_wanted=5):
    if start_index < 0:
        return matched_crypto_words, decoding_tuple
    for i in range(start_index, -1, -1):
        current_crypto_word = crypto_words[i]
        if wordlists.get(current_crypto_word) is None:
            continue
        for word in wordlists[current_crypto_word]:
            if matched_crypto_words is None:
                decoding_tuple = get_decoding_tuple([current_crypto_word], [word])
                new_matched_crypto_words, new_decoding_tuple = try_to_match_more_words(crypto_words, wordlists, i - 1, tuple([current_crypto_word]), decoding_tuple, min_matches_wanted)
                if len(new_matched_crypto_words) >= min_matches_wanted:
                    return new_matched_crypto_words, new_decoding_tuple
                continue
            if not match_word_to_decoding_tuple(word, current_crypto_word, decoding_tuple):
                continue
            new_matched_crypto_words = tuple([*matched_crypto_words, current_crypto_word])
            words = tuple([w for _, w in decrypt_crypto_words(matched_crypto_words, decoding_tuple)])
            new_decoding_tuple = get_decoding_tuple(new_matched_crypto_words, [*words, word])
            new_matched_crypto_words, new_decoding_tuple = try_to_match_more_words(crypto_words, wordlists, i - 1, new_matched_crypto_words, new_decoding_tuple, min_matches_wanted)
            if len(new_matched_crypto_words) >= min_matches_wanted:
                return new_matched_crypto_words, new_decoding_tuple
    return matched_crypto_words, decoding_tuple


def try_to_match_words_to_numbers(crypto_numbers, wordlist, min_matches_wanted, min_letter_matches_wanted=3, num_of_iterations=3):
    # most_matching_words = 0
    # best_decryption = []
    crypto_words = sorted([crypto_num for crypto_num in crypto_numbers if crypto_num], key=lambda x: len(x))
    wordlists = {crypto_word: get_matching_words(crypto_word, wordlist) for crypto_word in crypto_words}
    wordlists = {crypto_word: words for crypto_word, words in wordlists.items() if words}

    matched_crypto_words0, decoding_tuple0 = try_to_match_more_words(crypto_words, wordlists, len(crypto_words) - 1, None, None, min_matches_wanted)
    # counts = count_in_how_many_words_numbers_are(matched_crypto_words0)
    # decoding_tuple = tuple(pair for pair in decoding_tuple0 if counts[pair[0]] >= min_letter_matches_wanted)
    matched_crypto_words = matched_crypto_words0
    decoding_tuple = decoding_tuple0
    not_done = num_of_iterations
    # print("ERROR CHECK")
    # for cw, w in decrypt_crypto_words(matched_crypto_words, decoding_tuple):
    #     print(w, "\t", cw)
    # print()
    while not_done:
        counts = count_in_how_many_words_numbers_are(matched_crypto_words)
        decoding_tuple = tuple(pair for pair in decoding_tuple if counts[pair[0]] >= min_letter_matches_wanted)

        filtered_wordlists = dict()
        matched_crypto_words = []
        matched_words = []
        
        for crypto_word, words in wordlists.items():
            filtered_words = [word for word in words if match_word_to_decoding_tuple(word, crypto_word, decoding_tuple)]
            if filtered_words:
                filtered_wordlists[crypto_word] = filtered_words
                if len(filtered_words) == 1:
                    matched_crypto_words.append(crypto_word)
                    matched_words.append(filtered_words[0])
        decoding_tuple = get_decoding_tuple(matched_crypto_words, matched_words)
        if all([len(words) == 1 for words in filtered_wordlists.values()]):
            return matched_crypto_words, decoding_tuple
            print(f"Needed {num_of_iterations - not_done + 1} iterations")
        not_done -= 1
    counts = count_in_how_many_words_numbers_are(matched_crypto_words)
    # decoding_tuple = tuple(pair for pair in decoding_tuple if counts[pair[0]] >= min_letter_matches_wanted)
    return matched_crypto_words, decoding_tuple
    
    # for i in range(len(crypto_words) - 1, -1, -1):
    #     current_crypto_word = crypto_words[i]
    #     if wordlists.get(current_crypto_word) is None:
    #         continue
    #     for word in wordlists[current_crypto_word]:
    #         decoding_tuple = get_decoding_tuple([current_crypto_word], [word])

    # return best_decryption, most_matching_words
    # 
    # result_dict = dict()
    # num_of_words = 1
    # result_dict[num_of_words] = dict()
    # for numberline in crypto_numbers:
    #     reference = nums_to_letters(numberline)
    #     result_dict[num_of_words][(numberline,)] = tuple(word for word in wordlist if match_word(word, reference))
    # while result_dict[num_of_words]:
    #     next_num_of_words = num_of_words + 1
    #     print(f"number of words: {next_num_of_words}")
    #     result_dict[next_num_of_words] = dict()
    #     tested_num = 0
    #     for numbers, matched_words in result_dict[num_of_words].items():
    #         for numberline0, words in result_dict[1].items():
    #             numberline = numberline0[0]
    #             if not numberline:
    #                 continue
    #             # print(numberline)
    #             if numberline in numbers:
    #                 continue
    #             for new_numbers in result_dict[next_num_of_words].keys():
    #                 if all([num in new_numbers for num in [*numbers, numberline]]):
    #                     continue
    #             references = [nums_to_letters(num) for num in numbers]
    #             new_matches = match_new_wordlist(references, matched_words, nums_to_letters(numberline), words)
    #             if new_matches:
    #                 result_dict[next_num_of_words][(*numbers, numberline)] = new_matches
    #                 print(f"{tested_num + 1} new matches found for {(*numbers, numberline)}")
    #         tested_num += 1
    #     num_of_words = next_num_of_words
    # return result_dict


def DW(decoding_tuple):
    return decrypt_crypto_words(CRYPTO_WORDS, decoding_tuple)

def add_padding(word, total_length):
    return word + " " * (total_length - len(word))

def pdw(decoded_words):
    biggest_length = 0
    for c_w, w in decoded_words:
        if len(c_w) > biggest_length:
            biggest_length = len(c_w)
    for c_w, w in decoded_words:
        print(f"{add_padding(w, biggest_length)} \t {c_w}")

def pw(decoding_tuple):
    pdw(DW(decoding_tuple))


def save_decoded_words_to_file(decoded_words, filepath="ratkaisu.csv"):
    with open(filepath, "w") as f:
        for crypto_word, word in decoded_words:
            f.write(f"{','.join([str(num) for num in crypto_word])};{word}\n")


if __name__ == "__main__":
    # print(sys.argv)
    try:
        language_tag = sys.argv[2]
    except IndexError:
        language_tag = None

    alphabet, wordlist_path = get_alphabet_and_wordlist_path(language_tag)
    FULL_WORDLIST = get_wordlist(wordlist_path)
    WORDLIST = [word for word in FULL_WORDLIST if are_letters_in_alphabet(word, alphabet)]

    try:
        crypto_path = sys.argv[1]
        CRYPTO_WORDS = get_crypto_words(crypto_path)
    except IndexError:
        pass
    # decoding_tuple = None
    # res = try_to_match_words_to_numbers(CRYPTO_WORDS, WORDLIST)
    # cw = sorted(CRYPTO_WORDS, key=lambda x: len(x))
    # while cw:
    #     longest_word = cw.pop()
    #     for another_word in cw[::-1]:
    #         matched_words = match_from_references(longest_word, another_word)
    #         if matched_words:
    #             print(f"Matches for {longest_word}, {another_word}")
    #             for w1, w2 in matched_words:
    #                 print(f"{w1}, {w2}")
    #             if len(matched_words) == 1:
    #                 w1, w2 = matched_words[0]
    #                 decoding_tuple = get_decoding_tuple((longest_word, another_word), (w1, w2))
    #             cw = None
    #             break
    # decoded_words = decrypt_crypto_words(CRYPTO_WORDS, decoding_tuple)
    # for c_w, w in decoded_words:
    #     print(f"{w} \t {c_w}")
    print(f"{len(CRYPTO_WORDS)} encrypted words, {len(WORDLIST)} words to match...")

    cw_solved, dt = try_to_match_words_to_numbers(CRYPTO_WORDS, WORDLIST, min_matches_wanted=len(CRYPTO_WORDS) // 8, min_letter_matches_wanted=3, num_of_iterations=10)
    
    print(f"{len(cw_solved)} out of {len(CRYPTO_WORDS)} words found:")
    for w in [word for _, word in decrypt_crypto_words(cw_solved, dt)]:
        if w in WORDLIST:
            print(f"{w} is in wordlist")
        else:
            print(f"{w} NOT in wordlist")
    print()
    print("key:")
    for num, char in dt:
        print(num, char)
    
    print()
    pw(dt)
