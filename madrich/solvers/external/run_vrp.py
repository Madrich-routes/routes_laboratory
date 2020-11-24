import logging
import subprocess

from absl import app, flags

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(lineno)d %(message)s")

FLAGS = flags.FLAGS

# tf.logging.set_verbosity(tf.logging.ERROR)
flags.DEFINE_string('algo', None, 'ej; init; rtr; sa')
flags.DEFINE_string('vrp_file', None, 'path to .vrp file')
flags.DEFINE_integer('num_ejected', None, 'FOR EJ: num_ejected should be something less than 20 or so')
flags.DEFINE_integer(
    'num_trials', None, 'FOR EJ: num_trials can be fairly large as the procedure is fast (say 1000)'
)
flags.DEFINE_integer(
    'method',
    None,
    'FOR EJ: method must be 0 (RANDOM search), 1 (REGRET search)\nFOR INIT: method should be 0 for CW, 1 for Sweep',
)
flags.DEFINE_string(
    'sol_file',
    None,
    'FOR EJ OPTIONAL: Can start with a solution in sol_file or it will generate an initial solution for you',
)
flags.DEFINE_string('out_file', None, 'Can write the final best solution discovered to out_file')
flags.DEFINE_boolean('verbose', False, 'Adding --verbose will print verbose output')
flags.DEFINE_boolean(
    'clean',
    False,
    'If --clean option is given, then all routes are cleaned up at the end by running intra-route improvements',
)
flags.DEFINE_integer(
    'accept_type',
    None,
    'FOR RTR: -a <accept_type> 0 for VRPH_FIRST_ACCEPT or 1 for VRPH_BEST_ACCEPT (default is VRPH_FIRST_ACCEPT)',
)
flags.DEFINE_float(
    'deviation', None, 'FOR RTR: -d <deviation> runs the RTR search with given deviation default is dev=.01'
)
flags.DEFINE_string(
    'fixed_edge_file', None, 'FOR RTR: -fix <fixed_edge_file> will fix all of the edges in the provided file'
)
flags.DEFINE_string(
    'heuristic',
    None,
    'FOR RTR OR SA: -h <heuristic> applies the specified heuristics (can be repeated) \n \
                default is ONE_POINT_MOVE, TWO_POINT_MOVE, and TWO_OPT \n \
                others available are OR_OPT, THREE_OPT, and CROSS_EXCHANGE\n \
                Example: -h OR_OPT -h THREE_OPT -h TWO_OPT -h ONE_POINT_MOVE\n \
                Setting -h KITCHEN_SINK applies all heuristics in the improvement phase',
)
flags.DEFINE_float(
    'intensity',
    None,
    'FOR RTR: -k <intensity> runs the RTR search with the provided intensity (default is 30)',
)
flags.DEFINE_string(
    'num_lambdas',
    None,
    'FOR RTR OR SA: -L <num_lambdas> runs the RTR OR SA procedure from num_lambdas \n \
                different initial solutions using a random lambda chosen from (0.5,2.0)'
    ' default is to use lambda in {.6, 1.4, 1.6}.',
)
flags.DEFINE_integer(
    'max_tries',
    None,
    'FOR RTR: -m <max_tries> gives up after not beating a local minimum after \
                max_tries consecutive attempts (default is 5)',
)
flags.DEFINE_integer(
    'nlist_size',
    None,
    'FOR RTR OR SA: -N <nlist_size> uses the nlist_size nearest neighbors in the search \
                default is 25(RTR) 40(SA). Using -N 0 will not use neighbor lists at all',
)
flags.DEFINE_integer(
    'num_perturbs',
    None,
    'FOR RTR: -P <num_perturbs> perturbs the current solution num_perturbs times (default is 1)',
)
flags.DEFINE_integer(
    'perturb_type', None, 'FOR RTR: <perturb_type> 0 for VRPH_LI_PERTURB or 1 for VRPH_OSMAN_PERTURB'
)
flags.DEFINE_string(
    'plot',
    None,
    'FOR RTR OR SA: <plot> plots the best solution to the provided file. This requires a working PLPlot installation',
)
flags.DEFINE_string('pdf', None, 'FOR RTR OR SA: -pdf will create a .pdf from the .ps file created by -plot')
flags.DEFINE_boolean(
    'rand_neighbor', False, 'FOR RTR: <rand_neighbor> will search the neighborhood in a random fashion'
)
flags.DEFINE_string(
    'tabu_list_size', None, 'FOR RTR: <tabu_list_size> will use a primitive Tabu Search in the uphill phase'
)
flags.DEFINE_integer(
    'num_iters', None, 'FOR SA: -i <num_iters> runs the SA procedure for num_iters iterations before cooling'
)
flags.DEFINE_integer(
    'num_loops', None, 'FOR SA: -n <num_loops> runs the SA procedure a total of num_loops times'
)
flags.DEFINE_float(
    'starting_temperature',
    None,
    'FOR SA: -t <starting_temperature> runs the SA procedure starting at this temperature',
)
flags.DEFINE_float(
    'cooling_ratio',
    None,
    'FOR SA: -c <cooling_ratio> runs the SA by decreasing the temperature by a '
    'multiplicative factor of cooling_ratio every num_iters moves',
)
flags.DEFINE_integer('num_heur_sols', None, 'for ej')
# flags.DEFINE_bool('help', None, 'print this message')

