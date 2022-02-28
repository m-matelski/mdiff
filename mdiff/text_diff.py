from difflib import SequenceMatcher
from typing import Sequence, Generator, List, Tuple

from mdiff.seqmatch.heckel import HeckelSequenceMatcher
from mdiff.utils import OpCodesType, OpCode, CompositeOpCode, SequenceMatcherBase


def find_best_similar_match(i1: int, i2: int, j1: int, j2: int, a: Sequence, b: Sequence, sm: SequenceMatcher = None) \
        -> Tuple[int, int, float]:
    """
    Finds most similar pair of elements in sequences bounded by indexes a[i1:i2], b[j1: j2].

    :param i1: starting index in "a" sequence.
    :param i2: ending index in "a" sequence.
    :param j1: starting index in "b" sequence.
    :param j2: ending index in "b" sequence.
    :param a: first sequence.
    :param b: second sequence.
    :param sm: SequenceMatcher object. Creates new difflib.SequenceMatcher instance if not passed.

    :return: Tuple (best_i, best_j, best_ratio) where:
        best_i: is index of most similar element in sequence "a".
        best_j: is index of most similar element in sequence "b".
        best_ratio: similarity ratio of elements a[best_i] and b[best_j], where 1.0 means elements are identical
            and 0.0 means that elements are completely different.
    """
    best_ratio = 0.0
    best_i = best_j = None
    if not sm:
        sm = SequenceMatcher()

    for i in range(i1, i2):
        sm.set_seq1(a[i])
        for j in range(j1, j2):
            sm.set_seq2(b[j])
            if sm.real_quick_ratio() > best_ratio and sm.quick_ratio() > best_ratio and sm.ratio() > best_ratio:
                best_i = i
                best_j = j
                best_ratio = sm.ratio()

    return best_i, best_j, best_ratio


def extract_replace_similarities(tag: str, i1: int, i2: int, j1: int, j2: int, a: Sequence, b: Sequence, cutoff: float,
                                 sm: SequenceMatcherBase = None) -> Generator[CompositeOpCode, None, None]:
    """
    Finds and extracts similarities in sequences bounded by indexes a[i1:i2], b[j1: j2].
    Returns CompositeOpCode object with subsequence level of opcodes for pair of elements from sequences "a" and "b"
    when similarity between those elements is greater than cutoff.
    If elements are not similar enough, they are replaced into "insert" and "delete" tags.

    This function should be used with opcodes tagged as "replace".
    This function assumes that elements of sequences "a" and "b" are also sequences
    (i.e list of strings split by new line character).

    :param tag: opcode tag
    :param i1: starting index in "a" sequence.
    :param i2: ending index in "a" sequence.
    :param j1: starting index in "b" sequence.
    :param j2: ending index in "b" sequence.
    :param a: first sequence.
    :param b: second sequence.
    :param cutoff: Value in range of (0.0: 1.0). Elements similarity ratio cutoff to generate subsequence diff.
    :param sm: SequenceMatcher object. Creates new difflib.SequenceMatcher instance if not passed.

    :return: Generator of CompositeOpCode elements with potential subsequences opcodes.
    """
    if sm is None:
        sm = SequenceMatcher()

    match_i, match_j, match_ratio = find_best_similar_match(i1, i2, j1, j2, a, b)
    if match_ratio == 1.0:
        yield CompositeOpCode('equal', i1, i2, j1, j2)
    elif match_ratio > cutoff:
        # left
        yield from extract_replace_similarities(tag, i1, match_i, j1, match_j, a, b, cutoff)

        # replace middle
        sm.set_seqs(a=a[match_i], b=b[match_j])
        opcodes = [OpCode(*i) for i in sm.get_opcodes()]
        opcode = CompositeOpCode(tag, match_i, match_i + 1, match_j, match_j + 1)
        opcode.children_opcodes.extend(opcodes)
        yield opcode

        # right
        yield from extract_replace_similarities(tag, match_i + 1, i2, match_j + 1, j2, a, b, cutoff)
    else:
        if not (i1 == i2 and j1 == j2):
            if i1 == i2:
                yield CompositeOpCode('insert', i1, i2, j1, j2)
            elif j1 == j2:
                yield CompositeOpCode('delete', i1, i2, j1, j2)
            else:
                yield CompositeOpCode(tag, i1, i2, j1, j2)


