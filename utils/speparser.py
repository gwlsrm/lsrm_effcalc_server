"""LSRM *.spe parser """
import os.path
import struct
import sys
import typing as tp
from dataclasses import dataclass, field

import numpy as np


def _str_to_float_def(string, defValue = 0.0):
    try:
        return float(string)
    except:
        return defValue


@dataclass
class SpectrumInformation:
    """Information about spectrum"""
    name: str = ""
    tlive: float = 0.0
    treal: float = 0.0
    geometry: str = ""
    distance: float = 0.0
    headerdict: tp.Dict[str, tp.Any] = field(default_factory=dict)

    def print_params(self):
        for key,value in self.headerdict.items():
            if value:
                print(key, value, sep = '=')
            else:
                print(key)


class Spectrum:
    """contains spectrum and spectrum information"""
    def __init__(self, data: tp.Optional[np.ndarray] = None, info: tp.Optional[SpectrumInformation] = None) -> None:
        self.data = data if data is not None else np.array([], dtype=int)
        self.info = info if info is not None else SpectrumInformation()


class SpectrumReader:
    @staticmethod
    def parse_spe(spe_fname: str) -> Spectrum:
        spe_info = SpectrumInformation()
        with open(spe_fname, 'rb') as f:
            # read header
            parname = ''
            while parname != "SPECTR":
                parname, parvalue = SpectrumReader.readline(f)
                if parname == "SHIFR":
                    spe_info.name = parvalue
                elif parname == "TLIVE":
                    spe_info.tlive = _str_to_float_def(parvalue)
                elif parname == "TREAL":
                    spe_info.treal = _str_to_float_def(parvalue)
                elif parname == "GEOMETRY":
                    spe_info.geometry = parvalue
                elif parname == "DISTANCE":
                    spe_info.distance = _str_to_float_def(parvalue)
                if parname != "SPECTR" and parvalue:
                    spe_info.headerdict[parname] = parvalue

            # read binary data
            i = f.read(4)
            spectrum_list = []
            while len(i) > 3:
                x = struct.unpack("i", i)[0]
                spectrum_list.append(x)
                i = f.read(4)
            spectr_data = np.array(spectrum_list, dtype=int)
        return Spectrum(spectr_data, spe_info)

    @staticmethod
    def readline(f) -> tp.Tuple[str, tp.Optional[str]]:
        c = ''
        param_name = ''
        param_value = ''
        is_has_value = False
        while c != '\r':
            b = f.read(1)
            c = b.decode(encoding="cp1251")

            if c == '\r':
                f.read(1) # reading \n
                if is_has_value:
                    return param_name, param_value
                else:
                    return param_name, None
            elif c == '=' and param_name == "SPECTR": # start of spectr section
                return param_name, None
            elif c == '=':
                is_has_value = True
            else:
                if is_has_value:
                    param_value += c
                else:
                    param_name += c


def save_spectrum_as_txt(spectrum: Spectrum, filename: str) -> None:
    with open(filename, "w") as f:
        # write header
        f.write('SHIFR=' + spectrum.info.name + '\n')
        f.write('TLIVE=' + str(spectrum.info.tlive) + '\n')
        f.write('TREAL=' + str(spectrum.info.treal) + '\n')
        if 'MEASBEGIN' in spectrum.info.headerdict:
            f.write('DATE=' + (spectrum.info.headerdict['MEASBEGIN'].split(" "))[0] + '\n')
            f.write('TIME=' + (spectrum.info.headerdict['MEASBEGIN'].split(" "))[1] + '\n')

        #write spectr head
        f.write("SPECTRTXT=" + str(len(spectrum.data)) + '\n')

        # writing spectr
        for i, x in enumerate(spectrum.data):
            f.write(str(i+1) + '\t' + str(x) + '\n')


def _get_output_filename(input_filename: str):
    filename, _ = os.path.splitext(input_filename)
    return filename + '.txt'


def main():
    """example for reading spe-file and converting it to txt"""
    if len(sys.argv) < 2:
        sys.exit()

    spe_filename = sys.argv[1]
    spectrum = SpectrumReader().parse_spe(spe_filename)
    save_spectrum_as_txt(spectrum, _get_output_filename(spe_filename))


if __name__ == "__main__":
    main()
