# ggruber193/automated-window-sliding: Output

### Splitting of the alignment

- `removed_sequences.log`: TSV containing the header of all removed sequences for each window.
    <details>
    <summary>File Description</summary>
    This TSV file has 2 columns. In the first column the is the name of the window and in the second column are the sequence headers of the removed sequences, that only contain ambiguous characters. The different sequence headers are separate by a comma.
    
    Here a small example:

    ```tsv title="custom_ranges.csv"
    1       seq1,seq2
    1001    seq3
    3001    seq2,seq3
    ```

    </details>
- `windows.log`: TSV file containing information for each window.
    <details>
    <summary>File Description</summary>
    This TSV file has 6 columns count, start, mid, end, win_len, name. The coordinates are in one-based format.

    - `count`: Sequential numbering of windows starting at 0.
    - `start`: Start position of the window.
    - `mid`: Middle position of the window.
    - `end`: End position of the window.
    - `win_len`: Length of the window.
    - `name`: Name of the window. Either the midpoint or if a CSV file with a name column was provided, the respective name.
    
    Here a small example:

    ```tsv title="custom_ranges.csv"
    count    start    mid    end    win_len    name
    0        1        1      50     50         1
    1        1        26     75     75         26
    2        1        51     100    100        51
    ```

    </details>
- `alignments/`
    - `*.fasta`: If `--output_windows` or `--run_mode split` was used all subalignment that were generated during the splitting process will placed in this directory.

### Model Selection
- `models.txt`: TSV file containing the best-fit evolutionary model for each window.
    <details>
    <summary>File Description</summary>
    This TSV file has 2 columns. In the first is the name of the window and in the second the best-fit evolutionary model.

    ```tsv title="models.txt"
    1       GTR+F+I+G4
    1001    SYM+I+G4
    2001    TN+F+I+G4
    3001    TIM2e+I+G4
    ```

    </details>
- `model_finder_logs/`
    - `logs/`
        - `*.log`: The log file of IQ-TREE will be placed in this directory.
    - `iqtree/`
        - `*.iqtree`: The .iqtree summary files will be placed in this directory.

### Tree reconstruction
- `tree_reconstruction_logs/`
    - `logs/`
        - `*.log`: The log files of IQ-TREE or RAxML will be placed in this directory.
    - `iqtree_files/`
        - `*.iqtree`: If IQ-TREE was used for tree reconstruction, the .iqtree summary file of the execution will be placed in this directory.
- `tree_reconstruction/`
    - `iqtree/`: If `--keep_tree_files` and `--phylo_method iqtree2` was used all output files of of the tree reconstruction process will be placed in this directory.
    - `raxml/`: If `--keep_tree_files` and `--phylo_method "raxml-ng"` was used all output files of of the tree reconstruction process will be placed in this directory.

### Tree Collection
- `best_trees.<nexus/newick>`: File containing all the best trees that were found during tree reconstruction in nexus format.
- `consensus_trees.<nexus/newick>`: File containing all the consensus trees that were generated during tree reconstruction. Created if Bootstrapping was enabled.

If Nexus format is used as output format, then the name of the trees corresponds to either the midpoint of the subalignment window, that was used to reconstruct the tree or if a CSV file with a name column was used then to the respective name.

### Nextflow default output

- `pipeline_info/`
    - `execution_trace*`: Nextflow creates an execution tracing file that contains some useful information about each process executed in your pipeline script, including: submission time, start time, completion time, cpu and memory used.
    - `execution_report*`: Nextflow can create an HTML execution report: a single document which includes many useful metrics about a workflow execution.
    - `execution_timeline*`: Nextflow can render an HTML timeline for all processes executed in your pipeline.
    - `pipeline_dag*`: Directed-acyclic-graph representation of the Nextflow pipeline.

For more information about these output files check out the official [Nextflow documentation](https://www.nextflow.io/docs/latest/tracing.html#execution-report).