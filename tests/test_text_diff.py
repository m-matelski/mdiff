import unittest

from mdiff.text_diff import split_paragraphs, split_all_levels

# TODO: finish tests

class TestSplitParagraphs(unittest.TestCase):

    def test1(self):
        text = "word1 word2\n"\
               "word3 word4\n"\
               "\n"\
               "abc\n"\
               "\r\n"\
               "xyz\n"\
               "\n"\
               "\n"

        paragraphs = split_paragraphs(text, keepends=True)
        x = 1


class TestTextDiff(unittest.TestCase):

    def test1(self):
        a = "word1 word2\n" \
            "word3 word4\n" \
            "\n" \
            "word2_1 word2_2\n" \
            "word2_3 word2_4\n" \
            "word2_5 word2_6\n" \
            "\r\n" \
            "word3_1 word3_2\n" \
            "word3_3 word3_4\n" \
            "word3_5 word3_6\n" \
            "\n" \
            "word4_1 word4_2\n" \
            "\n" \
            "\n"

        b = "word1 word2\n" \
            "word3 word4x\n" \
            "\n" \
            "\r\n" \
            "word3_1 word3_2\n" \
            "word3_3 word3_4\n" \
            "word3_5 word3_6\n" \
            "\n" \
            "\n" \
            "word2_1 word2_2\n" \
            "word2_3 word2_4\n" \
            "word2_5 word2_6\n" \
            "\n" \
            "\n"

        res = split_all_levels(a, b)
        x = 1