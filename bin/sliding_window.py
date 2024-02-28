#!/usr/bin/env python3
"""
A python script to split a multiple sequence alignment into several sub-alignments using either
a sliding window approach or a CSV file containing alignment ranges. \b

For each window a separate file in fasta format is written to the directory specified by 'output_directory'.
"""

# external dependencies
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment

# Python Standard Libraries
import argparse
from pathlib import Path
from typing import Generator, Iterable
from enum import Enum
import re
from math import ceil

ILLEGAL_ID_CHARACTERS_REPLACE = {",": "_", ";": "_", "(": "_", ")": "_", " ": "_", "'": "_", ":": "_"}
AMBIGUOUS_CHARACTERS_NUCLEOTIDES_REGEX = "^[\\?|N|\\-|\\.|\\~|\\!|O|X|\\*]*$"
AMBIGUOUS_CHARACTERS_AMINO_ACID_REGEX = "^[U|X|\\?'|\\-|\\.|\\~|\\*|\\!]*$"
AMBIGUOUS_CHARACTERS_OTHER_REGEX = "^[\\-|\\.|\\*]*$"


class SequenceType(Enum):
    NUCLEOTIDE = 1
    AMINO_ACID = 2
    OTHER = 3


class GreaterEqualOne(argparse.Action):
    """
    An argparse action to check if the user value is greater than 0.
    """

    def __call__(self, parser, namespace, values: int, option_string=None):
        if values < 1:
            parser.error("Minimum value for {0} is 1".format(option_string))
        setattr(namespace, self.dest, values)


class WindowInfo:
    """
    A class representing the information of a sub-alignment window.

    Attributes:
        count    (int):  The number of the window.
        strtpos  (int):  The start position of the window.
        midpos   (int):  The middle position of the window.
        endpos   (int):  The end position of the window.
        winlen   (int):  The number of nucleotides in the window.
        _strtpos (int):  The start position of the window in one based format. Only used for displaying the window.
        _midpos  (int):  The middle position of the window in one based format Only used for displaying the window.
        name (str|int):  The name of the window. Either a string specified during the initialization or the one based
                         midpoint.
        rev_comp (bool): Whether the reverse complement of the window should be used.
    """

    def __init__(self, count: int, strtpos: int, endpos: int, midpos: int = None, name: str = None,
                 rev_comp: bool = False):
        """
        Initializes a WindowInfo object.
        :param count: The number of the window.
        :param strtpos: The start position of the window.
        :param endpos: The end position of the window.
        :param midpos: The middle position of the window.
        :param name: The name of the window.
        :param rev_comp: Whether the reverse complement of the window should be used.
        """
        self.count = count
        self.strtpos = strtpos
        self.midpos = midpos if midpos is not None else int(
            (endpos + strtpos) / 2)  # calc midpos based on end and start if not specified; for ranges
        self.endpos = endpos
        self.winlen = endpos - strtpos
        self._strtpos = self.strtpos + 1  # display value
        self._midpos = self.midpos + 1  # display value
        self.name = midpos + 1 if name is None else name
        self.rev_comp = rev_comp

    def get_display(self) -> str:
        """
        Get 1-based information of the window
        :return: The attributes of the window as a tab-separated string in one based format.
        """
        return f"{self.count}\t{self._strtpos}\t{self._midpos}\t{self.endpos}\t{self.winlen}\t{self.name}"

    def __repr__(self) -> str:
        return f"{self.count}\t{self.strtpos}\t{self.midpos}\t{self.endpos}\t{self.winlen}\t{self.name}"


