import os
import sys
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Make df
gdata = {}
rdata = {}

goodgreatlist = []

# READ PROCESSED BINNED DATA
dirname_proc = "/Users/danielmuthukrishna/Documents/Projects/sandbox/flux_uncertainty_distributions/processed_curves_good_great (7)/"
filenames_proc = os.listdir(dirname_proc)
data_proc_all_lcs = pd.DataFrame()

for i, filename in enumerate(filenames_proc):
    if not filename.endswith('.csv'):
        continue
    goodgreatlist.append(filename.split('_')[1])

    print(f"{i} of {len(filenames_proc)}")
    filepath = dirname_proc + filename
    data_proc = pd.read_csv(filepath)

    data_proc_all_lcs = data_proc_all_lcs.append(data_proc, ignore_index=True)

# --- Make processed only plot --- #
grid = sns.jointplot(data=data_proc_all_lcs, x='g_flux', y='g_uncert', kind='kde', ratio=2, height=8, fill=True, alpha=0.4)
grid.plot_joint(sns.kdeplot, fill=False, joint_kws={'line_kws': {'linewidth': 0.1}})
grid.savefig(f"flux_vs_fluxerr_proc.pdf")
# --- #


# READ RAW DATA
dirname_raw = "/Users/danielmuthukrishna/Documents/Projects/sandbox/Get_ZTF_TESS_lightcurves/forced_photometry_calibrated_lightcurves/"
filenames_raw = os.listdir(dirname_raw)
data_raw_all_lcs = pd.DataFrame()

for i, filename in enumerate(filenames_raw):
    if not filename.endswith('.csv'):
        continue

    if filename.split('_')[0] not in goodgreatlist:
        continue

    print(f"{i} of {len(filenames_raw)}")

    filepath = dirname_raw + filename
    data_raw = pd.read_csv(filepath)

    peaktime = data_raw['julian_date'][np.argmax(data_raw['flux'])]
    data_raw = data_raw[(data_raw['julian_date'] > (peaktime - 50)) & (data_raw['julian_date'] < (peaktime + 50))]

    data_raw_all_lcs = data_raw_all_lcs.append(data_raw, ignore_index=True)

# --- Make raw only plot --- #
data_raw_all_lcs['$\log_{10}$(Flux)'] = np.log10(data_raw_all_lcs['flux'])
data_raw_all_lcs['$\log_{10}$(Flux Uncertainty)'] = np.log10(data_raw_all_lcs['flux_unc'])
# grid = sns.jointplot(data=data_raw_all_lcs, x='flux', y='flux_unc', hue="filter", kind='kde', ratio=2, height=8, fill=True, alpha=0.4)
grid = sns.jointplot(data=data_raw_all_lcs, x='$\log_{10}$(Flux)', y='$\log_{10}$(Flux Uncertainty)', hue="filter", kind='hist', ratio=2, height=8, fill=True, alpha=0.4)
grid.plot_joint(sns.kdeplot, fill=False, joint_kws={'line_kws': {'linewidth': 0.1}})
grid.savefig(f"flux_vs_fluxerr_raw.pdf")
# --- #



# MAKE DATA ARRAY

# g-band raw
gdata_raw = data_raw_all_lcs[data_raw_all_lcs['filter'] == 'ZTF_g']
gdata['Flux'] = gdata_raw['flux']
gdata['Flux Uncertainty'] = gdata_raw['flux_unc']
gdata['$\log_{10}$(Flux)'] = np.log10(gdata_raw['flux'])
gdata['$\log_{10}$(Flux Uncertainty)'] = np.log10(gdata_raw['flux_unc'])
gdata[f"g-band"] = ["raw"] * len(gdata_raw['flux'])

# r-band raw
rdata_raw = data_raw_all_lcs[data_raw_all_lcs['filter'] == 'ZTF_r']
rdata['Flux'] = rdata_raw['flux']
rdata['Flux Uncertainty'] = rdata_raw['flux_unc']
rdata['$\log_{10}$(Flux)'] = np.log10(rdata_raw['flux'])
rdata['$\log_{10}$(Flux Uncertainty)'] = np.log10(rdata_raw['flux_unc'])
rdata[f"r-band"] = ["raw"] * len(rdata_raw)

# g-band proc
gdata['Flux'] = np.append(gdata['Flux'], data_proc_all_lcs['g_flux'])
gdata['Flux Uncertainty'] = np.append(gdata['Flux Uncertainty'], data_proc_all_lcs['g_uncert'])
gdata['$\log_{10}$(Flux)'] = np.append(gdata['$\log_{10}$(Flux)'], np.log10(data_proc_all_lcs['g_flux']))
gdata['$\log_{10}$(Flux Uncertainty)'] = np.append(gdata['$\log_{10}$(Flux Uncertainty)'], np.log10(data_proc_all_lcs['g_uncert']))
gdata[f"g-band"] = np.append(gdata[f"g-band"], ["processed"] * len(data_proc_all_lcs['g_flux']))

