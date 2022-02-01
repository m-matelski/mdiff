from difflib import SequenceMatcher
from itertools import chain
from typing import Union, Sequence

from mdiff.block_extractor import EmptyStringBlockExtractor, extraction_inversion, convert_to_slices
from mdiff.seqmatch.heckel import HeckelSequenceMatcher, DisplacementSequenceMatcher
from mdiff.utils import pair_iteration, OpCodesType, OpCode, CompositeOpCode


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


def extract_replace_similarities(tag: str, i1: int, i2: int, j1: int, j2: int, a: Sequence, b: Sequence, cutoff: float):
    match_i, match_j, match_ratio = find_best_similar_match(i1, i2, j1, j2, a, b)
    if match_ratio > cutoff:
        # left
        yield from extract_replace_similarities(tag, i1, match_i, j1, match_j, a, b, cutoff)

        # replace middle
        opcodes = [OpCode(*i) for i in SequenceMatcher(a=a[match_i], b=b[match_j]).get_opcodes()]
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


def extract_similarities(opcodes: OpCodesType, a: Sequence, b: Sequence, cutoff: float):
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'replace':
            yield from extract_replace_similarities(tag, i1, i2, j1, j2, a, b, cutoff)
        else:
            yield CompositeOpCode(tag, i1, i2, j1, j2)


def split_paragraphs(text: str, keepends=False, keepend_after_paragraph=True):
    text_splitlines = text.splitlines(True)
    text_splitlines_without_ends = text.splitlines(False)
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
    result = [text_splitlines[i] for i in paragraphs_slices]
    return result