def get_windows_from_parameters(window_size: int, step_size: int, alignment_length: int) \
        -> Generator[WindowInfo, None, None]:
    """
    Create sub-alignment windows from the two parameters window- and step-size.
    :param window_size: Size of the windows.
    :param step_size: Distance between the windows.
    :param alignment_length: Length of the alignment.
    :return: Generator containing WindowInfo objects.
    """
    # in the case of an even window size this results in a longer left side than right side by 1.
    leftwin = int(window_size / 2)
    rightwin = ceil(window_size / 2)  # int(window_size-1 / 2) remove -1 because the end of index range in python is exclusive

    windows = (WindowInfo(count=count, strtpos=max(0, i - leftwin), midpos=i, endpos=min(ali_len, i + rightwin))
               for count, i in enumerate(range(0, alignment_length, step_size)))
    return windows


def get_windows_from_file(path: Path, one_based: bool = False) \
        -> Generator[WindowInfo, None, None]:
    """
    Create sub-alignment windows from the ranges provided in a CSV file.
    :param path: CSV file containing custom ranges. Has to have at least two columns.
        First column is the start position and the second column the end position of the window.
        Optionally can use a third column to specify the name of the windows.
        Furthermore, if the starting position is greater than the end position the reverse complement of this range
        will be used.
    :param one_based: Set to true if the windows in `path` are in one based format.
    :return: Generator containing WindowInfo objects.
    """

    # parse the CSV file specified in path
    with open(path, 'r') as f_r:
        file_content = f_r.read()
    file_content = [i.split(',') for i in file_content.strip().split('\n')]
    n_cols = len(file_content[0])
    if n_cols < 2:
        raise ValueError(
            "The CSV file should have two columns with start and end positions, optionally a third with the name of the range")
    # check if the first two columns are integers
    try:
        file_content = [[int(i[0]), int(i[1])] + i[2:] for i in file_content]
    except ValueError:
        raise ValueError(
            "The first two columns of the CSV file should be start and end position and have to be integer values")

    if one_based:
        windows = (WindowInfo(count=count, strtpos=i[0] - 1, midpos=int((i[0] - 1 + i[1]) / 2), endpos=i[1])
                   for count, i in enumerate(file_content))
    else:
        windows = (WindowInfo(count=count, strtpos=i[0], midpos=int((i[0] + i[1]) / 2), endpos=i[1])
                   for count, i in enumerate(file_content))

    if n_cols > 2:
        windows_names = zip(windows, [i[2] for i in file_content])
        windows = (
        WindowInfo(count=window.count, strtpos=window.strtpos, midpos=window.midpos, endpos=window.endpos, name=name)
        for window, name in windows_names)

    # check if start position of windows is greater than the end position
    # if that's the case swap start and end position and set rev_comp to True
    windows = (WindowInfo(count=window.count, strtpos=window.strtpos, midpos=window.midpos, endpos=window.endpos,
                          name=window.name) if window.winlen > 0 else
               WindowInfo(count=window.count, strtpos=window.endpos, midpos=window.midpos, endpos=window.strtpos,
                          name=window.name, rev_comp=True)
               for window in windows)

    return windows


def load_alignment(path: Path | str, input_format: str = None) -> tuple[AlignIO.MultipleSeqAlignment, str]:
    """
    Open an alignment file and return a tuple of :py:class:`Bio.AlignIO.MultipleSeqAlignment` and str.
    Tries different alignment formats until an alignment format is found that is suitable.
    Raises a ValueError if the file is not in a valid alignment format.
        The following sequence formats are tried to parse the alignment are,
            ["phylip", "phylip-relaxed", "fasta", "nexus", "msf", "maf"]
    :param path: Path to an alignment file. Can either be a Path object or a path specified as string.
    :param input_format: File format of the alignment specified in `path`. Can be used if the format is known
        beforehand.
    :return: A tuple containing a :py:class:`Bio.AlignIO.MultipleSeqAlignment` representing the alignment
        and the file format of the alignment as string.
    """

    # different alignment format used to try to parse the file
    valid_sequence_formats = ["phylip-relaxed", "phylip", "fasta", "nexus", "msf", "clustal"]

    alignment = None
    seq_format = ""

    # check if input_format was specified
    if not input_format:
        for sequence_format in valid_sequence_formats:
            try:
                alignment = AlignIO.read(path, sequence_format)
                seq_format = sequence_format
                break
            except:
                pass
    else:
        seq_format = input_format
        alignment = AlignIO.read(path, seq_format)

    # if alignment could not be parsed raise an error
    if alignment is None:
        raise ValueError(f"Unknown alignment format")

    return alignment, seq_format


