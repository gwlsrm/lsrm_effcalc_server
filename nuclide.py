_ELEMENT_NAMES = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
                  "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn",
                  "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y",
                  "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I",
                  "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho",
                  "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl",
                  "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am",
                  "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Ku"]

_NAME_TO_Z = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
    "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18, "K": 19, "Ca": 20,
    "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25, "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30,
    "Ga": 31, "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36, "Rb": 37, "Sr": 38, "Y": 39, "Zr": 40,
    "Nb": 41, "Mo": 42, "Tc": 43, "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48, "In": 49, "Sn": 50,
    "Sb": 51, "Te": 52, "I": 53, "Xe": 54, "Cs": 55, "Ba": 56, "La": 57, "Ce": 58, "Pr": 59, "Nd": 60,
    "Pm": 61, "Sm": 62, "Eu": 63, "Gd": 64, "Tb": 65, "Dy": 66, "Ho": 67, "Er": 68, "Tm": 69, "Yb": 70,
    "Lu": 71, "Hf": 72, "Ta": 72, "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79, "Hg": 80,
    "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85, "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90,
    "Pa": 91, "U": 92, "Np": 93, "Pu": 94, "Am": 95, "Cm": 96, "Bk": 97, "Cf": 98, "Es": 99, "Fm": 100,
    "Md": 101, "No": 102, "Lr": 103, "Ku": 104
}


class Nuclide:
    def __init__(self, z, a, m):
        self._z = z
        self._a = a
        self._m = m
        assert self.is_valid()

    def is_valid(self):
        return 0 < self._z <= 104 and 0 < self._a and self._z <= self._a and self._m >= 0

    @property
    def z(self):
        return self._z

    @property
    def a(self):
        return self._a

    @property
    def m(self):
        return self._m

    @property
    def name(self):
        return _ELEMENT_NAMES[self._z-1]

    def __str__(self):
        return f'nuclide: {self.name} {self._z}, {self._a}, {self._m}'

    def __eq__(self, __o: object) -> bool:
        return (self._z, self._a, self._m) == (__o._z, __o._a, __o._m)

    @staticmethod
    def parse_from(nuclide_string):
        if len(nuclide_string) < 3 or '-' not in nuclide_string:
            raise ValueError(f'Bad nuclide string: {nuclide_string}, waits "Co-60" like string')

        element, nuclide_string = nuclide_string.split('-')
        element = element.capitalize()

        if element not in _NAME_TO_Z:
            ValueError(f'Bad element: {element}')
        z = _NAME_TO_Z[element]

        if 'm' in nuclide_string:
            a, m = (int(w) for w in nuclide_string.split('m'))
        else:
            a, m = int(nuclide_string), 0
        return Nuclide(z, a, m)

    @staticmethod
    def get_default():
        return Nuclide(27, 290, 0)


def _test():
    n = Nuclide.parse_from('Co-60')
    expected = Nuclide(27, 60, 0)
    assert n == expected, f'{n} != {expected}'
    assert n.name == 'Co'

    n = Nuclide.parse_from('La-100m1')
    expected = Nuclide(57, 100, 1)
    assert n == expected, f'{n} != {expected}'
    assert n.name == 'La'


if __name__ == '__main__':
    _test()
