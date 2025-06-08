
from pathlib import Path
import pytest

import krypto


def test_read_config():
    config_path = Path(__file__).parent / "test_stuff" / "test_config.conf"
    default_language, config_dict = krypto.read_config(config_path)

    assert default_language == "tag"
    assert config_dict["tag"]["name"] == "default"
    assert config_dict["tag"]["alphabet"] == "abcdefg"
    assert config_dict["tag"]["wordlist_path"] == Path("test_stuff") / "test_wordlist"
    assert config_dict["tag"]["codeword_folder_path"] == Path("test_stuff")

    assert config_dict["another_tag"]["name"] == "second"
    assert config_dict["another_tag"]["alphabet"] == "abcdefghijklmnopqrstuvwxyzåäö"
    assert config_dict["another_tag"]["wordlist_path"] is None
    assert config_dict["another_tag"]["codeword_folder_path"] == Path(__file__).parent


def test_get_language_dict():
    language_file_path = Path(__file__).parent / "language_file"
    language_dict = krypto.get_language_dict(language_file_path)
    assert "fi" in language_dict.keys()
    assert "en" in language_dict.keys()
    assert language_dict["fi"]["yes"] == "kyllä"
    assert language_dict["en"]["no"] == "no"
    assert language_dict["fi"]["words_in_file"] == "%1% sanaa tiedostossa %2%"
    assert language_dict["en"]["find_unique_pairs"] == "Find unique pairs"


def test_get_wordlist():
    wordlist_path = Path(__file__).parent / "test_stuff" / "test_wordlist"
    expected_wordlist = ["some", "words", "here", "to", "be", "read", "by", "someone", "or", "something", "cola", "camp"]
    assert krypto.get_wordlist(wordlist_path) == expected_wordlist


def test_get_csv_files_in_folder():
    csv_files = list(krypto.get_csv_files_in_folder())
    path1 = Path(__file__).parent.parent / "cw25-05-12.csv"
    if path1.exists():
        assert path1 in csv_files
    path2 = Path(__file__).parent.parent / "k24-51-52.csv"
    if path2.exists():
        assert path2 in csv_files


def test_get_codewords():
    codeword_path = Path(__file__).parent / "test_stuff" / "test_codewords"
    expected_codewords = [
        (1, 2, 3, 4, 5, 6),
        (3, 7, 9),
        (8, 10, 11),
        (10, 12, 13),
        (3, 22, 24, 15),
        (21, 15, 13, 11)
    ]
    expected_comments = ["this is a comment", "another line"]
    comments, codewords = krypto.get_codewords(codeword_path)
    assert comments == expected_comments
    assert codewords == expected_codewords


@pytest.mark.parametrize(
        "word, alphabet, result", [
            ("abcdefghijklmnopqrstuvwxyz", "abcdefghijklmnopqrstuvwxyz", True),
            ("abc", "def", False),
            ("no?", "abcdefghijklmnopqrstuvwxyz", False),
            ("yes?", "abcdefghijklmnopqrstuvwxyz?", True),
            ("älämölö", "abcdefghijklmnopqrstuvwxyzåäö", True)
        ]
)
def test_are_letters_in_alphabet(word, alphabet, result):
    assert krypto.are_letters_in_alphabet(word, alphabet) == result


def test_find_correspondence0():
    substitutions = ((1, "a"), (2, "b"), (3, "x"), (5, "p"), (-7, "g"))
    assert krypto.find_correspondence(1, substitutions) == "a"
    assert krypto.find_correspondence(2, substitutions) == "b"
    assert krypto.find_correspondence("x", substitutions) == 3
    assert krypto.find_correspondence("p", substitutions) == 5
    assert krypto.find_correspondence(-7, substitutions) == "g"
    assert krypto.find_correspondence("c", substitutions) is None
    assert krypto.find_correspondence(4, substitutions) is None


