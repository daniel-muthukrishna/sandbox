import os
import numpy as np
import pandas as pd
from alerce.core import Alerce

data_list = pd.read_csv("/Users/danielmuthukrishna/Downloads/AT_count_transients_s1-47 (2).txt", delim_whitespace=True,
            names=("sector", "ra", "dec", "magnitude at discovery", "time of discovery in TESS JD", "SN",
                    "classification", "IAU name", "discovery survey", "cam", "ccd", "column", "row")
                        )

print(data_list)

row = data_list.iloc[43]

client = Alerce()
ra = row['ra']
dec = row['dec']
radius = 20
catalog_name = "GAIA/DR1"
xmatch_objects = client.catshtm_conesearch(ra,
                                dec,
                                radius,
                                format="pandas")