# r-band proc
rdata['Flux'] = np.append(rdata['Flux'], data_proc_all_lcs['r_flux'])
rdata['Flux Uncertainty'] = np.append(rdata['Flux Uncertainty'], data_proc_all_lcs['r_uncert'])
rdata['$\log_{10}$(Flux)'] = np.append(rdata['$\log_{10}$(Flux)'], np.log10(data_proc_all_lcs['r_flux']))
rdata['$\log_{10}$(Flux Uncertainty)'] = np.append(rdata['$\log_{10}$(Flux Uncertainty)'], np.log10(data_proc_all_lcs['r_uncert']))
rdata[f"r-band"] = np.append(rdata[f"r-band"], ["processed"] * len(data_proc_all_lcs['r_flux']))

for histkind in ('kde', 'hist'):
    gdata = pd.DataFrame(gdata)
    grid = sns.jointplot(data=gdata, x='$\log_{10}$(Flux)', y='$\log_{10}$(Flux Uncertainty)', hue="g-band",kind=histkind, ratio=2, height=8, fill=True, alpha=0.4, xlim=(-1.5, 4), ylim=(1, 2.5))
    grid.plot_joint(sns.kdeplot, fill=False, joint_kws={'line_kws': {'linewidth': 0.1}})
    grid.savefig(f"logflux_vs_fluxerr_gband_{histkind}.pdf")

    rdata = pd.DataFrame(rdata)
    grid = sns.jointplot(data=rdata, x='$\log_{10}$(Flux)', y='$\log_{10}$(Flux Uncertainty)', hue="r-band",kind=histkind, ratio=2, height=8, fill=True, alpha=0.4, xlim=(-1.5, 4), ylim=(1, 2.5))
    grid.plot_joint(sns.kdeplot, fill=False, joint_kws={'line_kws': {'linewidth': 0.1}})
    grid.savefig(f"logflux_vs_fluxerr_rband_{histkind}.pdf")

    gdata = pd.DataFrame(gdata)
    grid = sns.jointplot(data=gdata, x='Flux', y='Flux Uncertainty', hue="g-band", kind=histkind, ratio=2, height=8, fill=True, alpha=0.4, xlim=(-1000, 4000), ylim=(0, 200))
    grid.plot_joint(sns.kdeplot, fill=False, joint_kws={'line_kws': {'linewidth': 0.1}})
    grid.savefig(f"flux_vs_fluxerr_gband_{histkind}.pdf")

    rdata = pd.DataFrame(rdata)
    grid = sns.jointplot(data=rdata, x='Flux', y='Flux Uncertainty', hue="r-band", kind=histkind, ratio=2, height=8, fill=True, alpha=0.4, xlim=(-1000, 4000), ylim=(0, 200))
    grid.plot_joint(sns.kdeplot, fill=False, joint_kws={'line_kws': {'linewidth': 0.1}})
    grid.savefig(f"flux_vs_fluxerr_rband_{histkind}.pdf")



plt.show()






