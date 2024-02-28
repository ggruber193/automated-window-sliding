process SlidingWindow {
    publishDir path: "${params.outdir}/alignments/", pattern: "*.fasta", mode: params.publish_dir_mode, enabled: "${params.output_windows || params.run_mode == 'split'}"

    cpus 1

    conda "conda-forge::python=3.11 conda-forge::biopython"
    container "ggruber193/automated-window-sliding-base_image"

    input:
    path alignment
    path window_file

    output:
    path('*.fasta'), emit: alignments
    path("windows.log"), emit: log
    path("removed_sequences.log"), optional:true, emit: removed_sequences

    script: // script sliding_window.py is bundled with the the pipeline in the bin directory
    def window_file = window_file.name != 'NO_FILE' ? "--split-file ${window_file}" : ''
    def window_size = params.window_size? "--window-size ${params.window_size}" : ''
    def step_size = params.step_size? "--step-size ${params.step_size}": ''
    def keep_ambiguous = (params.amb_seqs == 'remove') ? '' : '--keep-ambiguous'
    
    """
    sliding_window.py --input ${alignment} ${window_size} ${step_size} --output-directory "" ${window_file} ${keep_ambiguous} --log -1
    """
}