def test_nums_to_letters():
    nums = (1, 3, 25)
    substitution = ((1, "a"), (2, "b"), (3, "c"), (10, "j"), (15, "q"), (25, "e"))
    expected_letters = "ace"
    assert krypto.nums_to_letters(nums, substitution) == expected_letters


def test_letters_to_nums():
    letters = "ace"
    substitution = ((1, "a"), (2, "b"), (3, "c"), (10, "j"), (15, "q"), (25, "e"))
    expected_nums = (1, 3, 25)
    assert krypto.letters_to_nums(letters, substitution) == expected_nums


def test_count_in_how_many_words_numbers_are():
    codewords = [(1, 2, 3, 5), (2, 3, 4), (1, 3, 6), (1, 3, 5)]
    expected_counts = {1: 3, 2: 2, 3: 4, 4: 1, 5: 2, 6: 1}
    assert krypto.count_in_how_many_words_numbers_are(codewords) == expected_counts


def test_get_decoding_tuple0():
    codewords = [(1, 2, 3, 2), (4, ), (5, 6)]
    words = ["here", "i", "am"]
    expected_substitution_tuple = ((1, "h"), (2, "e"), (3, "r"), (4, "i"), (5, "a"), (6, "m"))
    assert krypto.get_substitution_tuple(codewords, words) == expected_substitution_tuple


def test_get_decoding_tuple():
    codewords = [(1, 2, 3, 2), (4, ), (5, 6)]
    words = ["here", "i", "am"]
    previous_substitution_tuple = ((2, "e"), (4, "i"), (7, "t"))
    expected_substitution_tuple = ((1, "h"), (2, "e"), (3, "r"), (4, "i"), (5, "a"), (6, "m"), (7, "t"))
    assert krypto.get_substitution_tuple(codewords, words, previous_substitution_tuple) == expected_substitution_tuple


@pytest.mark.parametrize(
        "codeword, substitution_tuple, expected_word", [
            ((1, 4, 7, 1, 2, 3, 2), ((1, "h"), (2, "e"), (3, "r"), (4, "i"), (5, "a"), (6, "m"), (7, "t")), "hithere"),
            ((2, 10, 4, 7, 2), ((1, "h"), (2, "e"), (3, "r"), (4, "i"), (5, "a"), (6, "m"), (7, "t")), "e?ite")
        ]
)
def test_decrypt_codeword(codeword, substitution_tuple, expected_word):
    assert krypto.decrypt_codeword(codeword, substitution_tuple) == expected_word


def test_decrypt_codewords():
    codewords = [(1, 2, 3, 2), (4, ), (5, 6)]
    words = ["here", "i", "am"]
    substitution_tuple = ((1, "h"), (2, "e"), (3, "r"), (4, "i"), (5, "a"), (6, "m"), (7, "t"))
    expected_result = tuple(zip(codewords, words))
    assert krypto.decrypt_codewords(codewords, substitution_tuple) == expected_result


@pytest.mark.parametrize(
    "word, codeword, result", [
        ("hello", (1, 2, 3, 3, 4), True),
        ("world", (1, 2, 3, 4, 2), False)
    ]
)
def test_does_word_match(word, codeword, result):
    assert krypto.does_word_match(word, codeword) == result


@pytest.mark.parametrize(
    "word, codeword, substitution_tuple, result", [
        ("hello", (1, 2, 10, 10, 15), ((1, "h"), (2, "e"), (3, "r"), (4, "i"), (5, "a"), (6, "m"), (7, "t")), True),
        ("hello", (1, 2, 3, 3, 15), ((1, "h"), (2, "e"), (3, "r"), (4, "i"), (5, "a"), (6, "m"), (7, "t")), False),
        ("world", (0, 314, 3, 10, 28), ((1, "h"), (2, "e"), (3, "r"), (4, "i"), (5, "a"), (6, "m"), (7, "t")), True),
        ("world", (1, 2, 3, 4, 5), ((1, "h"), (2, "e"), (3, "r"), (4, "i"), (5, "a"), (6, "m"), (7, "t")), False)
    ]
)
def test_does_word_match_to_substitution_tuple(word, codeword, substitution_tuple, result):
    assert krypto.does_word_match_to_substitution_tuple(word, codeword, substitution_tuple) == result


