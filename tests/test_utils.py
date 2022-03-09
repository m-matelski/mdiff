import unittest
from enum import Enum

from mdiff.utils import CompositeDelegationMixin, sort_seq_by_other_seq, sort_seq_by_other_seq_indexes, \
    sort_string_seq_by_other


class TestCompositeDelegationMixin(unittest.TestCase):
    def test_attributes_and_method_delegation(self):
        # base class
        class MyClass:
            def __init__(self, a):
                self.a = a

                self.b = self.choose_b()

            def choose_b(self):
                if self.a > 10:
                    return 'a>10'
                return 'a<10'

            def set_a(self, new_a):
                self.a = new_a

            def print_a(self):
                print(self.a)

            def return_a(self):
                return self.a

        # composite class from base
        class MyClassComposite(MyClass, CompositeDelegationMixin):
            def __init__(self, *args, **kwargs):
                super().__init__(a=0)
                CompositeDelegationMixin.__init__(self)

        mc1 = MyClass(1)
        mc2 = MyClass(2)
        mcc = MyClassComposite()
        mcc.__children__.extend([mc1, mc2])

        # call method on children
        return_a = mcc.return_a()
        self.assertEqual(return_a, [1, 2])

        # set value for all children
        mcc.set_a(3)
        # get value directly by attribute
        a_attribute = mcc.a
        self.assertEqual(a_attribute, [3, 3])

        with self.assertRaises(AttributeError):
            mcc.non_existing_attribute

        with self.assertRaises(AttributeError):
            mcc.non_existing_method()


class TestSortSequenceByOther(unittest.TestCase):
    def test_sort_sequence_on_unique_values(self):
        a = [6, 5, 4, 2, 3]
        b = [1, 2, 3, 4]
        result = sort_seq_by_other_seq(a, b)
        expected = [2, 3, 4, 6, 5]
        self.assertEqual(expected, result)

    def test_sort_sequence(self):
        a = [5, 4, 3, 5, 1, 2]
        b = [1, 3, 1, 5, 6, 1, 4]
        result = sort_seq_by_other_seq(a, b)
        expected = [1, 3, 5, 4, 5, 2]
        self.assertEqual(expected, result)

    def test_sort_sequence_indexes(self):
        a = ['F', 'E', 'D', 'E']
        b = ['A', 'B', 'E', 'D']
        result = sort_seq_by_other_seq_indexes(a, b)
        expected = [(1, 'E'), (2, 'D'), (0, 'F'), (3, 'E')]
        self.assertEqual(expected, result)

    def test_sort_str_sequence_case_sensitive(self):
        a = ['a', 'C', 'b', 'A']
        b = ['A', 'B', 'E', 'D']

        result = sort_string_seq_by_other(a, b, case_sensitive=True)
        expected = ['A', 'a', 'C', 'b']
        self.assertEqual(expected, result)

        result = sort_string_seq_by_other(a, b, case_sensitive=False)
        expected = ['a', 'b', 'C', 'A']
        self.assertEqual(expected, result)
