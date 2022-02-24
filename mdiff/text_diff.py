from difflib import SequenceMatcher
from itertools import chain
from typing import Union, Sequence, Generator, List, Tuple, Type

from mdiff.block_extractor import EmptyStringBlockExtractor, extraction_inversion, convert_to_slices
from mdiff.seqmatch.heckel import HeckelSequenceMatcher, DisplacementSequenceMatcher
from mdiff.utils import pair_iteration, OpCodesType, OpCode, CompositeOpCode, get_composite_layer, SequenceMatcherBase


def find_best_similar_match(i1: int, i2: int, j1: int, j2: int, a: Sequence, b: Sequence, sm: SequenceMatcher = None):
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
                                 sm: SequenceMatcherBase = SequenceMatcher()) -> Generator[CompositeOpCode, None, None]:
    match_i, match_j, match_ratio = find_best_similar_match(i1, i2, j1, j2, a, b)
    if match_ratio > cutoff:
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
                         sm: SequenceMatcherBase = SequenceMatcher()) -> Generator[CompositeOpCode, None, None]:
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'replace':
            yield from extract_replace_similarities(tag, i1, i2, j1, j2, a, b, cutoff, sm)
        else:
            yield CompositeOpCode(tag, i1, i2, j1, j2)


def split_paragraphs(text: str, keepends=False, keepend_after_paragraph=True) -> List[str]:
    text_splitlines = tuple(text.splitlines(True))
    text_splitlines_without_ends = tuple(text.splitlines(False))
    split_len = len(text_splitlines)
    empty_string_blocks = list(EmptyStringBlockExtractor(text_splitlines_without_ends).extract_blocks())
    paragraph_string_blocks = list(extraction_inversion(split_len, empty_string_blocks))

    if keepends:
        paragraphs_blocks = []
        if empty_string_blocks[0][0] == 0:
            z = list(chain(*zip(empty_string_blocks, paragraph_string_blocks)))
            if keepend_after_paragraph:
                paragraphs_blocks.append(z.pop(0))
        else:
            z = list(chain(*zip(paragraph_string_blocks, empty_string_blocks)))

        for pair_block in pair_iteration(z):
            if len(pair_block) == 2:
                (b1_start, b1_len), (b2_start, b2_len) = pair_block
                paragraph_block = (b1_start, b1_len + b2_len)
                paragraphs_blocks.append(paragraph_block)
            else:
                paragraphs_blocks.append(pair_block[0])
        paragraphs_slices = list(convert_to_slices(paragraphs_blocks))
    else:
        paragraphs_slices = list(convert_to_slices(paragraph_string_blocks))
    result = [''.join(text_splitlines[i]) for i in paragraphs_slices]
    return result


def split_all_levels(a: str, b: str):
    # paragraphs
    a_par = split_paragraphs(a, keepends=True)
    b_par = split_paragraphs(b, keepends=True)
    sm = DisplacementSequenceMatcher(a_par, b_par)
    par_opcodes = sm.get_opcodes()

    # lines
    a_lines = [tuple(i.splitlines(True)) for i in a_par]
    b_lines = [tuple(i.splitlines(True)) for i in b_par]
    line_opcodes = list(extract_similarities(par_opcodes, a_lines, b_lines, 0.75))

    # characters
    root_comp = CompositeOpCode('root', 0, 0, 0, 0)
    root_comp.children_opcodes = line_opcodes
    line_layer = list(get_composite_layer(root_comp, 2, lambda x: x.children_opcodes))
    x = 1
    a_characters = [i for i in a_lines]


def diff_lines_with_similarities(a: str, b: str, line_similarity_cutoff=0.75,
                                 line_sm: SequenceMatcherBase = DisplacementSequenceMatcher(),
                                 similarities_sm: SequenceMatcherBase = SequenceMatcher()) \
        -> Tuple[List[str], List[str], List[CompositeOpCode]]:
    a_lines = a.splitlines(keepends=False)
    b_lines = b.splitlines(keepends=False)
    line_sm.set_seqs(a_lines, b_lines)
    line_opcodes = line_sm.get_opcodes()
    line_opcodes_with_similarities = \
        extract_similarities(line_opcodes, a_lines, b_lines, line_similarity_cutoff, similarities_sm)
    return a_lines, b_lines, list(line_opcodes_with_similarities)

