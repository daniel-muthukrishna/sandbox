import os
import numpy as np
import pandas as pd
from alerce.core import Alerce

alerce = Alerce()

# Get list of ZTF IDs
tns_info = pd.read_csv('/Users/danielmuthukrishna/Documents/Projects/Fausnaugh_lightcurves/tns_info2.csv')

ztf_names = []
iau_names = []
for i, row in tns_info.iterrows():
    aliases = row['internal_name']
    if isinstance(aliases, str) and 'ZTF' in aliases:
        for alias in aliases.split('/'):
            if alias[0:3] == 'ZTF':
                ztf_id = alias
                break
        ztf_names.append(ztf_id)
        iau_names.append(row['IAU_name'])

# pd.DataFrame(ztf_names).to_csv('ztf_ids.txt', index=False)

for i, ztf_id in enumerate(ztf_names):
    print(i, iau_names[i], ztf_names[i])
    try:
        # Getting detections and non-detections for an object
        detections = alerce.query_detections(ztf_id, format="pandas")
        non_detections = alerce.query_non_detections(ztf_id, format="pandas")

        detections.to_csv(f"ztf_data/{iau_names[i]}_{ztf_names[i]}_detections.csv")
        detections.to_csv(f"ztf_data/{iau_names[i]}_{ztf_names[i]}_non_detections.csv")
    except Exception as e:
        print(e)
        print(f"Object {iau_names[i]} {ztf_names[i]} failed")



