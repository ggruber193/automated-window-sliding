/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PRINT PARAMS SUMMARY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { paramsSummaryLog; paramsSummaryMap } from 'plugin/nf-validation'

def summary_params = paramsSummaryMap(workflow)


/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT LOCAL MODULES/SUBWORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/


include { SlidingWindow  } from '../modules/local/sliding_window'
include { ModelSelection } from '../modules/local/model_finder'
include { IQTREE2        } from '../modules/local/tree_reconstruction/iqtree2'
include { RAXMLNG        } from '../modules/local/tree_reconstruction/raxmlng'
include { CollectTrees   } from '../modules/local/collect_trees'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow AutomatedWindowSliding {

    // -- MAIN WORKFLOW --

    input_alignment = Channel.fromPath(params.input)

    // check if a file with custom windows was provided -> if not the dummy file NO_FILE is used
    // needs to be done because there is no option for optional input channels
    if ( params.window_file ) {
        custom_windows_file = Channel.fromPath(params.window_file)
    } else {
        custom_windows_file = Channel.fromPath("${projectDir}/assets/NO_FILE")
    }

    sliding_window_output = SlidingWindow(input_alignment, custom_windows_file)

    // collect a overview of the windows
    sliding_window_output.log.collectFile(storeDir: "${params.outdir}")
    
    // collect the removed sequences for each window
    sliding_window_output.removed_sequences.collectFile(storeDir: "${params.outdir}")

    // caluculate the relative length for each window of the total length of all windows for resource allocation
    window_lengths = sliding_window_output.log.splitCsv(sep: '\t', header: true).map({ row -> tuple(row.name, row.win_len.toFloat())})
    total_length = window_lengths.map({it[1]}).sum()
    window_lengths = window_lengths.combine(total_length).map({tuple(it[0], it[1]/it[2])})

    alignment_windows = sliding_window_output.alignments

    num_windows = alignment_windows.flatten().count()

    // assign the model channel
    if ( params.model != null && !params.model.isEmpty() ) {
        // create a channel from the model specified with --model and store it in a file
        evolutionary_model = Channel.from([params.model]).collectFile(name: 'model.txt')
    } else {
        if ( params.model_finder_splits ) {
            // add the relative length of the window to the input for model finder for resource allocation
            model_finder_input = alignment_windows.flatten().map({tuple(it.baseName, it)}).join(window_lengths).map({tuple(it[1], it[2])})
        } else {
            // use dummy channel to satisfy input cardinality
            model_finder_input = input_alignment.combine(Channel.from([1]))
        }
        evolutionary_model = ModelSelection(model_finder_input, num_windows)

        // output tsv file with models for each window
        evolutionary_model.model_tuple.map({"${it[0]}\t${it[1].text}"}).collectFile(name: 'models.txt', storeDir: "${params.outdir}", sort: {it.split('\t')[0].isInteger()?it.split('\t')[0].toInteger():it.split('\t')[0]})
        evolutionary_model.log.collectFile(storeDir: "${params.outdir}/model_finder_logs/logs")
        evolutionary_model.iqtree.collectFile(storeDir: "${params.outdir}/model_finder_logs/iqtree")
    }

    // prepare the input for tree reconstruction -> combine alignment windows with evolutionary model
    if ( params.model != null && !params.model.isEmpty() ) {
        tree_input = alignment_windows.flatten().combine(evolutionary_model.map({it.text.trim()}))
    } else {
        if ( params.model_finder_splits ) {
            alignment_windows = alignment_windows.flatten().map( { tuple(it.baseName, it) } )
            tree_input = alignment_windows.join(evolutionary_model.model_tuple).map( {tuple(it[1], it[2].text.trim())} )
        } else {
            tree_input = alignment_windows.flatten().combine(evolutionary_model.model_tuple.map( {it[1].text.trim()}))
        }
    }

    // add the relative length of the window to the input for model finder for resource allocation
    tree_input = tree_input.map({tuple(it[0].baseName, it[0], it[1])}).join(window_lengths).map({tuple(it[1], it[2], it[3])})

    // tree input now a tuple with 3 entries (alignment_file, model_str, relative_length)

    // choose tree reconstruction program that should be used
    // to add a new phylogenetic program define new process in modules/local and import into this script
    // add the new phylogenetic program as a new branch in this if-else block. Also add parameter as valid pattern in nextflow_schema.json
    // new process should have a output channel containing the reconstructed trees. Assign this output channel to a new channel called treefiles.

    if ( params.phylo_method == "iqtree2" ) {
        tree = IQTREE2(tree_input, num_windows)
        treefiles = tree.treefile
        contrees = tree.consensus_tree
        tree.iqtree.collectFile(storeDir: "${params.outdir}/tree_reconstruction_logs/iqtree_files")
    } else if ( params.phylo_method == "raxml-ng" ) {
        tree = RAXMLNG(tree_input, num_windows)
        treefiles = tree.best_tree
        contrees = tree.consensus_tree
    } else {
        throw new Error("Phylogenetic Program'${params.phylo_method}' not supported")
    }

    tree.log.collectFile(storeDir: "${params.outdir}/tree_reconstruction_logs/logs")
    treefiles = treefiles.collect().map( {tuple("best_trees", it)} )
    contrees = contrees.collect().map( {tuple("consensus_trees", it)} )
    trees = treefiles.concat(contrees)


    // sort the trees by the midpoint position of the window
    if (params.window_file) {
        // create hashmap to get midpoint position based on the filename
        midpoints = sliding_window_output.log.splitCsv(sep: '\t', header: true).map({tuple(it.name, it.mid)}).collect(flat: false).collectEntries(elem -> [elem[0], elem[1].toInteger()])
        trees = trees.map({tuple(it[0], it[1].toSorted({elem -> midpoints.get(elem.simpleName).value}))})
    } else {
        trees = trees.map({tuple(it[0], it[1].toSorted({elem -> elem.simpleName.toInteger()}))})
    }


    CollectTrees(trees)
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
