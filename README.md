## Index
[Introduction](#Introduction)   
[Structure of Package](#Structure of Package)   
[how to use](#how to use)     
[Result](#Result)
***

## introduction
Our goal is to make the program compatible on all dies, not on one die. 

For running a program, just only 'run.py' file should make the program run. - Make each analysis step into a module and load it.
### contributors: If your have any questions,please contact us at the following email.

| name | e_mail | 
| --- | --- |
| 나유진 | [nayoujin2002@hanyang.ac.kr] |
| 창영곤 | [changyongkun@hanyang.ac.kr] |
| 박소연 | [psy030412@hanyang.ac.kr] |
| 박승우 | [seungwo7@hanyang.ac.kr] |




## Structure of Package

+ doc : .gitignore and README.md (explaining how to use our package)
+ src
   + flat_transmission： plot flatten wavelength sweep graph
   + ivcurve：Extract the current value at -1V on the IV graph and the current value at 1V on the IV graph. And draw the I-V relationship graph
   + pandas_frame：Extract spectral and IV data from multiple XML files, process and fit the data, and finally organize the processed data into a Pandas data frame
   + ref_transmission：Automatically process multiple XML files, extract spectral data, perform polynomial fits, generate corresponding graphs, and save these graphs as JPG files
   + requirements.txt
   + transmission：Automatically process multiple XML files, extract spectral data and generate corresponding graphs, and save these graphs as JPG files for subsequent analysis and use
+ .gitignore：Ignore unnecessary files
+ README：Documentation on development
+ run：main program

## how to use
### Library function required to execute code
```python
import os
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
import lmfit
import pandas as pd
import src.pandas_frame
import warnings
from   scipy.interpolate import UnivariateSpline
from   src.ivcurve import plot_iv_data
from   src.transmission import plot_transmission_spectra_all
from   src.ref_transmission import plot_transmission_spectra
from   src.flat_transmission import plot_flat_transmission_spectra
```
***

## Result

![img.png](img.png)