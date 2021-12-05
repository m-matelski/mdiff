import unittest

from mdiff.seq_compare import GenericSequenceComparator, KeyComparisonResult, KeyComparisonResultEntry, KeyCompareStatus


class KeyCompareTest(unittest.TestCase):

    def test_ok(self):
        source = ['f1', 'f2', 'f3']
        target = ['f1', 'f2', 'f3']

        key_compare = GenericSequenceComparator(source, target)
        result = key_compare.compare_sequences()
        expected = KeyComparisonResult([KeyComparisonResultEntry(source_key='f1', target_key='f1',
                                                                 missing_keys_offset=0, absolute_offset=0,
                                                                 relative_offset=0, status=KeyCompareStatus.OK),
                                        KeyComparisonResultEntry(source_key='f2', target_key='f2',
                                                                 missing_keys_offset=0, absolute_offset=0,
                                                                 relative_offset=0, status=KeyCompareStatus.OK),
                                        KeyComparisonResultEntry(source_key='f3', target_key='f3',
                                                                 missing_keys_offset=0, absolute_offset=0,
                                                                 relative_offset=0, status=KeyCompareStatus.OK)])
        self.assertEqual(result, expected)

    def test_missing(self):
        source = ['f1', 'f2', 'f3']
        target = ['f1', 'f3']

        key_compare = GenericSequenceComparator(source, target)
        result = key_compare.compare_sequences()
        expected = KeyComparisonResult([KeyComparisonResultEntry(source_key='f1', target_key='f1',
                                                                 missing_keys_offset=0, absolute_offset=0,
                                                                 relative_offset=0, status=KeyCompareStatus.OK),
                                        KeyComparisonResultEntry(source_key='f2', target_key=None,
                                                                 missing_keys_offset=0, absolute_offset=None,
                                                                 relative_offset=None, status=KeyCompareStatus.MISSING),
                                        KeyComparisonResultEntry(source_key='f3', target_key='f3',
                                                                 missing_keys_offset=-1, absolute_offset=-1,
                                                                 relative_offset=0, status=KeyCompareStatus.OK)])
        self.assertEqual(result, expected)

    def test_excessive(self):
        source = ['f1', 'f3']
        target = ['f1', 'f2', 'f3']

        key_compare = GenericSequenceComparator(source, target)
        result = key_compare.compare_sequences()
        expected = KeyComparisonResult([KeyComparisonResultEntry(source_key='f1', target_key='f1',
                                                                 missing_keys_offset=0, absolute_offset=0,
                                                                 relative_offset=0, status=KeyCompareStatus.OK),
                                        KeyComparisonResultEntry(source_key=None, target_key='f2',
                                                                 missing_keys_offset=0, absolute_offset=None,
                                                                 relative_offset=None,
                                                                 status=KeyCompareStatus.EXCESSIVE),
                                        KeyComparisonResultEntry(source_key='f3', target_key='f3',
                                                                 missing_keys_offset=1, absolute_offset=1,
                                                                 relative_offset=0, status=KeyCompareStatus.OK)])
        self.assertEqual(result, expected)

    def test_out_of_order(self):
        source = ['f1', 'f2', 'f3']
        target = ['f1', 'f3', 'f2']

        key_compare = GenericSequenceComparator(source, target)
        result = key_compare.compare_sequences()
        expected = KeyComparisonResult([KeyComparisonResultEntry(source_key='f1', target_key='f1',
                                                                 missing_keys_offset=0, absolute_offset=0,
                                                                 relative_offset=0, status=KeyCompareStatus.OK),
                                        KeyComparisonResultEntry(source_key='f2', target_key='f3',
                                                                 missing_keys_offset=0, absolute_offset=-1,
                                                                 relative_offset=-1,
                                                                 status=KeyCompareStatus.OUT_OF_ORDER),
                                        KeyComparisonResultEntry(source_key='f3', target_key='f2',
                                                                 missing_keys_offset=0, absolute_offset=1,
                                                                 relative_offset=1,
                                                                 status=KeyCompareStatus.OUT_OF_ORDER)])
        self.assertEqual(result, expected)

    def test_new_element(self):
        source = ['f1', 'f2']
        target = ['f1', 'f2', 'f3']

        key_compare = GenericSequenceComparator(source, target)
        result = key_compare.compare_sequences()
        expected = KeyComparisonResult([KeyComparisonResultEntry(source_key='f1', target_key='f1',
                                                                 missing_keys_offset=0, absolute_offset=0,
                                                                 relative_offset=0, status=KeyCompareStatus.OK),
                                        KeyComparisonResultEntry(source_key='f2', target_key='f2',
                                                                 missing_keys_offset=0, absolute_offset=0,
                                                                 relative_offset=0, status=KeyCompareStatus.OK),
                                        KeyComparisonResultEntry(source_key=None, target_key='f3',
                                                                 missing_keys_offset=0, absolute_offset=None,
                                                                 relative_offset=None,
                                                                 status=KeyCompareStatus.EXCESSIVE)])
        self.assertEqual(result, expected)

    def test_random(self):
        source = [f"f{i}" for i in range(100000)]
        target = [f"f{i}" for i in range(110000)]

        key_compare = GenericSequenceComparator(source, target)
        result = key_compare.compare_sequences()
