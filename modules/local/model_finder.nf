process ModelSelection {
    label "process_high"
    errorStrategy {params.amb_seqs == 'skip' ? 'ignore' : 'finish'}

    cpus { !params.model_finder_splits ? params.max_cpus-1 : Math.floor(percent_total_length*params.max_cpus)}
    // Math.floor((params.max_cpus/num_windows))

    conda "bioconda::iqtree=2.2.6"

    container 'biocontainers/iqtree:2.2.6--h21ec9f0_0'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/iqtree:2.2.6--h21ec9f0_0' :
        'biocontainers/iqtree:2.2.6--h21ec9f0_0' }"

    input:
    tuple path(alignment), val(percent_total_length)
    val num_windows

    output:
    tuple val("${alignment.baseName}"), path("${alignment}.model.txt"), emit: model_tuple
    path("${alignment}.log"), emit: log
    path("${alignment}.iqtree"), emit: iqtree

    when:
    params.run_mode == 'full' || params.run_mode == 'model'

    script:
    def args = params.model_finder_params?: ''
    
    def model_criterions = ["bic": "BIC", "aic": "AIC", "aicc": "AICc"]
    def model_criterion = model_criterions[params.model_criterion]

    """
    iqtree2 -T AUTO -ntmax ${task.cpus} -s ${alignment} -n 0 -m MF ${args}
    zcat ${alignment}.model.gz | grep -e "best_model_${model_criterion}:" | cut -d' ' -f2 > ${alignment}.model.txt
    """
}
