process CollectTrees {
    publishDir path: "${params.outdir}/", mode: params.publish_dir_mode

    conda "conda-forge::python=3.11 bioconda::dendropy"
    container "ggruber193/automated-window-sliding-base_image"

    cpus 1

    input:
    tuple val(output_name), path(trees)

    output:
    path "${output_name}*"

    script: // script collect_trees.py is bundled with the pipeline in the bin directory
    // ensure that output format is separated by ','. E.g. "newick nexus" -> "newick,nexus"
    def output_format = params.output_format?(params.output_format =~ '(?:\\bnewick\\b|\\bnexus\\b)+').findAll().join(',') : 'nexus'

    """
    collect_trees.py -o ${output_name} -i ${trees} --output-format ${output_format}
    """
}