flags.register_validator(
    'algo', lambda x: x in ['ej', 'init', 'rtr', 'sa'], message='please, use algo from "ej, init, rtr, sa"'
)

req_args = {
    'ej': ['vrp_file', 'num_ejected', 'num_trials', 'method', 'out_file'],
    'init': ['vrp_file', 'method', 'out_file'],
    'rtr': ['vrp_file', 'out_file'],
    'sa': ['vrp_file', 'out_file'],
}
extra_args = {
    'ej': ['sol_file', 'verbose', 'num_heur_sols'],
    'init': ['clean'],
    'rtr': [
        'accept_type',
        'deviation',
        'fixed_edge_file',
        'heuristic',
        'intensity',
        'num_lambdas',
        'max_tries',
        'nlist_size',
        'num_perturbs',
        'perturb_type',
        'plot',
        'pdf',
        'rand_neighbor',
        'tabu_list_size',
    ],
    'sa': [
        'heuristic',
        'num_lambdas',
        'nlist_size',
        'plot',
        'pdf',
        'num_iters',
        'num_loops',
        'starting_temperature',
        'cooling_ratio',
    ],
}

keymap = {
    'ej': {
        'vrp_file': '-f',
        'num_ejected': '-j',
        'num_trials': '-t',
        'method': '-m',
        'out_file': '-out',
        'sol_file': '-s',
        'num_heur_sols': '-n',
        'verbose': '-v',
    },
    'init': {'vrp_file': '-f', 'method': '-m', 'out_file': '-out', 'clean': '-c'},
    'rtr': {
        'vrp_file': '-f',
        'out_file': '-out',
        'accept_type': '-a',
        'deviation': '-d',
        'fixed_edge_file': '-fix',
        'heuristic': '-h',
        'intensity': '-k',
        'num_lambdas': '-L',
        'max_tries': '-m',
        'nlist_size': '-N',
        'num_perturbs': '-P',
        'perturb_type': '-p',
        'plot': '-plot',
        'pdf': '-pdf',
        'rand_neighbor': '-r',
        'tabu_list_size': '-t',
    },
    'sa': {
        'vrp_file': '-f',
        'out_file': '-out',
        'heuristic': '-h',
        'num_lambdas': '-l',
        'nlist_size': '-s',
        'plot': '-plot',
        'pdf': '-pdf',
        'num_iters': '-i',
        'num_loops': '-n',
        'starting_temperature': '-t',
        'cooling_ratio': '-c',
    },
}


def main(argv):
    cmd = [f'bin/vrp_{FLAGS.algo}']
    # Specify necessary args
    for arg in req_args[FLAGS.algo]:
        logging.info(FLAGS[arg].amounts)
        if FLAGS[arg].amounts is None:
            print(f'Please, specify --{arg}')
            exit(1)
        cmd += [keymap[FLAGS.algo][arg], str(FLAGS[arg].amounts)]
    # Specify extra args if any
    for arg in extra_args[FLAGS.algo]:
        if FLAGS[arg].amounts is not None:
            cmd += [keymap[FLAGS.algo][arg], str(FLAGS[arg].amounts)]

    logging.info(f'Execute command: {cmd}')

    p = subprocess.run(cmd)
    if p.returncode == 0:
        logging.info(f'\nSuccess, see file {FLAGS.out_file}')
    else:
        logging.info(f'\nSome error')


if __name__ == "__main__":
    # FLAGS(sys.argv)
    app.run(main)