@pytest.mark.parametrize(
    "word1, word2, codeword1, codeword2, result", [
        ("some", "some", (3, 22, 24, 15), (21, 15, 13, 11), False),
        ("cola", "camp", (3, 22, 24, 15), (21, 15, 13, 11), False),
        ("zola", "camp", (3, 22, 24, 15), (21, 15, 13, 11), True)
    ]
)
def test_do_two_words_match(word1, word2, codeword1, codeword2, result):
    assert krypto.do_two_words_match(word1, word2, codeword1, codeword2) == result


def test_get_matching_words():
    codeword = (1, 2, 3, 3, 4)
    wordlist = ["hello", "world", "tiny", "english", "abccd"]
    expected_answer = ["hello", "abccd"]
    assert krypto.get_matching_words(codeword, wordlist) == expected_answer


def test_does_word_match_to_matching_indices():
    word = "hello"
    dict_works = {
        "h": [0],
        "e": [1],
        "l": [2, 3],
        "o": [4]
    }
    dict_doesnt_work = {
        "a": [0],
        "e": [1],
        "h": [0],
        "l": [2, 3],
        "o": [4]
    }
    dict_doesnt_work_either = {
        "a": [0],
        "b": [1]
    }
    assert krypto.does_word_match_to_matching_indices(word, dict_works)
    assert not krypto.does_word_match_to_matching_indices(word, dict_doesnt_work)
    assert not krypto.does_word_match_to_matching_indices(word, dict_doesnt_work_either)

def test_does_word_match_to_matching_indices2():
    matching_indices = {
        "c": [0],
        "o": [1],
        "l": [2],
        "a": [3]
    }
    word = "camp"
    assert not krypto.does_word_match_to_matching_indices(word, matching_indices)


def test_does_word_match_to_fixed_index_values():
    word = "hello"
    dict_works = {
        0: "h",
        2: "l"
    }
    dict_doesnt_work = {
        0: "h",
        3: "o"
    }
    nothing_works = dict()
    assert krypto.does_word_match_to_fixed_index_values(word, dict_works)
    assert not krypto.does_word_match_to_fixed_index_values(word, dict_doesnt_work)
    assert krypto.does_word_match_to_fixed_index_values(word, nothing_works)


@pytest.mark.parametrize(
        "word, total_length, result", [
            ("hello", 7, "hello  "),
            ("world", 4, "worl"),
            ("longer", 10, "longer    "),
            ("uncharacteristic", 16, "uncharacteristic")
        ]
)
def test_add_whitespace(word, total_length, result):
    assert krypto.add_whitespace(word, total_length) == result


@pytest.mark.parametrize(
        "codeword, written_codeword", [
            ((1, 1, 1, 1), "1,1,1,1"),
            ((1, 2, 3), "1,2,3"),
            ((25, 30, 10, 0), "25,30,10,0")
        ]
)
def test_codeword_as_str(codeword, written_codeword):
    assert krypto.codeword_as_str(codeword) == written_codeword


@pytest.mark.parametrize(
    "text, additions, result", [
        ("he%1%o", ("ll",), "hello"),
        ("w%1%r%2%d", ("o", "l"), "world"),
        ("something %1% %2% strange %3%", ("NOT", "particularly", "at all"), "something NOT particularly strange at all"),
        ("%1% me %2% others", (1, (2, 3)), "1 me (2, 3) others")
    ]
)
def test_mass_replace(text, additions, result):
    assert krypto.mass_replace(text, *additions) == result


