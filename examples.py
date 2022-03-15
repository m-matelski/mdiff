from mdiff import HeckelSequenceMatcher

a = ['line1', 'line2', 'line3', 'line4', 'line5']
b = ['line1', 'line3', 'line2', 'line4', 'line6']
sm = HeckelSequenceMatcher(a, b)
for opcode in sm.get_opcodes():
    print(opcode)
