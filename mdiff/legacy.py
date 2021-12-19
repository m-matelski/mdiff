from typing import List

KEYS_ORDER_TARGET = 'target'
KEYS_ORDER_SOURCE = 'source'
KEYS_ORDER_ZIP = 'zip'
KEY_ORDER_OPTIONS = (KEYS_ORDER_TARGET, KEYS_ORDER_SOURCE, KEYS_ORDER_ZIP)


def get_item_or_none(iterable, i):
    try:
        return iterable[i]
    except IndexError:
        return None


def compare_keys_zip(source_keys, target_keys):
    pos_factor = 0
    src_idx = 0
    tgt_idx = 0
    key_comp_list = []
    # set of common keys
    common_keys = source_keys.keys() & target_keys.keys()

    common_keys_upper = set([k.upper() for k in source_keys.keys()]) & set([k.upper() for k in target_keys.keys()])

    while src_idx < len(source_keys) or tgt_idx < len(target_keys):

        src_key = get_item_or_none(list(source_keys.keys()), src_idx)
        tgt_key = get_item_or_none(list(target_keys.keys()), tgt_idx)

        src_key_upper = src_key.upper() if src_key is not None else None
        tgt_key_upper = tgt_key.upper() if tgt_key is not None else None

        if src_key_upper in common_keys_upper and tgt_key_upper in common_keys_upper:
            comparison_dict = {
                'source': source_keys[src_key],
                'target': target_keys[tgt_key],
                'exists_on_source': True,
                'exists_on_target': True,
                'match': True,  # exists_on_source and exists_on_target
                'inserted_on_source': False,
                'inserted_on_target': False,
                'order_match': bool(src_idx + pos_factor==tgt_idx and src_key_upper==tgt_key_upper)
            }
            key_comp_list.append(comparison_dict)
            src_idx += 1
            tgt_idx += 1

        else:

            if tgt_key_upper not in common_keys_upper and tgt_key_upper is not None:
                comparison_dict = {
                    'source': None,
                    'target': target_keys[tgt_key],
                    'exists_on_source': False,
                    'exists_on_target': True,
                    'match': False,
                    'inserted_on_source': False,
                    'inserted_on_target': bool(src_idx + pos_factor==tgt_idx),
                    'order_match': bool(src_idx + pos_factor==tgt_idx)
                }
                key_comp_list.append(comparison_dict)
                tgt_idx += 1
                pos_factor += 1

            if src_key_upper not in common_keys_upper and src_key_upper is not None:
                comparison_dict = {
                    'source': source_keys[src_key],
                    'target': None,
                    'exists_on_source': True,
                    'exists_on_target': False,
                    'match': False,
                    'inserted_on_source': bool(src_idx + pos_factor==tgt_idx),
                    'inserted_on_target': False,
                    'order_match': bool(src_idx + pos_factor==tgt_idx)
                }
                key_comp_list.append(comparison_dict)
                src_idx += 1
                pos_factor -= 1

    return key_comp_list


class KeysComparisonResult:
    """Stores data about comparison result of 2 lists of keys"""

    def __init__(self, source, target, exists_on_source, exists_on_target, match, inserted_on_source,
                 inserted_on_target, order_match):
        self.source = source
        self.target = target
        self.exists_on_source = exists_on_source
        self.exists_on_target = exists_on_target
        self.match = match
        self.inserted_on_source = inserted_on_source
        self.inserted_on_target = inserted_on_target
        self.order_match = order_match

    def __repr__(self):
        return f'({self.source}, {self.target})'


def compare_keys(source, target, key=None) -> List[KeysComparisonResult]:
    getter = key if key is not None else lambda a: a
    # dict key insertion order
    source_keys = {getter(i): i for i in source}
    target_keys = {getter(i): i for i in target}

    res = compare_keys_zip(source_keys, target_keys)
    keys_comparison = [KeysComparisonResult(**r) for r in res]

    return keys_comparison