import unittest

from mdiff.text_diff import split_paragraphs


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
