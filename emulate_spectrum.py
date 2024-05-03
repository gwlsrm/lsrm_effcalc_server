import argparse
import logging
import os
import sys
import threading
import time
import typing as tp

import utils.speparser as speparser
from abstract_mca import IMCA
from nuclide import Nuclide
from tccfcalc_wrapper import TccFcalcDllWrapper, get_prepare_error_message

SPE_NAME = "test_spectr.spe"


class StableFpsTimer:
    """
    wait diff time to make cycle work with stable fps
    """
    def __init__(self) -> None:
        self.cur_time = None

    def start(self):
        self.cur_time = time.time()

    def wait(self, n_sec: int):
        assert self.cur_time is not None
        elapsed = time.time() - self.cur_time
        diff = max(0.0, n_sec - elapsed)
        time.sleep(diff)


class CalculationThread(threading.Thread):
    """Thread with spectrum calculation in tccfcalc.dll"""
    def __init__(self, lib: TccFcalcDllWrapper, activity: float, dt: int = 1) -> None:
        super().__init__()
        self.lib = lib
        self.activity = activity
        self.dt = dt
        self._stop_thread = False
        self._run_calc = False
        self._fps_timer = StableFpsTimer()
        self._mutex = threading.Lock()

    def run(self):
        while not self._stop_thread:
            self._fps_timer.start()
            if self._run_calc:
                with self._mutex:
                    err = self.lib.tccfcalc_calc_spectrum_n_sec(self.dt, self.activity)
                if err != 0:
                    logging.error(f"Error #{err} in spectrum emulation")
                    break
            self._fps_timer.wait(self.dt)

    def stop_thread(self):
        self._stop_thread = True

    def run_calc(self):
        self._run_calc = True

    def stop_calc(self):
        self._run_calc = False

    def is_running(self) -> bool:
        return self._run_calc

    def reset_spectrum(self):
        with self._mutex:
            self.lib.tccfcalc_reset_spectrum()
            try:
                os.remove(SPE_NAME)
            except FileNotFoundError:
                pass

    def get_spectrum(self) -> speparser.Spectrum:
        with self._mutex:
            try:
                return speparser.SpectrumReader.parse_spe(SPE_NAME)
            except FileNotFoundError:
                return speparser.Spectrum()


def prepare_lib(nuclide: Nuclide, seed: int) -> TccFcalcDllWrapper:
    cur_path = os.getcwd()
    cur_lib_path = os.path.join(cur_path, 'Lib')
    lib = TccFcalcDllWrapper()
    error_num = lib.tccfcalc_prepare(nuclide.a, nuclide.z, nuclide.m, cur_path, cur_lib_path, seed)
    if error_num:
        error_msg = get_prepare_error_message(error_num)
        logging.error(f'Prepare error #{error_num}: {error_msg}')
        sys.exit()
    return lib


class EffCalcMCA(IMCA):
    def __init__(self, nuclide: Nuclide, channels_num: int, seed: int, activity: float, acquire_time: int = 1) -> None:
        super().__init__()
        self._lib = prepare_lib(nuclide, seed)
        self._channels_num = channels_num
        self._calc_thr = CalculationThread(self._lib, activity, acquire_time)
        self._calc_thr.start()

    def start(self) -> None:
        self._calc_thr.run_calc()

    def stop(self) -> None:
        self._calc_thr.stop_calc()

    def clear(self) -> None:
        if self._calc_thr:
            self._calc_thr.reset_spectrum()
        else:
            self._lib.tccfcalc_reset_spectrum()

    def get_data(self) -> speparser.Spectrum:
        if not self._calc_thr:
            raise Exception("acquiring hasn't started yet")
        return self._calc_thr.get_spectrum()

    def is_running(self) -> bool:
        return self._calc_thr.is_running()

    def get_channels(self) -> int:
        return self._channels_num

    def delete_mca(self):
        self._calc_thr.stop_thread()


def _print_status(mca: EffCalcMCA) -> None:
    if not mca:
        print("acquiring hasn't started yet")
        return
    print(f"spectr is {'running' if mca.is_running() else 'stopped'}")
    spe = mca.get_data()
    print(f"spectr live time: {spe.info.tlive} s, {spe.info.tlive/60:.3} min")
    cps = sum(spe.data) / spe.info.tlive if spe.info.tlive != 0 else 0
    print(f"spectr load, cps: {cps}")


def read_channels(filename: str) -> int:
    """get analyzer channel number from tccfcalc.in"""
    with open(filename) as f:
        for line in f:
            if line.startswith("AN_N_ch"):
                words = line.strip().split('=')
                return int(words[1].strip())
    raise Exception("There is no analyzer in tccfcalc.in")


def main():
    parser = argparse.ArgumentParser(
        description='emulate_spectrum -- util for emulate spectrum acquiring with Monte-Carlo method')

    parser.add_argument('positional', help='element Z, A, M', nargs='*', type=int)

    parser.add_argument('-n', '--nuclide', help='nuclide as string, e.g. Co-60 or Cs-137m')
    parser.add_argument('-t', '--time', type=int, default=1, help='acquire time interval, s')
    parser.add_argument('-s', '--seed', help='seed for random generator, default = 0 <- random seed',
                        type=int, default=0)
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

    # nuclide
    if len(args.positional) not in (0, 3):
        raise ValueError('need 3 or 0 positional arguments')

    if len(args.positional) == 3:
        nuclide = Nuclide(*args.positional)
    else:
        if args.nuclide is not None:
            nuclide = Nuclide.parse_from(args.nuclide)
        else:
            nuclide = Nuclide.get_default()
    logging.info(nuclide)

    # other
    seed = args.seed
    activity = args.activity
    channels = read_channels("tccfcalc.in")

    # command interface
    mca: tp.Optional[IMCA] = None
    while True:
        cmd = input("Enter command: ").strip()
        if cmd in ("quit", "exit"):
            if mca:
                mca.delete_mca()
            break
        elif cmd in ("prepare", "init"):
            mca = EffCalcMCA(nuclide, channels, seed, activity, 1)
        elif cmd == "start":
            mca.start()
        elif cmd == "stop":
            mca.stop()
        elif cmd == "clear":
            mca.clear()
        elif cmd == "status":
            _print_status(mca)
        else:
            print(f"unknown command {cmd}, avaliable commands: quit (exit), prepare (init), start, stop, clear, status")


if __name__ == "__main__":
    main()
