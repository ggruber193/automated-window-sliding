#!/usr/bin/env python3
"""
A python script to collect trees in newick format into a single Newick and or Nexus file.

Takes multiple tree files in newick format as input and collects them in a single Newick and or Nexus file. The order
of the trees in the output file is the same as specified in the input.
"""

import dendropy
import argparse
import pathlib


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-o', '--output', help="output path", required=True, type=pathlib.Path)
    parser.add_argument('-i', '--input', help="Input files in newick format. The order of the trees in "
                                              "the output file is the same as provided as the input file parameter",
                        required=True, nargs="+", type=pathlib.Path)
    parser.add_argument('--output-format', help="Output formats separated by a comma. "
                                                "E.g. 'nexus,newick' or 'nexus'. "
                                                "Only tested with nexus and newick format.",
                        required=True, type=str)

    args = parser.parse_args()

    input_files = args.input
    output_formats = args.output_format.split(',')
    output_path: pathlib.Path = args.output

    trees = dendropy.TreeList()
    labels = []

    for file in input_files:
        trees.read_from_path(file, schema='newick')
        labels.append(file.stem.split('.')[0])

    for i, tree in enumerate(trees):
        tree.label = labels[i]

    for output_format in output_formats:
        current_output = output_path.with_suffix(f".{output_format}")
        trees.write_to_path(current_output, schema=output_format)
