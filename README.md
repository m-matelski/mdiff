# mdiff
mdiff is a package for finding difference between two input sequences which is able to detect sequence elements displacements.
The features are:
* New SequenceMatcher class compatible with built-in `difflib.SequenceMatcher` class.
* CLI for using package as a simple tool for comparing files.

## Installation
For plain SequenceMatcher classes and API (no additional dependencies):
```console
pip install mdiff
```

For additional CLI tool functionalities (uses external packages such as [colorama](https://github.com/tartley/colorama), 
or [Typer](https://github.com/tiangolo/typer)):
```console
pip install mdiff[cli]
```

## Usage

### HeckelSequenceMatcher
mdiff provides `HeckelSequenceMatcher` class for comparing pairs of sequences of any type, as long as sequences
are comparable and hashable. Unlike builtin `difflib.SequenceMatcher`, it detects and marks elements
displacement between sequences. This class provides `get_opcodes()` method which returns Sequence of opcodes
with differences between sequences in a similar manner as `difflib.SequenceMatcher.get_opcodes()` does, but
with additional `"move"` and `"moved"` tags for displaced elements. 
Unlike `difflib.SequenceMatcher` - this class doesn't provide any additional functionality for generating
human-readable sequence comparisons.

`HeckelSequenceMatcher` implements Paul Heckel's algorithm described in
"A Technique for Isolating Differences Between Files" paper, which can be found
[here](http://documents.scribd.com/docs/10ro9oowpo1h81pgh1as.pdf).



#### Example:
```python
>>> from mdiff import HeckelSequenceMatcher

>>> a = ['line1', 'line2', 'line3', 'line4', 'line5']
>>> b = ['line1', 'line3', 'line2', 'line4', 'line6']
>>> sm = HeckelSequenceMatcher(a, b)
>>> opcodes = sm.get_opcodes()
>>> opcodes

[OpCode('equal', 0, 1, 0, 1), OpCode('move', 1, 2, 2, 2), OpCode('equal', 2, 3, 1, 2), OpCode('moved', 1, 1, 2, 3), OpCode('equal', 3, 4, 3, 4), OpCode('replace', 4, 5, 4, 5)]
```

`OpCode` object can be unpacked like a tuple, so it can easily replace `difflib.SequenceMatcher.get_opcodes()` result:
```python
...
>>> for tag, i1, i2, j1, j2 in opcodes:
...    print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2]))
```
```console
equal     a[0:1] --> b[0:1]  ['line1'] --> ['line1']
move      a[1:2] --> b[2:2]  ['line2'] --> []
equal     a[2:3] --> b[1:2]  ['line3'] --> ['line3']
moved     a[1:1] --> b[2:3]         [] --> ['line2']
equal     a[3:4] --> b[3:4]  ['line4'] --> ['line4']
replace   a[4:5] --> b[4:5]  ['line5'] --> ['line6']
```

### Text diff
#### `diff_lines_with_similarities`
This function takes two input text sequences, turns them into lists of lines, generates opcodes for those lines
and tries to find single characters differences in similar lines.

Parameters:
* `a: str` - source text sequence
* `b: str` - target text sequence
* `line_similarity_cutoff: float = 0.75` - number in range [0:1], where 1 means that lines are identical and 0 means that lines are completely different. Compared lines with similarity ratio > `line_similarity_cutoff` will be used to generate in-line opcodes.
* `line_sm: SequenceMatcherBase = DisplacementSequenceMatcher()` - SequenceMatcher object used to find differences between input texts lines.
* `similarities_sm: SequenceMatcherBase = SequenceMatcher()` - SequenceMatcher object used to find differences between similar lines (i.e. using `difflib.SequenceMatcher` when in-line diff displacement detection is not desirable).

Returns `Tuple[a_lines: List[str], b_lines: List[str], opcodes: List[CompositeOpCode]]` where:
* `a_lines`: is list of lines from `a` input text sequence.
* `b_lines`: is list of lines from `b` input text sequence.
* `opcodes`: is list of `CompositeOpCode` which behave the same way as `OpCode` (has `tag i1 i2 j1 j2` fields and can be unpacked), but has additional `children_opcodes` which stores list of opcodes with SequenceMatcher result for similar lines. List is empty if lines were not similar enough.

##### Example
```python
from mdiff import diff_lines_with_similarities, CompositeOpCode

a = 'line1\nline2\nline3\nline4\nline5'
b = 'line1\nline3\nline2\nline4\nline6'
a_lines, b_lines, opcodes = diff_lines_with_similarities(a, b)

for opcode in opcodes:
    tag, i1, i2, j1, j2 = opcode
    print('{:7}   a_lines[{}:{}] --> b_lines[{}:{}] {!r:>10} --> {!r}'.
          format(tag, i1, i2, j1, j2, a_lines[i1:i2], b_lines[j1:j2]))
    if isinstance(opcode, CompositeOpCode) and opcode.children_opcodes:
        for ltag, li1, li2, lj1, lj2 in opcode.children_opcodes:
            print('\t{:7}   a_lines[{}][{}:{}] --> b_lines[{}][{}:{}] {!r:>10} --> {!r}'
                  .format(ltag, i1, li1, li2, j1, lj1, lj2, a_lines[i1][li1:li2], b_lines[j1][lj1:lj2]))
```
```console
equal     a_lines[0:1] --> b_lines[0:1]  ['line1'] --> ['line1']
move      a_lines[1:2] --> b_lines[2:2]  ['line2'] --> []
equal     a_lines[2:3] --> b_lines[1:2]  ['line3'] --> ['line3']
moved     a_lines[1:1] --> b_lines[2:3]         [] --> ['line2']
equal     a_lines[3:4] --> b_lines[3:4]  ['line4'] --> ['line4']
replace   a_lines[4:5] --> b_lines[4:5]  ['line5'] --> ['line6']
	equal     a_lines[4][0:4] --> b_lines[4][0:4]     'line' --> 'line'
	replace   a_lines[4][4:5] --> b_lines[4][4:5]        '5' --> '6'
```

## CLI Tool

mdiff also provides CLI tool (available only if installed using `pip install mdiff[cli]`). For more information
type `mdiff --help`

```console
Usage: mdiff [OPTIONS] SOURCE_FILE TARGET_FILE

  Reads 2 files from provided paths, compares their content and prints diff.
  If compared lines in text files are similar enough (exceed cutoff) then
  extracts in-line diff.

  There are few possible strategies to choose to use independently in line-
  level and in-line-level diff:

      standard: uses built in python SequenceMatcher object to generate diff,
      elements movement detection not supported.

      heckel: detects elements movement in a human-readable form, might not
      catch all of moves and differences.

      displacement: detects all differences and movements, might not be very
      useful when both input files contains     many common lines (for example
      many empty newlines).

Arguments:
  SOURCE_FILE  Source file path to compare.  [required]
  TARGET_FILE  Target file path to compare.  [required]

Options:
  --line-sm [standard|heckel|displacement]
                                  Choose sequence matching method to detect
                                  differences between lines.  [default:
                                  heckel]
  --inline-sm [standard|heckel|displacement]
                                  Choose sequence matching method to detect
                                  in-line differences between similar lines.
                                  [default: heckel]
  --cutoff FLOAT RANGE            Line similarity ratio cutoff. If value
                                  exceeded then finds in-line differences in
                                  similar lines.  [default: 0.75; 0.0<=x<=1.0]
  --char-mode [utf8|ascii]        Character set used when printing diff
                                  result.  [default: utf8]
  --color-mode [fore|back]        Color mode used when printing diff result.
                                  [default: fore]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.
```
### Example
Sample output for `mdiff a.txt b.txt` command:
![](https://github.com/m-matelski/mdiff/raw/master/resources/readme/mdiff_cli1.PNG)