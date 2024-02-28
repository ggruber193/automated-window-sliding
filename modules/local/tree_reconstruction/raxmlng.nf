process RAXMLNG {
    label "process_medium"
    errorStrategy {params.amb_seqs == 'skip' ? 'ignore' : 'finish'}
    publishDir path: "${params.outdir}/tree_reconstruction/raxml/${alignment.simpleName}", mode: params.publish_dir_mode, enabled: params.keep_tree_files, pattern: "*"
    cpus { Math.floor(percent_total_length*params.max_cpus) }

    conda "bioconda::raxml-ng=1.2.1"

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/raxml-ng:1.2.1--h6d1f11b_0' :
        'biocontainers/raxml-ng:1.2.1--h6d1f11b_0' }"

    input:
    tuple path(alignment), val(model), val(percent_total_length)
    val num_windows

    output:
    path("*.bestTree"), emit: best_tree
    path("*.consensusTree"), optional: true, emit: consensus_tree
    path("*.log"), emit: log
    path("*"), emit: all

    when:
    params.run_mode == 'full'

    script:
    // some RAxML and IQ-TREE models do not match => convert the IQ-TREE model specifications to the corresponding RAxML model specifications
    def iqtree_to_raxml_models = [TN: "TN93", TNe: "TN93ef", JC69: "JC", K2P: "K80", HKY85: "HKY", K3P: "TPM1", K3Pu: "TPM1uf", K81u: "TPM1uf", TPM2u: "TPM2uf", 
                                    TPM3u: "TPM3uf", TIM: "TIM1uf", TIMe: "TIM1", TIM2: "TIM2uf", TIM2e: "TIM2", TIM3: "TIM3uf", TIM3e: "TIM3",
                                    TVMe: "TVMef", FQ: "FE"]
    def args = params.phylo_parameters?: ''
    def model_parts = model.split("\\+")
    def evo_model = model_parts.collect({iqtree_to_raxml_models.getOrDefault(it, it)}).join('+')

    """
    raxml-ng --threads auto{${task.cpus}} --workers auto --msa ${alignment} --model ${evo_model} ${args}
    """
}