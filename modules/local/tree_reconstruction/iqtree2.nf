process IQTREE2 {
    label "process_medium"
    errorStrategy {params.amb_seqs == 'skip' ? 'ignore' : 'finish'}
    publishDir path: "${params.outdir}/tree_reconstruction/iqtree/${alignment.simpleName}", mode: params.publish_dir_mode, enabled: params.keep_tree_files, pattern: "*"
    cpus { Math.floor(percent_total_length*params.max_cpus) }

    conda "bioconda::iqtree=2.2.6"

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/iqtree:2.2.6--h21ec9f0_0' :
        'biocontainers/iqtree:2.2.6--h21ec9f0_0' }"

    input:
    tuple path(alignment), val(model), val(percent_total_length)
    val num_windows

    output:
    path("*.treefile"), emit: treefile
    path("*.contree"), optional:true, emit: consensus_tree
    path("*.log"), emit: log
    path("*.iqtree"), emit: iqtree
    path("*"), emit: all

    when:
    params.run_mode == 'full'

    script:
    def args = params.phylo_parameters?: ''

    """
    iqtree2 --quiet -T AUTO -ntmax ${task.cpus} -s ${alignment} -m ${model} ${args}
    """
}