"""
# Plot Mag vs Magerr Joint plot...
import matplotlib
font = {'family': 'normal',
        'size': 16}
matplotlib.rc('font', **font)

import pandas as pd
import seaborn as sns
sns.set_style('white')


plot_kind = 'kde'

for pb in passbands:
    data1 = {}
    data2 = {}
    data3 = {}
    for lcdictname in lc_dict_names[0:2]:
        flux_peaks = np.array(save_fluxes_peaks[lcdictname][pb])
        fluxerr_peaks = np.array(save_fluxerrs_peaks[lcdictname][pb])
        fluxes = np.array(save_fluxes[lcdictname][pb])
        fluxerrs = np.array(save_fluxerrs[lcdictname][pb])
        redshifts = np.array(save_redshifts[lcdictname][pb])
        print(len(fluxes), len(fluxerrs), lcdictname)

    # Plot flux vs flux err
    lcdictname = 'ZTF sims SNIa'
    fluxes = np.log10(np.array(save_fluxes[lcdictname][pb]))
    fluxerrs = np.log10(np.array(save_fluxerrs[lcdictname][pb]))
    data1['$\log_{10}$(Flux)'] = fluxes
    data1['$\log_{10}$(Flux Uncertainty)'] = fluxerrs
    data1[f"${pb}$-band"] = [f"{lcdictname}"]*len(fluxes)
    lcdictname = 'ZTF real data SNIa'
    fluxes = np.log10(save_fluxes[lcdictname][pb])
    fluxerrs = np.log10(save_fluxerrs[lcdictname][pb])
    data1['$\log_{10}$(Flux)'] = np.append(data1['$\log_{10}$(Flux)'], fluxes)
    data1['$\log_{10}$(Flux Uncertainty)'] = np.append(data1['$\log_{10}$(Flux Uncertainty)'], fluxerrs)
    data1[f"${pb}$-band"] = np.append(data1[f"${pb}$-band"], [f"{lcdictname}"]*len(fluxes))
    data1 = pd.DataFrame(data1)
    grid = sns.jointplot(data=data1, x='$\log_{10}$(Flux)', y='$\log_{10}$(Flux Uncertainty)', hue=f"${pb}$-band", kind=plot_kind, ratio=2, height=8, xlim=(1.9, 4.5), ylim=(1.4, 3), fill=True, alpha=0.4)
    grid.plot_joint(sns.kdeplot, fill=False, joint_kws={'line_kws': {'linewidth': 0.1}})
    grid.savefig(f"mag_vs_magerr_zpt26point2_detections_{pb}_jointplot_{plot_kind}.pdf")

    # Plot peak flux vs peak flux err 
    lcdictname = 'ZTF sims SNIa'
    flux_peaks = np.log10(np.array(save_fluxes_peaks[lcdictname][pb]))
    fluxerr_peaks = np.log10(np.array(save_fluxerrs_peaks[lcdictname][pb]))
    data2['$\log_{10}$(Peak Flux)'] = flux_peaks
    data2['$\log_{10}$(Peak Flux Uncertainty)'] = fluxerr_peaks
    data2[f"${pb}$-band"] = [f"{lcdictname}"]*len(flux_peaks)
    lcdictname = 'ZTF real data SNIa'
    flux_peaks = np.log10(save_fluxes_peaks[lcdictname][pb])
    fluxerr_peaks = np.log10(np.array(save_fluxerrs_peaks[lcdictname][pb]))
    data2['$\log_{10}$(Peak Flux)'] = np.append(data2['$\log_{10}$(Peak Flux)'], flux_peaks)
    data2['$\log_{10}$(Peak Flux Uncertainty)'] = np.append(data2['$\log_{10}$(Peak Flux Uncertainty)'], fluxerr_peaks)
    data2[f"${pb}$-band"] = np.append(data2[f"${pb}$-band"], [f"{lcdictname}"]*len(flux_peaks))
    data2 = pd.DataFrame(data2)
    grid = sns.jointplot(data=data2, x='$\log_{10}$(Peak Flux)', y='$\log_{10}$(Peak Flux Uncertainty)', hue=f"${pb}$-band", kind=plot_kind, ratio=2, height=8, xlim=(1.9, 4.5), ylim=(1.4, 3), fill=True, alpha=0.4)
    grid.plot_joint(sns.kdeplot, fill=False, line_kws={'linewidth': 0.1})
    grid.savefig(f"peakmag_vs_peakmagerr_zpt26point2_peak_detections_{pb}_jointplot_{plot_kind}.pdf")


    #Plot peak flux vs redshift
    lcdictname = 'ZTF sims SNIa'
    redshifts = np.array(save_redshifts[lcdictname][pb])
    flux_peaks = np.log10(np.array(save_fluxes_peaks[lcdictname][pb]))
    data3['Redshift'] = redshifts
    data3['$\log_{10}$(Peak Flux)'] = flux_peaks
    data3[f"${pb}$-band"] = [f"{lcdictname}"]*len(redshifts)
    lcdictname = 'ZTF real data SNIa'
    redshifts = np.array(save_redshifts[lcdictname][pb])
    flux_peaks = np.log10(np.array(save_fluxes_peaks[lcdictname][pb]))
    data3['Redshift'] = np.append(data3['Redshift'], redshifts)
    data3['$\log_{10}$(Peak Flux)'] = np.append(data3['$\log_{10}$(Peak Flux)'], flux_peaks)
    data3[f"${pb}$-band"] = np.append(data3[f"${pb}$-band"], [f"{lcdictname}"]*len(redshifts))
    data3 = pd.DataFrame(data3)
    grid = sns.jointplot(data=data3, x='Redshift', y='$\log_{10}$(Peak Flux)', hue=f"${pb}$-band", kind=plot_kind, ratio=2, height=8, xlim=(0, 0.25), ylim=(1.9, 4.5),  fill=True, alpha=0.4)
    grid.plot_joint(sns.kdeplot, fill=False, linewidth=0.1)
    grid.savefig(f"peakmag_vs_redshift_zpt26point2_detections_{pb}_jointplot_{plot_kind}.pdf")
    


    plt.show()
    """