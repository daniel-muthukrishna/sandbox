import os
import glob
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from helpers import get_ztf_data


# Read tns_info file
tns_info = pd.read_csv('tns_info2.csv', index_col='IAU_name')

# # Begin saving ztf request details
# with open('ztf_request_details.txt', 'w') as file:
#     file.write("iau_name,ztf_name,ra,dec,jd_discovery_date,jd_start,jd_end\n")

# TODO: If file is already saved don't resubmit request

for i, (iau_name, row) in enumerate(tns_info.iterrows()):
    row = get_ztf_data(row)
    print(i, iau_name)

    if row is None:# or glob.glob(f"forced_photometry_raw_data/raw_{iau_name}_{row['ztf_name']}*_lc.txt"):
        continue  # If file already exists (or if not ZTF data (row=None)), then skip over requesting again

    # Make request for forced photometry
    page = requests.get('https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi', auth=('ztffps', 'dontgocrazy!'),
                        params={'ra': row['ra'], 'dec': row['dec'],
                                'jdstart': row['jd_discovery_date'] - 250, 'jdend': row['jd_discovery_date'] + 250,
                                'email': 'danmuth@mit.edu', 'userpass': 'input_password'})

    ztf_request = pd.read_html(page.text)[0]
    print(i, ztf_request)

    # # Append request details to file
    # with open('ztf_request_details.txt', 'a') as file:
    #     file.write(f"{iau_name},{row['ztf_name']},{row['ra']},{row['dec']},{row['jd_discovery_date']},{ztf_request['jdstart'][0]},{ztf_request['jdend'][0]}\n")

    # if i > 100:
    #     break


