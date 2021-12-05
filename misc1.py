import difflib

from mdiff.seq_compare import GenericSequenceComparator

a = ['F3', 'F5', 'F1', 'F2', 'F7']
b = ['F1', 'F4', 'F6', 'F2', 'F3', 'F8']

# a = ['F1', 'F2', 'F3']
# b = ['F1', 'F3', 'F2']

s = difflib.SequenceMatcher(None, a, b)
opcodes = list(s.get_opcodes())
print('--------opcodes-------')
for tag, i1, i2, j1, j2 in opcodes:
    print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2]))


grouped_opcodes = list(s.get_grouped_opcodes(0))
print('--------grouped opcodes-------')
for group in grouped_opcodes:
    for tag, i1, i2, j1, j2 in group:
        print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2]))

scmp = GenericSequenceComparator(a, b)
scmp_opcodes = [i for i in scmp.compare_sequences()]
print('--------mycmop-------')
for i in scmp_opcodes:
    print(f"{i.source_key} - {i.target_key} - {i.status}")


d = difflib.Differ()
c = list(d.compare(a, b))
print('--------differ-------')
print('\n'.join(c))




x=1