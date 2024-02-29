## Introduction

Automated-Window-Sliding is a bioinformatics pipeline that can be used as a starting point for sliding window based phylogenetic analysis. For this the input alignment is split into several subalignments using a sliding window approach or alternatively custom alignment ranges provided in a CSV file. For each of the subalignment windows a tree is reconstructed and in the end all trees are collected in a single Nexus/Newick file. This file can then be used to study effects that change the phylogenetic signal along the alignment, e.g. recombinations, reassortment and selection effects.

![Pipeline Diagram 1](assets/images/diagram1.png)
![Pipeline Diagram 2](assets/images/diagram2.png)

1. Split alignment into subalignments ([Python Script](bin/sliding_window.py))
2. Find best-fit evolutionary model for whole alignment or subalignments ([IQ-TREE ModelFinder](https://github.com/iqtree/iqtree2))
3. Run tree inference on each subalignment
   1. [IQ-TREE](https://github.com/iqtree/iqtree2)
   2. [RAxML-ng](https://github.com/amkozlov/raxml-ng)
4. Collect reconstructed trees in a single file ([Python Script](bin/collect_trees.py))
   1. Nexus
   2. Newick
   3. Both

## Installation

This pipeline runs on the Nextflow Workflow System. For the installation of Nextflow, please refer to [this page](https://www.nextflow.io/docs/latest/getstarted.html).

To run the pipeline the following programs are required:
   * [Python](https://www.python.org/downloads/) (tested with 3.11)
   * Python packages: [DendroPy](https://dendropy.org/), [Biopython](https://biopython.org/wiki/Download)
   * [IQ-TREE](http://www.iqtree.org/#download) ([RAxML-ng](https://github.com/amkozlov/raxml-ng) optional: if used for tree reconstruction)

If you do not want to manually install these dependencies you can run the pipeline with docker, singularity or conda by using `-profile <docker/singularity/podman/apptainer/conda/mamba>`. If you want to use your locally installed programs omit this parameter.

The pipeline can be downloaded via the nextflow pull command
```bash
nextflow pull ggruber193/automated-window-sliding
```
which automatically pulls the latest version of the pipeline into the folder `$HOME/.nextflow/assets` on your computer. This command is also used to update the pipeline to the latest version.

Alternatively the nextflow run command can be used to pull the pipeline and then run it immediately 
```bash
nextflow run ggruber193/automated-window-sliding <additional options>
```

You can also clone the repository and use the pipeline this way. Here you have to use the `nextflow run` and provide the path to the `main.nf` file.

```bash
git clone https://github.com/ggruber193/automated-window-sliding.git
```

```bash
nextflow run <path/to/cloned/repository>/main.nf <additional options>
```


## Usage

To check if everything works correctly the pipeline can be run on a minimal test case by using `-profile test`:

```bash
nextflow run ggruber193/automated-window-sliding -profile test -outdir <OUTDIR>
```

You can use multiple profile options in a single run, for example `-profile test,docker` to run the minimal test case with docker.

To run the pipeline on your own data provide a multiple sequence alignment (only accepts FASTA, PHYLIP, NEXUS, MSF, CLUSTAL) with `--input`:

```bash
nextflow run ggruber193/automated-window-sliding --input <ALIGNMENT> --outdir <OUTDIR>
```

To view available pipeline parameters use:
```bash
nextflow run ggruber193/automated-window-sliding --help
```

For more information about the usage and output of the pipeline refer to the full [Documentation](docs/README.md) of this project.

In addition to the pipeline specific parameters there are several parameters that Nextflow provides. These are invoked with a single dash, e.g. `-resume` to resume a previously failed pipeline run or `-qs <int>` to limit the number of parallel processes. For a full overview of Nextflow CLI parameters please refer to [this page](https://www.nextflow.io/docs/latest/cli.html) or use `nextflow run -h`


## Citations

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.
