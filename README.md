# Lsrm effcalc server

Lsrm effcalc sever is the virtual MCA (multi-channel analyzer) for SpectraLine. It accepts commands from SpectraLine by tcp (start, stop spectrum acquiring, clear spectrum, ...) and starts Monte-Carlo calculation using tccfcalc.dll from EffCalcMC (NuclideMasterPlus).

## How to use

### installation
- copy code
- install dependencies: `pip install -r requirements.txt`
- copy `tccfcalc.dll` and `Lib` from installed [EffCalcMC](http://lsrm.ru/en/products/detail.php?ELEMENT_CODE=nuclidemasterplus)
- copy `lmca_LsrmEthernet.dll` to SpectraLineXX\MCA

### usage
- run lsrm-server: `python main.py -n Co-60 -v`
- run SpectraLine
- select lsrmEthernet MCA: `127.0.0.1:23, effcalc_mca`
- manage MCA in SpectraLine as usual
- ctrl+break (windows), ctrl+c (linux) to exit

### command parameters
run  `python main.py --help` to see all command line parameters
To change detector or source, edit tccfcalc.in
