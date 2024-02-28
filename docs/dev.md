# ggruber193/automated-window-sliding: Developer-level-documentation

Overview over the project structure explaining what the individual files are for.
The project structure is based on the [nf-core template](https://nf-co.re/docs/contributing/adding_pipelines#nf-core-pipeline-structure).

- `automated-window-sliding/`
    - `assets/NO_FILE`: This is just an empty file, that is used to provide a custom window file as optional input to the [SlidingWindow process](../modules/local/sliding_window.nf). I took this trick from [here](https://nextflow-io.github.io/patterns/optional-input/).
    - `base_image/Dockerfile`: Dockerfile that is used for building the Docker Image that provides the required Python packages (Biopython, DendroPy) for the [SlidingWindow](../modules/local/sliding_window.nf) and [CollectTrees](../modules/local/collect_trees.nf) process.
    - `bin/`: Directory for scripts that must be directly accessible within a pipeline process. Anything in this directory can be directly called from within Nextflow processes.
        - [`sliding_window.py`](dev/sliding_window.md): Python script with a CLI, that is used in [SlidingWindow](../modules/local/sliding_window.nf) to split the user-provided alignment.
        - `collect_window.py`: Python script with a CLI, that is used in [CollectTrees](../modules/local/collect_trees.nf) to create a single file containing all generated trees. A python script to collect trees in newick format into a single Newick and or Nexus file. Takes multiple tree files in newick format as input and collects them in a single Newick and or Nexus file. The order
of the trees in the output file is the same as specified in the input.
    - `conf/`
        - `base.config`: [Nextflow config file](https://www.nextflow.io/docs/latest/config.html) containing base resource configurations.
        - `test.config`: [Nextflow config file](https://www.nextflow.io/docs/latest/config.html) specifying parameters for a minimal test run of the pipeline.
    - `lib/`: The lib directory contains Groovy utility functions. These are called from within the pipeline to do common pipeline tasks (e.g. parameter schema validation) and to hold Groovy functions that may be useful in the pipeline context (e.g. to validate pipeline-specific parameters). These files were already provided in the [nf-core template](https://nf-co.re/docs/contributing/adding_pipelines#nf-core-pipeline-structure) that was used as a starting point for the project structure.
        - `nfcore_external_java_deps.jar`: Bundled Groovy dependencies so that pipelines work offline (mostly for JSON schema validation - see imports in NfcoreSchema.groovy)
        - `NfcoreTemplate.groovy` - Additional nf-core specific pipeline functions
        - `Utils.groovy` - Additional generic pipeline functions (checking conda config and more)
        - `WorkflowMain.groovy` - Startup functions for the main pipeline (printing logs, custom params initialisation and more)
    - `modules/local/`: Pipeline-specific modules. Each file defines a process. Each process defines several input and output channels used to connect different processes with one another. Also defines the command that is run to generate the output. For more information about Nextflow processes refer to [this page](https://www.nextflow.io/docs/latest/process.html).
        - `tree_reconstruction/`
            - `iqtree2.nf`: IQ-TREE process used for tree reconstruction.
            - `raxmlng.nf`: RAxML-ng process used for tree reconstruction. Inside the script directive a dictionary is defined that maps IQ-TREE model names to RAxML model names.
        - `collect_trees.nf`: Process for collecting trees generated in the tree reconstruction step.
        - `model_finder.nf`: Process to determine best-fit evolutionary model using IQ-TREE ModelFinder.
        - `sliding_window.nf`: Process to perform splitting of the alignment.
    - `test_files/`: Specifies two alignment files that are used in the test profile to run a minimal execution of the pipeline.
    - `workflows/automated-window-sliding.nf`: Here the logic of the workflow is specified. Imports the processes from `modules/local/` and defines the relationship between them as a workflow to achieve the desired behavior of the pipeline.
    - `main.nf`: This script is executed when the pipeline is executed. Parameter validation and displaying the help message is performed in this script. The workflow defined in `workflows/automated-window-sliding.nf` is imported into this script and executed.
    - `nextflow_schema.json`: The JSON schema file is used for pipeline parameter specification. This is automatically created using the nf-core schema build command. It is used for printing command-line help, validating input parameters, building the website docs and for building pipeline launch interfaces (web and cli). To edit this file the use of nf-core schema build is recommended. See the [official documentation](https://nf-co.re/tools#pipeline-schema) for more information.
    - `nextflow.config`: The main nextflow configuration file. It contains the default pipeline parameters, nextflow configuration options and information like pipeline and minimum nextflow version, among others. Additional parameters should be specified inside this file. A overview of all parameters can be found in the [Usage docs](usage.md). The nextflow.config also defines different configuration profiles that can be used to run the pipeline. See the  [Configuration docs](https://nf-co.re/docs/usage/configuration) for more information.