def extract_similarities(opcodes: OpCodesType, a: Sequence, b: Sequence, cutoff: float,
                         sm: SequenceMatcherBase = None) -> Generator[CompositeOpCode, None, None]:
    """
    Translate OpCodes into CompositeOpCodes. Input sequences must contain sequences
    (for example list of strings generated by str.splitlines() function).
    This function is searches for "replace" opcodes, tries to find similar lines in those opcodes
    and generates sub-opcodes in form of CompositeOpCodes objects.
    CompositeOpCode's with detected similarities has non-empty list of opcodes in children_opcode attribute.

    :param opcodes:
    :param a: first sequence.
    :param b: second sequence.
    :param cutoff: Value in range of (0.0: 1.0). Elements similarity ratio cutoff to generate subsequence diff.
    :param sm: SequenceMatcher object. Creates new difflib.SequenceMatcher instance if not passed.

    :return: Generator of CompositeOpCode where children_opcodes attribute may contain opcodes regarding
    subsequence comparison (for example similar text lines).
    """
    if sm is None:
        sm = SequenceMatcher()

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'replace':
            yield from extract_replace_similarities(tag, i1, i2, j1, j2, a, b, cutoff, sm)
        else:
            yield CompositeOpCode(tag, i1, i2, j1, j2)


def diff_lines_with_similarities(a: str, b: str, line_similarity_cutoff=0.75,
                                 line_sm: SequenceMatcherBase = None,
                                 similarities_sm: SequenceMatcherBase = None) \
        -> Tuple[List[str], List[str], List[CompositeOpCode]]:
    """
    Takes input strings "a" and "b", splits them by newline characters and generates line diff opcodes.
    For every "replace" tag generated on line level a search for similar lines is performed,
    if similarity exceeds line_similarity_cutoff value, then additional opcodes are generated
    on character level that distinguish similar lines.

    :param a: source input text.
    :param b: target input text.
    :param line_similarity_cutoff: Value in range of (0.0: 1.0) where 0.0 means that lines are completely different
    and 1.0 means that lines are exactly the same. Line similarity cutoff is used to determine
    if sub opcodes for similar lines should be generated.
    :param line_sm: SequenceMatcher object used to generate diff tags between input texts lines.
    :param similarities_sm: SequenceMatcher object used to generate diff tags between characters in similar lines.

    :return: (a_lines, b_lines, opcodes) where:
        a_lines: is "a" input text split by newline characters.
        b_lines: is "b" input text split by newline characters.
        opcodes:
            is List of CompositeOpCode elements where root level of CompositeOpCode object is associated
            with line level diff. CompositeOpCode's children_opcodes list attribute contains single character level diff
            between similar lines. children_opcode list is empty when no lines meets line_similarity_cutoff condition.
            (note that similar lines opcodes are generated only for "replace" tags, so children_opcodes list
            will be empty for every other tag).

    Example:
    >>> a, b, opcodes = diff_lines_with_similarities(a='aa1\\nbb2\\ncc3', b='aa1\\ncc2', line_similarity_cutoff=0.6)
    >>> a
    ['aa1', 'bb2', 'cc3']
    >>> b
    ['aa1', 'cc2']
    >>> opcodes
    [CompositeOpCode('equal', 0, 1, 0, 1), CompositeOpCode('delete', 1, 2, 1, 1), CompositeOpCode('replace', 2, 3, 1, 2)*]
    >>> opcodes[2].children_opcodes
    [OpCode('equal', 0, 2, 0, 2), OpCode('replace', 2, 3, 2, 3)]
    """
    if line_sm is None:
        line_sm = HeckelSequenceMatcher()
    if similarities_sm is None:
        similarities_sm = SequenceMatcher()

    a_lines = a.splitlines(keepends=False)
    b_lines = b.splitlines(keepends=False)
    line_sm.set_seqs(a_lines, b_lines)
    line_opcodes = line_sm.get_opcodes()
    line_opcodes_with_similarities = \
        extract_similarities(line_opcodes, a_lines, b_lines, line_similarity_cutoff, similarities_sm)
    return a_lines, b_lines, list(line_opcodes_with_similarities)
