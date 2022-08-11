import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
import matplotlib.pyplot as plt


def get_ztf_data(row):
    if isinstance(row['internal_name'], str) and 'ZTF' in row['internal_name']:
        for alias in row['internal_name'].split('/'):
            if alias[0:3] == 'ZTF':
                row["ztf_name"] = alias
                break
    else:
        return None
    row["ra"] = row["ra"].split("/")[1]
    row["dec"] = row["dec"].split("/")[1]
    coords = SkyCoord(ra=row['ra'], dec=row['dec'], unit=(u.hourangle, u.deg))
    row["ra"] = coords.ra.value
    row["dec"] = coords.dec.value
    discovery_times = row["discovery_date"].split("/")
    ts_series = pd.Series([pd.Timestamp(time) for time in discovery_times])
    i = ts_series.idxmin()
    earliest_disc_time = ts_series[i]
    row["discovery_survey"] = row["discovery_survey"].split("/")[i]
    row["jd_discovery_date"] = earliest_disc_time.to_julian_date()
    return row


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx]


def make_plot(gtime, rtime, gflux, rflux, gfluxerr, rfluxerr, title, fpath):
    plt.figure()
    plt.errorbar(gtime, gflux, yerr=gfluxerr, fmt='.', color='g')
    plt.errorbar(rtime, rflux, yerr=rfluxerr, fmt='.', color='r')
    plt.title(title)
    plt.xlabel('Julian Date')
    plt.ylabel('Forced Difference Image PSF-fit Flux')
    plt.tight_layout()
    plt.savefig(fpath)
    # plt.show()


def make_plot_proccodes(lc, gmask, rmask, title, fpath, triggertime):
    pcode_marker = {'0': '.', '56': 'o', '57': 'v', '58': '^', '59': '<', '60': '>', '61': '*', '62': '+', '63': 'x', '64': '1', '65': 's'}

    fig = plt.figure()

    for procstatus in lc['procstatus'].unique():
        # print(lc['procstatus'].unique())

        marker = pcode_marker.get(str(procstatus), rf"${procstatus}$")

        procmask = (lc['procstatus'] == procstatus)
        g_lc = lc[gmask & procmask]
        r_lc = lc[rmask & procmask]
        plt.errorbar(g_lc['jd,'], g_lc['forcediffimflux,'], yerr=g_lc['forcediffimfluxunc,'], marker=marker, color='g', ls='none', label=procstatus)
        plt.errorbar(r_lc['jd,'], r_lc['forcediffimflux,'], yerr=r_lc['forcediffimfluxunc,'], marker=marker, color='r', ls='none')
        plt.axvline(triggertime, color="black", linestyle="--")
        plt.title(title)
        plt.xlabel('Julian Date')
        plt.ylabel('Forced Difference Image PSF-fit Flux')
        plt.legend()
        plt.tight_layout()
        plt.savefig(fpath)
    # plt.show()

    return fig


def get_pcodes(lc):
    pcodes = []
    for pcode in lc['procstatus'].unique():
        pcodes += pcode.split(',')
    pcodes = np.unique(pcodes)
    return pcodes

def read_html_lightcurve():
    return