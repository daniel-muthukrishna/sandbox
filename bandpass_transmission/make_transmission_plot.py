"""
Data from:
http://svo2.cab.inta-csic.es/theory/fps/index.php?id=TESS/TESS.Red&&mode=browse&gname=TESS&gname2=TESS#filter
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

font = {'family' : 'normal',
        'size'   : 15}

matplotlib.rc('font', **font)

plt.figure(figsize=(8,3.5))
g_band = pd.read_csv("Palomar_ZTF.g.dat", names=('wavelength', 'transmission'), delim_whitespace=True)
r_band = pd.read_csv("Palomar_ZTF.r.dat", names=('wavelength', 'transmission'), delim_whitespace=True)
tess_band = pd.read_csv("TESS_TESS.Red.dat", names=('wavelength', 'transmission'), delim_whitespace=True)

plt.plot(g_band['wavelength'], g_band['transmission'], color='tab:blue', label='ZTF g')
plt.plot(r_band['wavelength'], r_band['transmission'], color='tab:red', label='ZTF r')
plt.plot(tess_band['wavelength'], tess_band['transmission'], color='black', label='TESS')

plt.fill_between(g_band['wavelength'], g_band['transmission'], color='tab:blue', alpha=0.4)
plt.fill_between(r_band['wavelength'], r_band['transmission'], color='tab:red', alpha=0.4)
plt.fill_between(tess_band['wavelength'], tess_band['transmission'], color='black', alpha=0.17)

plt.xlabel("Wavelength (Angstroms)")
plt.ylabel("Transmission")
plt.legend()
plt.tight_layout()
plt.savefig("ZTF_TESS_bands_transmission.pdf")
plt.show()
