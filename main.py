import argparse
import logging
import os
import sys

from emulate_spectrum import EffCalcMCA, read_channels
from lsrm_server import ServerThread
from nuclide import Nuclide


def _get_nuclide_from_args(args: argparse.Namespace):
    if len(args.positional) not in (0, 3):
        raise ValueError('need 3 or 0 positional arguments')

    if len(args.positional) == 3:
        nuclide = Nuclide(*args.positional)
    else:
        if args.nuclide is not None:
            nuclide = Nuclide.parse_from(args.nuclide)
        else:
            nuclide = Nuclide.get_default()
    return nuclide


def main():
    # prepare in-file
    parser = argparse.ArgumentParser(
        description='emulate_spectrum -- util for emulate spectrum acquiring with Monte-Carlo method')

    parser.add_argument('positional', help='element Z, A, M', nargs='*', type=int)

    parser.add_argument('-n', '--nuclide', help='nuclide as string, e.g. Co-60 or Cs-137m')
    parser.add_argument('-t', '--time', type=int, default=1, help='acquire time interval, s, default=1')
    parser.add_argument('-s', '--seed', help='seed for random generator, default = 0 <- random seed',
                        type=int, default=0)
    parser.add_argument('-p', '--port', help='lsrm-server port, default: 23', type=int, default=23)
    parser.add_argument('--activity', help='activity for source in Bq, default = 1000 Bq',
                        type=float, default=1000)
    parser.add_argument('--json', help='search tccfcalc_input.json', action="store_true", default=False)
    parser.add_argument('-v', '--verbose', help='verbose mode', action="store_true", default=False)
    args = parser.parse_args()

    # logger
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    # remove old spectrum
    try:
        os.remove("test_spectr.spe")
    except FileNotFoundError:
        pass

    # nuclide and other params
    nuclide = _get_nuclide_from_args(args)
    logging.info(nuclide)
    seed = args.seed
    activity = args.activity
    acq_time = args.time
    channels = read_channels("tccfcalc.in")
    server_port = args.port

    # start calc thread
    mca = EffCalcMCA(nuclide, channels, seed, activity, acq_time)

    # start lsrm thread
    lsrm_server = ServerThread({"effcalc_mca": mca}, server_port)
    lsrm_server.start()

    # command interface
    # can be command line interface
    pass


if __name__ == "__main__":
    main()
