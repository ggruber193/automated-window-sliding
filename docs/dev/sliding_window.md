# Table of Contents

* [sliding\_window](#sliding_window)
  * [GreaterEqualOne](#sliding_window.GreaterEqualOne)
  * [WindowInfo](#sliding_window.WindowInfo)
    * [\_\_init\_\_](#sliding_window.WindowInfo.__init__)
    * [get\_display](#sliding_window.WindowInfo.get_display)
  * [get\_windows\_from\_parameters](#sliding_window.get_windows_from_parameters)
  * [get\_windows\_from\_file](#sliding_window.get_windows_from_file)
  * [load\_alignment](#sliding_window.load_alignment)
  * [sliding\_window](#sliding_window.sliding_window)
  * [check\_sequence\_type](#sliding_window.check_sequence_type)
* [collect\_trees](#collect_trees)

<a id="sliding_window"></a>

# sliding\_window

A python script with a CLI to split a multiple sequence alignment into several sub-alignments using either
a sliding window approach or a CSV file containing alignment ranges.

For each window a separate file in fasta format is written to the directory specified by 'output_directory'.

<a id="sliding_window.SequenceType"></a>

## SequenceType Objects

```python
class SequenceType(Enum)
```

Enum for sequence type enumeration. Defines `NUCLEOTIDE`, `AMINO_ACID` and `OTHER`.

<a id="sliding_window.GreaterEqualOne"></a>

## GreaterEqualOne Objects

```python
class GreaterEqualOne(argparse.Action)
```

An argparse action to check if the user value is greater than 0.

<a id="sliding_window.WindowInfo"></a>

## WindowInfo Objects

```python
class WindowInfo()
```

A class representing the information of a sub-alignment window.

**Attributes**:

- `count` _int_ - The number of the window.
- `strtpos` _int_ - The start position of the window.
- `midpos` _int_ - The middle position of the window.
- `endpos` _int_ - The end position of the window.
- `winlen` _int_ - The number of nucleotides in the window.
- `_strtpos` _int_ - The start position of the window in one based format. Only used for displaying the window.
- `_midpos` _int_ - The middle position of the window in one based format Only used for displaying the window.
- `name` _str|int_ - The name of the window. Either a string specified during the initialization or the one based
  midpoint.
- `rev_comp` _bool_ - Whether the reverse complement of the window should be used.

<a id="sliding_window.WindowInfo.__init__"></a>

#### \_\_init\_\_

```python
def __init__(count: int,
             strtpos: int,
             endpos: int,
             midpos: int = None,
             name: str = None,
             rev_comp: bool = False)
```

Initializes a `WindowInfo` object.

**Arguments**:

- `count`: The number of the window.
- `strtpos`: The start position of the window.
- `endpos`: The end position of the window.
- `midpos`: The middle position of the window.
- `name`: The name of the window.
- `rev_comp`: Whether the reverse complement of the window should be used.

<a id="sliding_window.WindowInfo.get_display"></a>

#### get\_display

```python
def get_display() -> str
```

Get 1-based information of the window

**Returns**:

The attributes of the window as a tab-separated string in one based format.

<a id="sliding_window.get_windows_from_parameters"></a>

#### get\_windows\_from\_parameters

```python
def get_windows_from_parameters(
        window_size: int, step_size: int,
        alignment_length: int) -> Generator[WindowInfo, None, None]
```

Create sub-alignment windows from the two parameters window- and step-size.

**Arguments**:

- `window_size`: Size of the windows.
- `step_size`: Distance between the windows.
- `alignment_length`: Length of the alignment.

**Returns**:

Generator containing WindowInfo objects.

<a id="sliding_window.get_windows_from_file"></a>

#### get\_windows\_from\_file

```python
def get_windows_from_file(
        path: Path,
        one_based: bool = False) -> Generator[WindowInfo, None, None]
```

Create sub-alignment windows from the ranges provided in a CSV file.

**Arguments**:

- `path`: CSV file containing custom ranges. Has to have at least two columns.
First column is the start position and the second column the end position of the window.
Optionally can use a third column to specify the name of the windows.
Furthermore, if the starting position is greater than the end position the reverse complement of this range
will be used.
- `one_based`: Set to true if the windows in `path` are in one based format.

**Returns**:

Generator containing WindowInfo objects.

<a id="sliding_window.load_alignment"></a>

#### load\_alignment

```python
def load_alignment(
        path: Path | str,
        input_format: str = None) -> tuple[AlignIO.MultipleSeqAlignment, str]
```

Open an alignment file and return a tuple of [`Bio.AlignIO.MultipleSeqAlignment`](https://biopython.org/docs/1.75/api/Bio.Align.html#Bio.Align.MultipleSeqAlignment) and str.

Tries different alignment formats until an alignment format is found that is suitable.
Raises a ValueError if the file is not in a valid alignment format.
    The following sequence formats are tried to parse the alignment are,
        ["phylip", "phylip-relaxed", "fasta", "nexus", "msf", "clustal"]

**Arguments**:

- `path`: Path to an alignment file. Can either be a Path object or a path specified as string.
- `input_format`: File format of the alignment specified in `path`. Can be used if the format is known
beforehand.

**Returns**:

A tuple containing a [`Bio.AlignIO.MultipleSeqAlignment`](https://biopython.org/docs/1.75/api/Bio.Align.html#Bio.Align.MultipleSeqAlignment) object representing the alignment
and the file format of the alignment as string.

<a id="sliding_window.sliding_window"></a>

#### sliding\_window

```python
def sliding_window(
    alignment: AlignIO.MultipleSeqAlignment, windows: Iterable[WindowInfo],
    sequence_type: SequenceType
) -> Generator[tuple[AlignIO.MultipleSeqAlignment, WindowInfo], None, None]
```

Generator that yields tuples of [`Bio.AlignIO.MultipleSeqAlignment`](https://biopython.org/docs/1.75/api/Bio.Align.html#Bio.Align.MultipleSeqAlignment) and `WindowInfo`.

Uses the sub-alignment windows specified in `windows` to create slices of the
    [`Bio.AlignIO.MultipleSeqAlignment`](https://biopython.org/docs/1.75/api/Bio.Align.html#Bio.Align.MultipleSeqAlignment) object specified in `alignment`.
    If the sequence type is `SequenceType.NUCLEOTIDE` and `rev_comp` is True for a `WindowInfo`
    in `windows` then the reverse complement of this window is used.

**Arguments**:

- `alignment`: The multiple sequence alignment as a [`Bio.AlignIO.MultipleSeqAlignment`](https://biopython.org/docs/1.75/api/Bio.Align.html#Bio.Align.MultipleSeqAlignment) object.
- `windows`: Iterable of `WindowInfo`.

<a id="sliding_window.check_sequence_type"></a>

#### check\_sequence\_type

```python
def check_sequence_type(
        alignment: AlignIO.MultipleSeqAlignment) -> SequenceType
```

Function to determine the sequence-type of an alignment. Uses the first sequence of the alignment and determines

the sequence-type based on the characters that occur in the sequence. Uses [`re.search`](https://docs.python.org/3/library/re.html#re.search) to check if only
nucleotide characters or only amino acid characters occur in the alignment. If the sequence type is neither
determined as nucleotide nor amino acid, the sequence type is set to other.

**Arguments**:

- `alignment`: The multiple sequence alignment as a [`Bio.AlignIO.MultipleSeqAlignment`](https://biopython.org/docs/1.75/api/Bio.Align.html#Bio.Align.MultipleSeqAlignment).AlignIO.MultipleSeqAlignment`

**Returns**:

`SequenceType`

