# mdiff
mdiff is a package, tool and application for comparing and generating diff info for input data. 
It has an ability to detect sequence elements displacements (i.e. line in text have been moved up or down).

The features are:
* New `SequenceMatcher` class generating opcodes with sequence elements displacement detection (new opcodes tags: `move` and `moved`).
* API for comparing and generating diff for text inputs.
* CLI for using package as a tool for comparing files.
* Simple Standalone GUI application for comparing text contents.

## Links
* [PyPI](https://pypi.org/project/mdiff/)
* [GitHub](https://github.com/m-matelski/mdiff)

## Requirements
* Python 3.8+

## Installation
For plain python package (no additional dependencies):
```console
pip install mdiff
```

For additional CLI tool and GUI functionalities (uses external packages such as [colorama](https://github.com/tartley/colorama), 
or [Typer](https://github.com/tiangolo/typer)):
```console
pip install mdiff[cli]
```

## Examples
Generating opcodes for input sequences:
```python
from mdiff import HeckelSequenceMatcher

a = ['line1', 'line2', 'line3', 'line4', 'line5']
b = ['line1', 'line3', 'line2', 'line4', 'line6']
sm = HeckelSequenceMatcher(a, b)
opcodes = sm.get_opcodes()
for opcode in opcodes:
    print(opcode)
```
```console
OpCode('equal', 0, 1, 0, 1)
OpCode('move', 1, 2, 2, 2)
OpCode('equal', 2, 3, 1, 2)
OpCode('moved', 1, 1, 2, 3)
OpCode('equal', 3, 4, 3, 4)
OpCode('replace', 4, 5, 4, 5)
```

Extracting changes from input sequences using opcodes:
```python
...
for tag, i1, i2, j1, j2 in opcodes:
    print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2]))
```
```console
equal     a[0:1] --> b[0:1]  ['line1'] --> ['line1']
move      a[1:2] --> b[2:2]  ['line2'] --> []
equal     a[2:3] --> b[1:2]  ['line3'] --> ['line3']
moved     a[1:1] --> b[2:3]         [] --> ['line2']
equal     a[3:4] --> b[3:4]  ['line4'] --> ['line4']
replace   a[4:5] --> b[4:5]  ['line5'] --> ['line6']
```

Generating and printing diff for input strings:
```python
from mdiff import diff_lines_with_similarities, CompositeOpCode

a = 'line1\nline2\nline3\nline4\nline5'
b = 'line1\nline3\nline2\nline4\nline6'
a_lines, b_lines, opcodes = diff_lines_with_similarities(a, b, cutoff=0.75)

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
Indented tags shows in-line differences, in this case `line5` and `line6` strings have the only difference at last character.

## API
General idea is to provide new `SequenceMatcher` object that's compatible with built-in `difflib.SequenceMatcher` class,
so they can be used interchangeably to generate opcodes.

### `HeckelSequenceMatcher`

`HeckelSequenceMatcher` is a class for comparing pairs of sequences of any type, as long as sequences
are comparable and hashable. Unlike builtin `difflib.SequenceMatcher`, it detects and marks elements
displacement between sequences. This class provides `get_opcodes()` method which returns Sequence of opcodes
with differences between sequences, similar as `difflib.SequenceMatcher.get_opcodes()` does, but
with additional `move` and `moved` tags for displaced elements.

`HeckelSequenceMatcher` implements Paul Heckel's algorithm described in
_"A Technique for Isolating Differences Between Files"_ paper, which can be found
[here](http://documents.scribd.com/docs/10ro9oowpo1h81pgh1as.pdf).

---

#### `HeckelSequenceMatcher(a: Sequence[Any] = '', b: Sequence[Any] = '', replace_mode=True)`
Initialize sequence matcher object, parameters:
* `a` - source(old) sequence.
* `b` - target(new) sequence.
* `replace_mode` - if True: it merges consecutive pairs of `insert` and `delete` blocks into `replace` operation. Remains `insert` and `delete` opcodes otherwise.

---

#### `get_opcodes() -> List[OpCode]`
Returns list of `OpCode` objects describing how to turn sequence `a` into `b`.
`OpCode` consists of attributes: `tag`, `i1`, `i2`, `j1`, `j2`. `OpCode` can be unpacked as tuple.

Usually the first tuple has `i1 == j1 == 0`, and remaining tuples have `i1` equal to the `i2`
from the preceding tuple, and, likewise, `j1` equal to the previous `j2`. However, this rule is broken when
`move` and `moved` tags appears in OpCodes list, due to sequence elements displacement detection.

The tags are strings, with these meanings:
* `replace` - `a[i1:i2]` should be replaced by `b[j1:j2]`
* `delete` - `a[i1:i2]` should be deleted. Note that `j1==j2` in this case.
* `insert` - `b[j1:j2]` should be inserted at `a[i1:i1]`. Note that `i1==i2` in this case.
* `equal` - `a[i1:i2] == b[j1:j2]`
* `move` -  `a[i1:i2]` should be moved to `b[j1:j2]` position. Note that `j1==j2` in this case.
* `moved` - is opposite tag for `move`. It's not an operation necessary for turning sequence `a` into `b`. It indicates that `b[j1:j2]` is moved from `i1` position (or `b[j1:j2]` should be moved back to `a[i1:i2]`). Note that `i1==j2` in this case. It can be used for sequence elements movement visualisation.

---

### `DisplacementSequenceMatcher`
`DisplacementSequenceMatcher` is a variation of `HeckelSequenceMatcher` class. 
The algorithm keeps tracking of every sequence element occurrence, which might give better result when both sequences have common unique elements. 
It tries to detect all sequences elements displacements, where `HeckelSequenceMatcher` might sometimes treat displaced elements as delete/insert. 
This `SequenceMatcher` class might be useful when finding all sequences displacements is crucial 
, however for ordinary text sequences it might produce human-unreadable diff.

This object has the same methods as `HeckelSequenceMatcher`

---

### Generating text diff

#### `diff_lines_with_similarities(...)`
This function takes two input text sequences, turns them into lists of lines, generates opcodes for those lines
and tries to find single characters differences in similar lines.

Parameters:
* `a: str` - source text.
* `b: str` - target text.
* `cutoff: float = 0.75` - value in range [0:1], where 0.0 means that lines are completely different and 1.0 means that lines are exactly the same. Line similarity cutoff is used to determine if sub opcodes for similar lines should be generated. If `cutoff == 1`, then in-line diff won't be generated.
* `line_sm: SequenceMatcherBase = None` - SequenceMatcher object used to find differences between input texts lines. `HeckelSequenceMatcher()` will be used if not specified.
* `inline_sm: SequenceMatcherBase = None` - SequenceMatcher object used to find differences between similar lines (i.e. using `difflib.SequenceMatcher` when in-line diff displacement detection is not desirable). `difflib.SequenceMatcher()` will be used if not specified.
* `keepends = False` - Whether to keep newline characters when splitting input sequences.
* `case_sensitive = True` - Whether to perform string case-sensitive comparison when generating diff.

Returns a tuple `(a_lines: List[str], b_lines: List[str], opcodes: List[CompositeOpCode])` where:
* `a_lines` - is list of lines from `a` input text sequence.
* `b_lines` - is list of lines from `b` input text sequence.
* `opcodes` - is list of `CompositeOpCode` which behave the same way as `OpCode` (has `tag i1 i2 j1 j2` fields and can be unpacked), but has additional `children_opcodes` which stores list of nested opcodes with SequenceMatcher result for similar lines. List is empty if lines were not similar enough. (note that similar lines opcodes are generated only for `replace` tags, so children_opcodes list will be empty for every other tag).

---

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
  --gui / --no-gui                Open GUI window with diff result.  [default:
                                  no-gui]
  --case-sensitive / --no-case-sensitive
                                  Whether diff is going to be case sensitive.
                                  [default: case-sensitive]
  --char-mode [utf8|ascii]        Terminal character set used when printing
                                  diff result.  [default: utf8]
  --color-mode [fore|back]        Terminal color mode used when printing diff
                                  result.  [default: fore]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.
```
### Example
Sample output for `mdiff a.txt b.txt` command:

![](https://github.com/m-matelski/mdiff/raw/master/resources/readme/mdiff_cli1.png)

Showing result in GUI `mdiff a.txt b.txt --gui`:

![](https://github.com/m-matelski/mdiff/raw/master/resources/readme/mdiff_gui1.png)


## Standalone GUI application
Standalone app provides simple text editor, which allows generating diff based on user input.

![](https://github.com/m-matelski/mdiff/raw/master/resources/readme/mdiff_gui_app1.png)

Use `mdiff-gui` command to launch GUI application in interpreter mode, or use precompiled version from [here](https://github.com/m-matelski/mdiff/releases/latest).

### Building Standalone GUI application
GUI application can be built directly from source by typing below commands:
```console
> pip install -r requirements.txt
> ./pyinstaler_start.sh
```