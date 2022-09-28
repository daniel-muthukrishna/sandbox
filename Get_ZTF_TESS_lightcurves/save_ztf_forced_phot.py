import os
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
import matplotlib.pyplot as plt
from helpers import make_plot_proccodes


# Get list of saved requests
saved_ztf_request_details = pd.read_csv('ztf_request_details.txt')
saved_catalog_coords = SkyCoord(ra=saved_ztf_request_details['ra']*u.degree, dec=saved_ztf_request_details['dec']*u.degree)


# Get list of all forced phot requests from ztf server
page = requests.get('https://ztfweb.ipac.caltech.edu/cgi-bin/getForcedPhotometryRequests.cgi', auth=('ztffps', 'dontgocrazy!'), params={'email': 'danmuth@mit.edu', 'userpass': 'htdn483', 'option': 'All recent jobs', 'action': 'Query Database'})

# Get list of lightcurve HTML file locations
ztf_requests = pd.read_html(page.text)


# Save html lightcurve file
for i, row in ztf_requests[0].iterrows():
    print(f"{i} of {len(ztf_requests[0])}")
    # Find nearest object from ztf catalog requests
    coord = SkyCoord(ra=row['ra']*u.degree, dec=row['dec']*u.degree)
    index, dist2d, dist3d = coord.match_to_catalog_sky(saved_catalog_coords)
    # print(index, dist2d.value[0], dist3d.value)
    # print(ztf_request_details.iloc[index])

    saved_catalog_match = saved_ztf_request_details.iloc[index]
    # print(saved_catalog_match['iau_name'])
    # if saved_catalog_match['iau_name'] != '2018grv':
    #     continue

    if (dist2d.value[0] < 1 and int(row['startJD']) == int(saved_catalog_match['jd_start']) and int(row['endJD']) == int(saved_catalog_match['jd_end'])):
        # Check if file already processed
        save_fpath = f"forced_photometry_raw_data/raw_{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']}_exitcode{int(row['exitcode'])}_lc.txt"
        if os.path.exists(save_fpath):
            continue

        # Read HTML light curve
        lc_url = f"https://ztfweb.ipac.caltech.edu{row['lightcurve']}"
        lc_page = requests.get(lc_url, auth=('ztffps', 'dontgocrazy!'))

        # Save HTML light curve to file
        with open(save_fpath, 'w') as file:
            file.write(lc_page.text)

        # Read light curve
        print(save_fpath)
        lc = pd.read_csv(save_fpath, comment='#', delim_whitespace=True)

        # SANITY CHECKS #

        # Check for bad exit codes
        assert row['exitcode'] not in [63, 64, 255]

        # Check that the reference image duration not in transient period
        triggertime = saved_catalog_match['jd_discovery_date'] - 10
        if not (np.all(lc['refjdstart,'] < triggertime) and np.all(lc['refjdend,'] < triggertime)):
            badrefmask = ((lc['refjdstart,'] > triggertime) | (lc['refjdend,'] > triggertime))

            for fieldnum in lc['field,'].unique():
                fieldmask = (lc['field,'] == fieldnum)

                # Plot lightcurves in each field before calibration
                fig = make_plot_proccodes(lc=lc,
                                          gmask=(lc['filter,'] == 'ZTF_g') & (lc['field,'] == fieldnum),
                                          rmask = (lc['filter,'] == 'ZTF_r') & (lc['field,'] == fieldnum),
                                          title=f"{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']}_field{fieldnum}",
                                          fpath=f"forced_photometry_plots_baselines/{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']}_exitcode{row['exitcode']}_field{fieldnum}_lc.pdf",
                                          triggertime=saved_catalog_match['jd_discovery_date'])

                for filt in ['ZTF_g', 'ZTF_r']:
                    filtmask = (lc['filter,'] == filt)

                    # Shade reference image region
                    ax = fig.gca()
                    ax.axvspan(lc[fieldmask & filtmask]['refjdstart,'].max(), lc[fieldmask & filtmask]['refjdend,'].min(), facecolor='black', alpha=0.2, label='ref images')
                    fig.savefig(f"forced_photometry_plots_baselines/{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']}_exitcode{row['exitcode']}_field{fieldnum}_lc.pdf")

                    # Calibrate baseline correction of bad field filter lcs
                    if not lc[badrefmask & fieldmask & filtmask].empty:
                        pretriggermask = (lc[fieldmask & filtmask]['jd,'] < triggertime) | (lc[fieldmask & filtmask]['jd,'] > triggertime + 100)
                        if np.any(pretriggermask):
                            baseline = np.nanmedian(lc[fieldmask & filtmask & pretriggermask]['forcediffimflux,'])
                            lc.loc[(fieldmask & filtmask), 'forcediffimflux,'] = (lc.loc[(fieldmask & filtmask), 'forcediffimflux,'] - baseline)
                        else:
                            lc.loc[(fieldmask & filtmask), 'forcediffimflux,'] = np.nan
                            lc.loc[(fieldmask & filtmask), 'forcediffimfluxunc,'] = np.nan

                # Plot lightcurves in each field bad field after calibration
                if fieldnum in lc[badrefmask]['field,'].unique():
                    make_plot_proccodes(lc=lc,
                                        gmask=(lc['filter,'] == 'ZTF_g') & (lc['field,'] == fieldnum),
                                        rmask=(lc['filter,'] == 'ZTF_r') & (lc['field,'] == fieldnum),
                                        title=f"{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']}_field{fieldnum}_calibrated",
                                        fpath=f"forced_photometry_plots_baselines/{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']}_exitcode{row['exitcode']}_field{fieldnum}_calibrated_lc.pdf",
                                        triggertime=saved_catalog_match['jd_discovery_date'])

        # Check phot uncertainties
        for fieldnum in lc['field,'].unique():
            fieldmask = (lc['field,'] == fieldnum)
            for filt in ['ZTF_g', 'ZTF_r']:
                filtmask = (lc['filter,'] == filt)
                rms_chisq = np.sqrt(np.nanmean(np.square(lc.loc[(fieldmask & filtmask), 'forcediffimchisq,'])))
                median_chisq = np.nanmedian(lc.loc[(fieldmask & filtmask), 'forcediffimchisq,'])
                if (rms_chisq > 1.5 or rms_chisq < 0.5) and (median_chisq > 1.3 or median_chisq < 0.7):
                    print(f"WARNING: forcediffimchisq rms is {rms_chisq} and median is {median_chisq}. See section 11 of https://web.ipac.caltech.edu/staff/fmasci/ztf/forcedphot.pdf")
                    plt.hist(lc[fieldmask & filtmask]['forcediffimchisq,'], bins=100)
                    plt.xlabel(f"forcediffimchisq for field{fieldnum} {filt} and {saved_catalog_match['iau_name']}")
                    plt.savefig(f"forced_photometry_plots_baselines/{saved_catalog_match['iau_name']}_field{fieldnum}_{filt}.png")
                    # Fix uncertainty
                    lc.loc[(fieldmask & filtmask), 'forcediffimfluxunc,'] = np.sqrt(rms_chisq) * lc.loc[(fieldmask & filtmask), 'forcediffimfluxunc,']

        # Plot corrected light curves
        make_plot_proccodes(lc=lc,
                            gmask=(lc['filter,'] == 'ZTF_g'),
                            rmask=(lc['filter,'] == 'ZTF_r'),
                            title=f"{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']}",
                            fpath=f"forced_photometry_plots/{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']}_exitcode{row['exitcode']}_lc.pdf",
                            triggertime=saved_catalog_match['jd_discovery_date'])

        # Plot zeropoint distribution
        plt.figure()
        plt.hist(lc['zpdiff,'][lc['filter,'] == 'ZTF_r'], bins=100, color='red', alpha=0.4)
        plt.hist(lc['zpdiff,'][lc['filter,'] == 'ZTF_g'], bins=100, color='green', alpha=0.4)
        plt.xlabel('zero points')
        plt.title(f"{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']} \n zpt-median{round(np.nanmedian(lc['zpdiff,']), 3)}_zpt-std{round(np.nanstd(lc['zpdiff,']), 3)}")
        plt.savefig(f"forced_photometry_plots_baselines/{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']}_zpt-median{round(np.nanmedian(lc['zpdiff,']), 3)}_zpt-std{round(np.nanstd(lc['zpdiff,']), 3)}.png")
        print(np.median(lc['zpdiff,']))

        # Save corrected light curves to file
        lc.loc[:, ('jd,', 'filter,', 'forcediffimflux,', 'forcediffimfluxunc,', 'procstatus')].to_csv(f"forced_photometry_calibrated_lightcurves/{saved_catalog_match['iau_name']}_{saved_catalog_match['ztf_name']}_exitcode{row['exitcode']}.csv", header=('julian_date', 'filter', 'flux', 'flux_unc', 'proc_status_code'), index=False)

    else:
        print(f"Skipping object because it is not one of the requested light curves: {row['reqId']}")






# # Convert to magnitudes
# if lc['forcediffimflux,'] / lc['forcediffimfluxunc,'] > 3:
#     mag = lc['zpdiff,'] - 2.5*np.log10(lc['forcediffimflux,'])
#     magunc = 1.0857 * lc['forcediffimfluxunc,'] / lc['forcediffimflux,']
# else:
#     mag = lc['zpdiff,'] - 2.5*np.log10(5*lc['forcediffimfluxunc,'])
