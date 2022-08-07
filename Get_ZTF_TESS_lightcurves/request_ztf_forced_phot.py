import os
import glob
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from helpers import get_ztf_data


# Read tns_info file
tns_info = pd.read_csv('tns_info2.csv', index_col='IAU_name')

# # Do Great, Good, and Maybe light curves first:
# good_lcs = np.array(['2018kfv','2018koy','2018kwm','2018lot','2019tfd','2020amv','2020amx','2020aoi','2020bj','2020fcw','2020ftl','2020ut','2021aesq','2021agfq','2021aggu','2021zny','2022eat','2022ik','2018fzi','2018grv','2018gxi','2018hgl','2018hka','2018hkb','2018hxq','2018hyy','2018itr','2018iyx','2018izg','2018jeb','2018jjs','2018jnd','2018jwh','2018ksr','2018kvc','2019aba','2019axj','2019bip','2019cxt','2019dhz','2019dke','2019dsn','2019fp','2019mdw','2019nvk','2019nvl','2019ook','2019pny','2019prm','2019prs','2019ptf','2019qhh','2019qmt','2019qqr','2019rrc','2019ruc','2019ruf','2019rvx','2019soh','2019tfa','2019tjz','2019uen','2019uge','2019ugr','2019ujw','2019ulr','2019ulw','2019uyn','2019vli','2019vlu','2019vyj','2019wjl','2019wla','2019wle','2019wz','2019xaq','2019xul','2019zam','2019zes','2020aan','2020aarw','2020aatb','2020aauh','2020aawh','2020abq','2020abqy','2020abrp','2020abvc','2020abxl','2020acbc','2020acdk','2020adff','2020adw','2020aek','2020ayw','2020bew','2020biz','2020bjj','2020bob','2020buv','2020bw','2020bza','2020bzd','2020bzv','2020cc','2020cdj','2020chi','2020clr','2020cmv','2020csx','2020cxe','2020dgc','2020dts','2020eee','2020flg','2020hdw','2020ht','2020hu','2020hye','2020hyh','2020jjk','2020kq','2020kt','2020kzp','2020kzr','2020lls','2020M','2020mga','2020nle','2020nxh','2020rub','2020tap','2020vbs','2020yef','2020yvf','2020yzv','2020yzw','2020zo','2021aanc','2021abbl','2021aboy','2021abyl','2021abzi','2021acpd','2021adad','2021adfs','2021aerh','2021aesb','2021afvp','2021afzz','2021agau','2021agji','2021agqe','2021agrt','2021amn','2021asu','2021aub','2021bpn','2021bpo','2021bxo','2021epv','2021gkb','2021htd','2021hup','2021hvp','2021sfh','2021ucq','2021uef','2021uhz','2021wly','2021zoj','2021zr','2022adv','2022aji','2022ajw','2022bdu','2022bii','2022bjn','2022blw','2022bmc','2022dbs','2022dma','2022dyu','2022eja','2022fw','2022mo','2022re','2018ijn','2018ime','2018iti','2018iwg','2018iyh','2018lit','2019aeu','2019bop','2019bwo','2019bwu','2019bxi','2019nnr','2019nzq','2019onn','2019opz','2019osp','2019pac','2019pzj','2019rdl','2019rj','2019slt','2019sql','2019str','2019sts','2019swy','2019sxc','2019sxe','2019tta','2019ubi','2019udn','2019ufy','2019uje','2019ujq','2019uwj','2019wkz','2019xar','2019xcn','2019zsi','2020aajf','2020aalz','2020aawi','2020abtd','2020abwb','2020acbf','2020accz','2020acmr','2020aczd','2020adbn','2020ael','2020amw','2020bja','2020bqr','2020brq','2020bvg','2020chm','2020cmb','2020cms','2020dkk','2020drk','2020dvf','2020dya','2020euy','2020eyb','2020eyf','2020fwi','2020hdh','2020hgw','2020hln','2020hp','2020ish','2020jjf','2020jjh','2020jsn','2020kbl','2020kn','2020ks','2020mfe','2020nnd','2020oii','2020uba','2020uve','2020uvg','2020uwl','2020wap','2020wpq','2020xit','2020yhg','2020ymv','2020yst','2020yu','2020zgr','2020zhg','2021aafd','2021aaxr','2021acet','2021acqi','2021actc','2021addk','2021adgt','2021adgx','2021afvj','2021aik','2021bmc','2021cfp','2021dic','2021dsb','2021hsg','2021isy','2021jui','2021sip','2021slm','2021vhz','2021vll','2021vtv','2021vzh','2021xts','2021xvg','2021xxn','2021xzf','2021yaz','2021ycy','2021yeu','2022abd','2022aee','2022ahq','2022bkf','2022cag','2022ced','2022cij','2022cou','2022cox','2022cvf','2022dvr','2022eaz','2022emd','2022erx','2022eti','2022fdw'])
# tns_info = tns_info.loc[good_lcs]

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
                                'email': 'danmuth@mit.edu', 'userpass': 'htdn483'})

    ztf_request = pd.read_html(page.text)[0]
    print(i, ztf_request)

    # # Append request details to file
    # with open('ztf_request_details.txt', 'a') as file:
    #     file.write(f"{iau_name},{row['ztf_name']},{row['ra']},{row['dec']},{row['jd_discovery_date']},{ztf_request['jdstart'][0]},{ztf_request['jdend'][0]}\n")

    # if i > 100:
    #     break