def sliding_window(alignment: AlignIO.MultipleSeqAlignment, windows: Iterable[WindowInfo], sequence_type: SequenceType) \
        -> Generator[tuple[AlignIO.MultipleSeqAlignment, WindowInfo], None, None]:
    """
    Generator that yields tuples of :py:class:`Bio.AlignIO.MultipleSeqAlignment` and :py:class:`WindowInfo`.
        Uses the sub-alignment windows specified in `windows` to create slices of the
        :py:class:`Bio.AlignIO.MultipleSeqAlignment` object specified in `alignment`.
        If the sequence type is :py:class:`SequenceType.NUCLEOTIDE` and `rev_comp` is True for a :py:class:`WindowInfo`
        in `windows` then the reverse complement of this window is used.
    :param alignment: The multiple sequence alignment as a :py:class:`Bio.AlignIO.MultipleSeqAlignment`
    :param windows: Iterable of :py:class:`WindowInfo`
    """
    for window in windows:
        if window.rev_comp and sequence_type == SequenceType.NUCLEOTIDE:
            seq_records = alignment[:, window.strtpos: window.endpos]
            for seq_record in seq_records:
                seq_record.seq = seq_record.seq.reverse_complement()
            frag = seq_records
        else:
            frag = alignment[:, window.strtpos: window.endpos]
        yield frag, window