@pytest.fixture
def puzzle():
    codeword_path = Path(__file__).parent / "test_stuff" / "test_codewords"
    comments, codewords = krypto.get_codewords(codeword_path)
    config_path = Path(__file__).parent / "test_stuff" / "test_config.conf"
    default_language, config_dict = krypto.read_config(config_path)
    wordlist = krypto.get_wordlist(config_dict[default_language]["wordlist_path"])
    return krypto.CodewordPuzzle(codewords, wordlist, config_dict[default_language]["alphabet"], comments)


def test_CodewordPuzzle_init(puzzle):
    expected_codewords = [
        (1, 2, 3, 4, 5, 6),
        (3, 7, 9),
        (8, 10, 11),
        (10, 12, 13),
        (3, 22, 24, 15),
        (21, 15, 13, 11)
    ]
    assert puzzle.codewords == expected_codewords
    expected_comments = ["this is a comment", "another line"]
    assert puzzle.comments == expected_comments

    expected_wordlist = ["some", "words", "here", "to", "be", "read", "by", "someone", "or", "something", "cola", "camp"]
    assert puzzle.wordlist == expected_wordlist

    assert puzzle.alphabet == "abcdefg"

    expected_substitution_dict = {
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: "",
        8: "",
        9: "",
        10: "",
        11: "",
        12: "",
        13: "",
        15: "",
        21: "",
        22: "",
        24: ""
    }
    assert puzzle.substitution_dict == expected_substitution_dict

    expected_wordlist2 = ["to", "be", "by", "or"]
    assert puzzle.wordlists[2] == expected_wordlist2
    expected_wordlist4 = ["some", "here", "read", "cola", "camp"]
    assert puzzle.wordlists[4] == expected_wordlist4

    expected_matches = {
        (1, 2, 3, 4, 5, 6): [],
        (3, 7, 9): [],
        (8, 10, 11): [],
        (10, 12, 13): [],
        (3, 22, 24, 15): ["some", "read", "cola", "camp"],
        (21, 15, 13, 11): ["some", "read", "cola", "camp"]
    }
    assert puzzle.matched_words_all == expected_matches
    assert puzzle.matched_words == {
        (3, 22, 24, 15): ["some", "read", "cola", "camp"],
        (21, 15, 13, 11): ["some", "read", "cola", "camp"]
    }


# def test_issue1():
#     codeword1 = (3, 22, 24, 15)
#     codeword2 = (21, 15, 13, 11)
#     matching_indices = dict()
#     for num in codeword1:
#         if matching_indices.get(num) is None:
#             matching_indices[num] = [i for i, c in enumerate(codeword2) if c == num]
#     assert matching_indices == {3: [], 22: [], 24: [], 15: [1]}

# def test_issue2():
#     codeword1 = (3, 22, 24, 15)
#     codeword2 = (21, 15, 13, 11)
#     word1 = "cola"
#     word2 = "camp"
#     m_indices = dict()
#     for i, char in enumerate(word1):
#         if m_indices.get(char) is None:
#             m_indices[char] = [i]
#         else:
#             m_indices[char].append(i)
#     assert m_indices == {"c": [0], "o": [1], "l": [2], "a": [3]}

#     word1 = "some"
#     m_indices = dict()
#     for i, char in enumerate(word1):
#         if m_indices.get(char) is None:
#             m_indices[char] = [i]
#         else:
#             m_indices[char].append(i)
#     assert m_indices == {"s": [0], "o": [1], "m": [2], "e": [3]}

# def test_issue3():
#     word2 = "camp"
#     m_indices = {"c": [0], "o": [1], "l": [2], "a": [3]}
#     assert not krypto.does_word_match_to_matching_indices(word2, m_indices)

#     word2 = "some"
#     m_indices = {"s": [0], "o": [1], "m": [2], "e": [3]}


def test_match_two_codewords(puzzle):
    codeword1 = (3, 22, 24, 15)
    codeword2 = (21, 15, 13, 11)
    maximum_matches = 999_999
    assert puzzle.match_two_codewords(codeword1, codeword2, maximum_matches) == [("some", "read")]
