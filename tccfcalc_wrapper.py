import os.path
import sys
import typing as tp
from ctypes import CDLL, RTLD_GLOBAL, c_int, c_double, c_char_p


PREPARE_ERROR_CODES = [
    "",
    "Memory allocation error.",
    "Unable to load Photon Attenuation Library files.",
    "No GLECS database.",
    "Could not find ECCBINDX.BIN data file.",
    "TCCFCALC.IN file not found.",
    "Incorrect input geometry or material data",
    "No ENSDF data found for the specified A, Z and M.",
    "There is no valid record in ENSDF data library.",
    "ENSDF: Normalization record is not complete.",
    "Could not find ICC.BIN data file.",
    "No X- or gamma-rays are emitted by the source.",
    "No EPDL97 library",
    "No Ttb library",
    "No Elib library",
    "Bad input json file",
    "Error while parsing input json file",
    "Error while parsing detector from input json file",
    "Error while parsing source, nuclide or ContainerSource from input json file",
    "Error while parsing calc_params from input json file",
]


def get_prepare_error_message(error_code: int) -> str:
    return PREPARE_ERROR_CODES[error_code] if error_code < len(PREPARE_ERROR_CODES) else ''


def _get_attribute(lib, attributes: tp.List[str]) -> tp.Any:
    """
        tries to get exported attribute from attributes list
        returns first successful
    """
    for attribute in attributes:
        try:
            res = getattr(lib, attribute)
            return res
        except AttributeError:
            continue
    raise AttributeError('Cannot find good symbol from ' + str(attributes))


class TccFcalcDllWrapper:
    def __init__(self, path_to_dll: tp.Optional[str] = None, lib_name: tp.Optional[str] = None) -> None:
        if path_to_dll is None:
            path_to_dll = os.getcwd()
        if lib_name is None:
            lib_name = self._auto_select_lib_name(path_to_dll)
        self._lib = CDLL(os.path.join(path_to_dll, lib_name), RTLD_GLOBAL)
        # prepare
        self._tccfcalc_prepare = _get_attribute(self._lib, ['TCCFCALC_Prepare@24', 'TCCFCALC_Prepare'])
        self._tccfcalc_prepare.argtypes = [c_int, c_int, c_int, c_char_p, c_char_p, c_int]
        # prepare json
        self._tccfcalc_prepare_json = _get_attribute(self._lib, ['TCCFCALC_Prepare_Json@8', 'TCCFCALC_Prepare_Json'])
        self._tccfcalc_prepare_json.argtypes = [c_char_p, c_int]
        # calculate
        self._tccfcalc_calculate = _get_attribute(self._lib, ['TCCFCALC_Calculate@4', 'TCCFCALC_Calculate'])
        self._tccfcalc_calculate.argtypes = [c_int]
        # reset
        self._tccfcalc_reset = _get_attribute(self._lib, ['TCCFCALC_Reset@0', 'TCCFCALC_Reset'])
        # calc spectrum
        self._tccfcalc_calculate_spectrum = \
            _get_attribute(self._lib, ['TCCFCALC_CalculateSpectrum@8', 'TCCFCALC_CalculateSpectrum'])
        self._tccfcalc_calculate_spectrum.argtypes = [c_double]
        self._tccfcalc_calc_spectrum_file = \
            _get_attribute(self._lib, ['TCCFCALC_CalcSpectrumFile@12', 'TCCFCALC_CalcSpectrumFile'])
        self._tccfcalc_calc_spectrum_file.argtypes = [c_char_p, c_double]
        # calc spectrum n sec
        self._tccfcalc_calc_spectrum_n_sec = _get_attribute(self._lib, ['TCCFCALC_Calculate_n_sec@8', 'TCCFCALC_Calculate_n_sec'])
        self._tccfcalc_calc_spectrum_n_sec.argtypes = [c_int, c_double]
        # reset spectrum
        self._tccfcalc_reset_spectrum = _get_attribute(self._lib, ['TCCFCALC_Reset_Spectrum@0', 'TCCFCALC_Reset_Spectrum'])

    @staticmethod
    def _auto_select_lib_name(path_to_dll: str):
        for lib_name in ['tccfcalc.dll', 'libtccfcalc.dll', 'libtccfcalc.so']:
            if os.path.exists(os.path.join(path_to_dll, lib_name)):
                return lib_name
        raise AttributeError(f'cannot find tccfcalc library in {path_to_dll}')

    def tccfcalc_prepare(self, a: int, z: int, m, cur_path: str, library_path: str, seed: int = 0) -> int:
        return self._tccfcalc_prepare(a, z, m, bytes(cur_path, 'utf-8'), bytes(library_path, 'utf-8'), seed)

    def tccfcalc_prepare_json(self, input_filename: str, seed: int) -> int:
        return self._tccfcalc_prepare_json(bytes(input_filename, 'utf-8'), seed)

    def tccfcalc_calculate(self, histories: int) -> None:
        return self._tccfcalc_calculate(histories)

    def tccfcalc_reset(self) -> None:
        self._tccfcalc_reset()

    def tccfcalc_calc_spectrum_file(self, analyzer_filename: str, activity: float) -> int:
        return self._tccfcalc_calc_spectrum_file(bytes(analyzer_filename, 'utf-8'), activity)

    def tccfcalc_calculate_spectrum(self, activity: float) -> int:
        return self._tccfcalc_calculate_spectrum(activity)

    def tccfcalc_calc_spectrum_n_sec(self, time_sec: int, activity: float) -> int:
        return self._tccfcalc_calc_spectrum_n_sec(time_sec, activity)

    def tccfcalc_reset_spectrum(self) -> None:
        return self._tccfcalc_reset_spectrum()


def main():
    cur_path = os.getcwd()
    cur_lib_path = os.path.join(cur_path, 'Lib')
    lib = TccFcalcDllWrapper()
    error_num = lib.tccfcalc_prepare(290, 27, 0, cur_path, cur_lib_path, 42)
    if error_num:
        error_msg = PREPARE_ERROR_CODES[error_num] if error_num < len(PREPARE_ERROR_CODES) else ''
        print(f'Prepare error #{error_num}: {error_msg}')
        sys.exit()

    for _ in range(1000):
        lib.tccfcalc_calculate(1000)
    print('done')


if __name__ == '__main__':
    main()