def check_sequence_type(alignment: AlignIO.MultipleSeqAlignment) -> SequenceType:
    """
    Function to determine the sequence-type of an alignment. Uses the first sequence of the alignment and determines
    the sequence-type based on the characters that occur in the sequence. Uses :py:func:`re.search` to check if only
    nucleotide characters or only amino acid characters occur in the alignment. If the sequence type is neither
    determined as nucleotide nor amino acid, the sequence type is set to other.

    :param alignment: The multiple sequence alignment as a :py:class:Bio.AlignIO.MultipleSeqAlignment`
    :return: :py:class:`SequenceType`
    """
    # valid nucleotide and amino acid characters taken from IQ-TREE documentation and IUPAC
    nucleotide = (
    'R', 'Y', 'W', 'S', 'M', 'K', 'B', 'H', 'D', 'V', '\\?', '\\-', '\\.', '\\~', '\\!', 'O', 'N', 'X', '\\*',
    'A', 'C', 'G', 'T', 'U')
    amino_acid = ('A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'O', 'S', 'T',
                  'W', 'Y', 'V', 'B', 'Z', 'J', 'U', 'X', '\\?', '\\-', '\\.', '\\~', '\\*', '\\!')
    nuc_reg_str = f"[^{'|'.join(nucleotide)}]"
    ami_reg_str = f"[^{'|'.join(amino_acid)}]"

    sample_seq = str(alignment[0, :].seq).upper()

    nuc_reg = re.search(nuc_reg_str, sample_seq)
    ami_reg = re.search(ami_reg_str, sample_seq)

    if nuc_reg is None:
        seq_type = SequenceType.NUCLEOTIDE
    elif ami_reg is None:
        seq_type = SequenceType.AMINO_ACID
    else:
        seq_type = SequenceType.OTHER
    return seq_type


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-i', '--input', help="path to the alignment file", required=True, type=Path)
    parser.add_argument('-o', '--output-directory', help="output directory", required=True, type=Path)
    parser.add_argument('-1', '--1-based', help="flag to treat provided ranges with `--split-file` as one-based", required=False,
                        action='store_true')
    parser.add_argument('--keep-ambiguous', help="keep sequences containing only ambiguous characters",
                        required=False, action='store_true')

    parser.add_argument('-w', '--window-size', help="window size",
                        default=300, type=int, action=GreaterEqualOne)
    parser.add_argument('-s', '--step-size', help="step size; distance between two windows",
                        default=25, type=int, action=GreaterEqualOne)
    parser.add_argument('--split-file', help="CSV file containing alignment ranges. Needs to have at least "
                                             "two columns start and end position. If start position is greater than "
                                             "end position and the sequence type is nucleotide then the reverse "
                                             "complement of this range is used. Optionally can use a third column to "
                                             "specify the name of the window.",
                        type=Path)
    parser.add_argument('-f', '--force', help="overwrite files already existing files",
                        required=False, action='store_true')
    parser.add_argument('-l', '--log', help="flag to output log files", required=False, action='store_true')

    args = parser.parse_args()

    alignment_path = args.input
    output_directory: Path = args.output_directory

    window_size = args.window_size
    step_size = args.step_size
    split_file = args.split_file

    force = args.force
    one_based = args.__dict__["1_based"]

    alignment, sequence_format = load_alignment(alignment_path)

    # replace illegal characters from the sequence name for RAxML
    for seq in alignment:
        seq.id = seq.id.translate(str.maketrans(ILLEGAL_ID_CHARACTERS_REPLACE))

    ali_len = alignment.get_alignment_length()

    sequence_type = check_sequence_type(alignment)

    if split_file:
        windows = get_windows_from_file(split_file, one_based=one_based)
    else:
        windows = get_windows_from_parameters(window_size, step_size, ali_len)

    if not output_directory.exists():
        output_directory.mkdir()

    if not args.keep_ambiguous:
        match sequence_type:
            case SequenceType.NUCLEOTIDE:
                amb_regex = AMBIGUOUS_CHARACTERS_NUCLEOTIDES_REGEX
            case SequenceType.AMINO_ACID:
                amb_regex = AMBIGUOUS_CHARACTERS_AMINO_ACID_REGEX
            case SequenceType.OTHER:
                amb_regex = AMBIGUOUS_CHARACTERS_OTHER_REGEX
            case _:
                raise ValueError("Should have Sequence Type from SequenceType Enum")
        amb_regex = re.compile(amb_regex)

    windows_log = [f"count\tstart\tmid\tend\twin_len\tname"]
    removed_sequences = {}

    windows = sliding_window(alignment, windows, sequence_type)

    for frag, window in windows:
        windows_log.append(window.get_display())

        output_path = output_directory.joinpath(f"{window.name}")
        output_path = output_path.with_suffix(".fasta")

        if output_path.exists() and not force:
            raise FileExistsError(
                f"The file {output_path} already exists\n If you want to overwrite already existing files use -f or --force")

        # remove sequences containing only ambiguous characters
        if not args.keep_ambiguous:
            remove_matches = [j if re.match(amb_regex, str(j.seq)) is None else j.id for i, j in enumerate(frag)]
            keep_seqs = [i for i in remove_matches if not isinstance(i, str)]
            remove_seqs = [i for i in remove_matches if isinstance(i, str)]
            frag = MultipleSeqAlignment(keep_seqs)
            if remove_seqs:
                removed_sequences[window.name] = remove_seqs

        # write 2-line fasta format for better performance
        AlignIO.write(frag, output_path, 'fasta-2line')

    if args.log:
        output_log_windows = output_directory.joinpath('windows.log')
        with open(output_log_windows, 'w') as f_w:
            f_w.write('\n'.join(windows_log))

    if removed_sequences:
        entry = '\n'.join([f"{window}\t{','.join(sequences)}" for window, sequences in removed_sequences.items()])
        output_log_removed_sequences = output_directory.joinpath('removed_sequences.log')
        with open(output_log_removed_sequences, 'w') as f_w:
            f_w.write(entry)
