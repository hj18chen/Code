from netCDF4 import Dataset
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
import xarray as xr
import pandas as pd

import sys
sys.path.insert(0, '/scratch/mp586/Code/PYCODES')
from plotting_routines_kav7 import *
import stats as st

GFDL_BASE = os.environ['GFDL_BASE']
sys.path.insert(0, os.path.join(GFDL_BASE,'src/extra/python/scripts'))
import cell_area as ca

ctl_model = 'isca'
if (ctl_model == 'Isca') or (ctl_model == 'isca'): 
    control_model = 'Isca_DATA'
elif (ctl_model == 'gfdl') or (ctl_model == 'GFDL'):
    control_model = 'GFDL_DATA'

HPC = 'yes'
control_dir = 'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387'
if (HPC == 'Yes') or (HPC == 'yes') or (HPC == 'y'):
    control_dir= control_model + '/ISCA_HPC/' + control_dir
else: 
    control_dir= control_model + '/' + control_dir

#print control_dir
ctl_runmin=121
ctl_runmax=481

model = 'isca'
if (model == 'Isca') or (model == 'isca'): 
    model_data = 'Isca_DATA'
    output_dir1 = 'Isca'
elif (model == 'gfdl') or (model == 'GFDL'):
    model_data = 'GFDL_DATA'
    output_dir1 = ''

HPC = 'yes'
testdir_in1= 'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387'
runmin=120
runmax=480
if (HPC == 'Yes') or (HPC == 'yes') or (HPC == 'y'):
    exp1_name = 'ISCA_HPC_'+testdir_in1
    testdir = model_data + '/ISCA_HPC/' + testdir_in1
    testdir_in1 = '/ISCA_HPC/' + testdir_in1
else: 
    exp1_name = testdir_in1
    testdir = model_data + '/' + testdir_in1

land = 'narrow_three'
landfile=Dataset(os.path.join(GFDL_BASE,'input/'+land+'/land.nc'),mode='r')

landmaskAM=landfile.variables['land_mask'][:]
landlats=landfile.variables['lat'][:]
landlons=landfile.variables['lon'][:]
# for specified lats
landmaskAMxr=xr.DataArray(landmaskAM,coords=[landlats,landlons],dims=['lat','lon']) # need this in order to use .sel(... slice) on it


area_array, dx, dy = ca.cell_area_all(t_res=42,base_dir='/scratch/mp586/GFDL_BASE/GFDL_FORK/GFDLmoistModel/') # added _all because then dx and dy are also returned 
area_array = xr.DataArray(area_array) # returned in units of m bzw m^2, because radius in cell_area.py is given in metres

area_array_3D = np.expand_dims(area_array, axis=0)
area_array_3D = np.repeat(area_array_3D, 40, axis = 0) # to make area_array 3D (pressure, lat, lon)


[net_lheAM,net_lheAM_avg,net_lheAM_seasonal_avg,net_lheAM_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lhe','mm/d',factor = 1./28.) # latent heat flux at surface (UP)
[precipitationAM,precipitationAM_avg,precipitationAM_seasonal_avg,precipitationAM_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'precipitation','mm/d', factor=86400)
[sw_netAM,sw_netAM_avg,sw_netAM_seasonal_avg,sw_netAM_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_sw','W/m^2',factor = 1.) # basically assume that all energy from Rnet goes into evaporation
[tsurfAM,tsurfAM_avg,tsurfAM_seasonal_avg,tsurfAM_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'t_surf','K')
[lw_downAM,lw_downAM_avg,lw_downAM_seasonal_avg,lw_downAM_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lw','W/m^2',factor = 1.) # 
[epAM,epAM_avg,epAM_seasonal_avg,epAM_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'potential_evap','mm/day',factor = 86400) # latent heat flux at surface (UP)

sigma = 5.67*10**(-8)

net_lwAM_avg = sigma*(tsurfAM_avg**4) - lw_downAM_avg

# Ep = Rnet/L, to convert from flux_lhe to mm/day basically convert W/mz to mm/day... factor = 1./28. 
# 1/28.=conversion from W/m^2 to mm/day using E=H/(rho*L), rho=1000kg/m3, L=2.5*10^6J/kg, see www.ce.utexas.edu/prof/maidment/CE374KSpr12/.../Latent%20heat%20flux.pptx @30DegC


[net_lheAM_ctl,net_lheAM_avg_ctl,net_lheAM_seasonal_avg_ctl,net_lheAM_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_lhe','mm/d',factor = 1./28.) # latent heat flux at surface (UP)
[precipitationAM_ctl,precipitationAM_avg_ctl,precipitationAM_seasonal_avg_ctl,precipitationAM_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'precipitation','mm/d', factor=86400)
[sw_netAM_ctl,sw_netAM_avg_ctl,sw_netAM_seasonal_avg_ctl,sw_netAM_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_sw','W/m^2',factor = 1.) # latent heat flux at surface (UP)
[tsurfAM_ctl,tsurfAM_avg_ctl,tsurfAM_seasonal_avg_ctl,tsurfAM_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'t_surf','K')
[lw_downAM_ctl,lw_downAM_avg_ctl,lw_downAM_seasonal_avg_ctl,lw_downAM_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_lw','W/m^2',factor = 1.) # 
[epAM_ctl,epAM_avg_ctl,epAM_seasonal_avg_ctl,epAM_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'potential_evap','mm/day',factor = 86400) # latent heat flux at surface (UP)
# [net_tAM_ctl,net_tAM_avg_ctl,net_tAM_seasonal_avg_ctl,net_tAM_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_t','W/m^2',factor = 1.) # 

net_lwAM_avg_ctl = sigma*(tsurfAM_avg_ctl**4) - lw_downAM_avg_ctl
net_lwAM_ctl = sigma*(tsurfAM_ctl**4) - lw_downAM_ctl

# Ep_AM_estim_ctl = (sw_netAM_avg_ctl - net_lwAM_avg_ctl - net_tAM_avg_ctl)/28. 
Ep_AM_estim_avg_ctl = (sw_netAM_avg_ctl - net_lwAM_avg_ctl)/28. 
Ep_AM_estim_ctl = (sw_netAM_ctl - net_lwAM_ctl)/28. 


testdir_in1= 'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387'
dire = testdir_in1
runmin=120
runmax=480
if (HPC == 'Yes') or (HPC == 'yes') or (HPC == 'y'):
    exp1_name = 'ISCA_HPC/'+testdir_in1
    testdir = model_data + '/ISCA_HPC/' + testdir_in1
    testdir_in1 = '/ISCA_HPC/' + testdir_in1
else: 
    exp1_name = testdir_in1
    testdir = model_data + '/' + testdir_in1

[net_lheAMveg,net_lheAMveg_avg,net_lheAMveg_seasonal_avg,net_lheAMveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lhe','mm/d',factor = 1./28.) # latent heat flux at surface (UP)
[precipitationAMveg,precipitationAMveg_avg,precipitationAMveg_seasonal_avg,precipitationAMveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'precipitation','mm/d', factor=86400)
# [sw_netAMveg,sw_netAMveg_avg,sw_netAMveg_seasonal_avg,sw_netAMveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_sw','mm/day',factor = 1.) # latent heat flux at surface (UP)
# [tsurfAMveg,tsurfAMveg_avg,tsurfAMveg_seasonal_avg,tsurfAMveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'t_surf','K')
# [lw_downAMveg,lw_downAMveg_avg,lw_downAMveg_seasonal_avg,lw_downAMveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lw','W/m^2',factor = 1.) # 
[epAMveg,epAMveg_avg,epAMveg_seasonal_avg,epAMveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'potential_evap','mm/day',factor = 86400) # latent heat flux at surface (UP)




ctl_model = 'isca'
if (ctl_model == 'Isca') or (ctl_model == 'isca'): 
    control_model = 'Isca_DATA'
elif (ctl_model == 'gfdl') or (ctl_model == 'GFDL'):
    control_model = 'GFDL_DATA'

HPC = 'yes'
control_dir = 'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_commitfe93b9d'
if (HPC == 'Yes') or (HPC == 'yes') or (HPC == 'y'):
    control_dir= control_model + '/ISCA_HPC/' + control_dir
else: 
    control_dir= control_model + '/' + control_dir

#print control_dir
ctl_runmin=121
ctl_runmax=481

model = 'isca'
if (model == 'Isca') or (model == 'isca'): 
    model_data = 'Isca_DATA'
    output_dir1 = 'Isca'
elif (model == 'gfdl') or (model == 'GFDL'):
    model_data = 'GFDL_DATA'
    output_dir1 = ''

HPC = 'yes'
testdir_in1= 'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commitfe93b9d'
runmin=120
runmax=480
if (HPC == 'Yes') or (HPC == 'yes') or (HPC == 'y'):
    exp1_name = 'ISCA_HPC_'+testdir_in1
    testdir = model_data + '/ISCA_HPC/' + testdir_in1
    testdir_in1 = '/ISCA_HPC/' + testdir_in1
else: 
    exp1_name = testdir_in1
    testdir = model_data + '/' + testdir_in1

land = 'square_Africa'
landfile=Dataset(os.path.join(GFDL_BASE,'input/'+land+'/land.nc'),mode='r')

landmaskAF=landfile.variables['land_mask'][:]
landlats=landfile.variables['lat'][:]
landlons=landfile.variables['lon'][:]
# for specified lats
landmaskAFxr=xr.DataArray(landmaskAF,coords=[landlats,landlons],dims=['lat','lon']) # need this in order to use .sel(... slice) on it


area_array, dx, dy = ca.cell_area_all(t_res=42,base_dir='/scratch/mp586/GFDL_BASE/GFDL_FORK/GFDLmoistModel/') # added _all because then dx and dy are also returned 
area_array = xr.DataArray(area_array) # returned in units of m bzw m^2, because radius in cell_area.py is given in metres

area_array_3D = np.expand_dims(area_array, axis=0)
area_array_3D = np.repeat(area_array_3D, 40, axis = 0) # to make area_array 3D (pressure, lat, lon)


[net_lheAF,net_lheAF_avg,net_lheAF_seasonal_avg,net_lheAF_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lhe','mm/d',factor = 1./28.) # latent heat flux at surface (UP)
[precipitationAF,precipitationAF_avg,precipitationAF_seasonal_avg,precipitationAF_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'precipitation','mm/d', factor=86400)
[sw_netAF,sw_netAF_avg,sw_netAF_seasonal_avg,sw_netAF_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_sw','mm/day',factor = 1.) # 
[tsurfAF,tsurfAF_avg,tsurfAF_seasonal_avg,tsurfAF_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'t_surf','K')
[lw_downAF,lw_downAF_avg,lw_downAF_seasonal_avg,lw_downAF_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lw','W/m^2',factor = 1.) # 
[epAF,epAF_avg,epAF_seasonal_avg,epAF_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'potential_evap','mm/day',factor = 86400) # latent heat flux at surface (UP)

net_lwAF_avg = sigma*(tsurfAF_avg**4) - lw_downAF_avg

[net_lheAF_ctl,net_lheAF_avg_ctl,net_lheAF_seasonal_avg_ctl,net_lheAF_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_lhe','mm/d',factor = 1./28.) # latent heat flux at surface (UP)
[precipitationAF_ctl,precipitationAF_avg_ctl,precipitationAF_seasonal_avg_ctl,precipitationAF_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'precipitation','mm/d', factor=86400)
[sw_netAF_ctl,sw_netAF_avg_ctl,sw_netAF_seasonal_avg_ctl,sw_netAF_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_sw','mm/day',factor = 1.) # 
[tsurfAF_ctl,tsurfAF_avg_ctl,tsurfAF_seasonal_avg_ctl,tsurfAF_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'t_surf','K')
[lw_downAF_ctl,lw_downAF_avg_ctl,lw_downAF_seasonal_avg_ctl,lw_downAF_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_lw','W/m^2',factor = 1.) # 
[epAF_ctl,epAF_avg_ctl,epAF_seasonal_avg_ctl,epAF_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'potential_evap','mm/day',factor = 86400) # latent heat flux at surface (UP)
# [net_tAF_ctl,net_tAF_avg_ctl,net_tAF_seasonal_avg_ctl,net_tAF_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_t','W/m^2',factor = 1.) # 

net_lwAF_avg_ctl = sigma*(tsurfAF_avg_ctl**4) - lw_downAF_avg_ctl
net_lwAF_ctl = sigma*(tsurfAF_ctl**4) - lw_downAF_ctl

# Ep_AF_estim_ctl = (sw_netAF_avg_ctl - net_lwAF_avg_ctl - net_tAF_avg_ctl)/28. 
Ep_AF_estim_avg_ctl = (sw_netAF_avg_ctl - net_lwAF_avg_ctl)/28. 
Ep_AF_estim_ctl = (sw_netAF_ctl - net_lwAF_ctl)/28. 


testdir_in1= 'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commitfe93b9d'
direAF = testdir_in1
runmin=120
runmax=480
if (HPC == 'Yes') or (HPC == 'yes') or (HPC == 'y'):
    exp1_name = 'ISCA_HPC/'+testdir_in1
    testdir = model_data + '/ISCA_HPC/' + testdir_in1
    testdir_in1 = '/ISCA_HPC/' + testdir_in1
else: 
    exp1_name = testdir_in1
    testdir = model_data + '/' + testdir_in1

[net_lheAFveg,net_lheAFveg_avg,net_lheAFveg_seasonal_avg,net_lheAFveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lhe','mm/d',factor = 1./28.) # latent heat flux at surface (UP)
[precipitationAFveg,precipitationAFveg_avg,precipitationAFveg_seasonal_avg,precipitationAFveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'precipitation','mm/d', factor=86400)
[sw_netAFveg,sw_netAFveg_avg,sw_netAFveg_seasonal_avg,sw_netAFveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_sw','mm/day',factor = 1.) #
[tsurfAFveg,tsurfAFveg_avg,tsurfAFveg_seasonal_avg,tsurfAFveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'t_surf','K')
[lw_downAFveg,lw_downAFveg_avg,lw_downAFveg_seasonal_avg,lw_downAFveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lw','W/m^2',factor = 1.) # 
[epAFveg,epAFveg_avg,epAFveg_seasonal_avg,epAFveg_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'potential_evap','mm/day',factor = 86400) # latent heat flux at surface (UP)


net_lwAFveg_avg = sigma*(tsurfAFveg_avg**4) - lw_downAFveg_avg



# finding omega-parameter

# america 

epAM_ctl_yrs = epAM_ctl.groupby('time.year').mean('time')
Ep_AM_estim_ctl_yrs = Ep_AM_estim_ctl.groupby('time.year').mean('time')
EAM_ctl_yrs = net_lheAM_ctl.groupby('time.year').mean('time')
PAM_ctl_yrs = precipitationAM_ctl.groupby('time.year').mean('time')

rge = np.linspace(1.,5.,99)

obj = np.empty((len(rge)))

j = 0 

for omega in rge: # parameter sweep
    obj_years = np.empty(((np.shape(epAM_ctl_yrs))[0]))
    for i in range((np.shape(epAM_ctl_yrs))[0]):
        epAM_ctl_yrs_awave = area_weighted_avg(epAM_ctl_yrs[i,:,:], area_array, landmaskAMxr, 'land', minlat = -10., maxlat = 10.)
        EAM_ctl_yrs_awave = area_weighted_avg(EAM_ctl_yrs[i,:,:], area_array, landmaskAMxr, 'land', minlat = -10., maxlat = 10.)
        PAM_ctl_yrs_awave = area_weighted_avg(PAM_ctl_yrs[i,:,:], area_array, landmaskAMxr, 'land', minlat = -10., maxlat = 10.)
        obj_years[i] = (EAM_ctl_yrs_awave/PAM_ctl_yrs_awave - (1 + epAM_ctl_yrs_awave/PAM_ctl_yrs_awave - (1 + (epAM_ctl_yrs_awave/PAM_ctl_yrs_awave)**omega)**(1./omega))**2)
    obj[j] = np.sum(obj_years)
    j += 1

omega_opt_AM = rge[np.argmin(np.abs(obj))]


obj = np.empty((len(rge)))

j = 0 


for omega in rge: # parameter sweep
    obj_years = np.empty(((np.shape(epAM_ctl_yrs))[0]))
    for i in range((np.shape(epAM_ctl_yrs))[0]):
        Ep_AM_estim_ctl_yrs_awave = area_weighted_avg(Ep_AM_estim_ctl_yrs[i,:,:], area_array, landmaskAMxr, 'land', minlat = -10., maxlat = 10.)
        EAM_ctl_yrs_awave = area_weighted_avg(EAM_ctl_yrs[i,:,:], area_array, landmaskAMxr, 'land', minlat = -10., maxlat = 10.)
        PAM_ctl_yrs_awave = area_weighted_avg(PAM_ctl_yrs[i,:,:], area_array, landmaskAMxr, 'land', minlat = -10., maxlat = 10.)
        obj_years[i] = (EAM_ctl_yrs_awave/PAM_ctl_yrs_awave - (1 + Ep_AM_estim_ctl_yrs_awave/PAM_ctl_yrs_awave - (1 + (Ep_AM_estim_ctl_yrs_awave/PAM_ctl_yrs_awave)**omega)**(1./omega))**2)
    obj[j] = np.sum(obj_years)
    j += 1

omega_opt_AM_estim = rge[np.argmin(np.abs(obj))]



# africa 

epAF_ctl_yrs = epAF_ctl.groupby('time.year').mean('time')
Ep_AF_estim_ctl_yrs = Ep_AF_estim_ctl.groupby('time.year').mean('time')
EAF_ctl_yrs = net_lheAF_ctl.groupby('time.year').mean('time')
PAF_ctl_yrs = precipitationAF_ctl.groupby('time.year').mean('time')


obj = np.empty((len(rge)))

j = 0 


for omega in rge: # parameter sweep
    obj_years = np.empty(((np.shape(epAF_ctl_yrs))[0]))
    for i in range((np.shape(epAF_ctl_yrs))[0]):
        epAF_ctl_yrs_awave = area_weighted_avg(epAF_ctl_yrs[i,:,:], area_array, landmaskAFxr, 'land', minlat = -10., maxlat = 10.)
        EAF_ctl_yrs_awave = area_weighted_avg(EAF_ctl_yrs[i,:,:], area_array, landmaskAFxr, 'land', minlat = -10., maxlat = 10.)
        PAF_ctl_yrs_awave = area_weighted_avg(PAF_ctl_yrs[i,:,:], area_array, landmaskAFxr, 'land', minlat = -10., maxlat = 10.)
        obj_years[i] = (EAF_ctl_yrs_awave/PAF_ctl_yrs_awave - (1 + epAF_ctl_yrs_awave/PAF_ctl_yrs_awave - (1 + (epAF_ctl_yrs_awave/PAF_ctl_yrs_awave)**omega)**(1./omega))**2)
    obj[j] = np.sum(obj_years)
    j += 1

omega_opt_AF = rge[np.argmin(np.abs(obj))]


obj = np.empty((len(rge)))

j = 0 


for omega in rge: # parameter sweep
    obj_years = np.empty(((np.shape(epAF_ctl_yrs))[0]))
    for i in range((np.shape(epAF_ctl_yrs))[0]):
        Ep_AF_estim_ctl_yrs_awave = area_weighted_avg(Ep_AF_estim_ctl_yrs[i,:,:], area_array, landmaskAFxr, 'land', minlat = -10., maxlat = 10.)
        EAF_ctl_yrs_awave = area_weighted_avg(EAF_ctl_yrs[i,:,:], area_array, landmaskAFxr, 'land', minlat = -10., maxlat = 10.)
        PAF_ctl_yrs_awave = area_weighted_avg(PAF_ctl_yrs[i,:,:], area_array, landmaskAFxr, 'land', minlat = -10., maxlat = 10.)
        obj_years[i] = (EAF_ctl_yrs_awave/PAF_ctl_yrs_awave - (1 + Ep_AF_estim_ctl_yrs_awave/PAF_ctl_yrs_awave - (1 + (Ep_AF_estim_ctl_yrs_awave/PAF_ctl_yrs_awave)**omega)**(1./omega))**2)
    obj[j] = np.sum(obj_years)
    j += 1

omega_opt_AF_estim = rge[np.argmin(np.abs(obj))]



PAM_ctl = precipitationAM_avg_ctl.where(landmaskAM == 1.).sel(lat = slice(-10., 10.))
EAM_ctl = net_lheAM_avg_ctl.where(landmaskAM == 1.).sel(lat = slice(-10., 10.))
epAM_ctl = epAM_avg_ctl.where(landmaskAM == 1.).sel(lat = slice(-10., 10.))
epAMveg = epAMveg_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.))
Ep_AM_estim_ctl = Ep_AM_estim_avg_ctl.where(landmaskAM == 1.).sel(lat = slice(-10., 10.))
epAM = epAM_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.))
PAM = precipitationAM_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.))
EAM = net_lheAM_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.))
PAMveg = precipitationAMveg_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.))
EAMveg = net_lheAMveg_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.))
fu_ctlAM = (epAM_ctl/PAM_ctl) + 1. - (1. + (epAM_ctl/PAM_ctl)**(omega_opt_AM))**(1./omega_opt_AM)
fu_ctlAM_estim = (Ep_AM_estim_ctl/PAM_ctl) + 1. - (1. + (Ep_AM_estim_ctl/PAM_ctl)**(omega_opt_AM_estim))**(1./omega_opt_AM_estim)



PAF_ctl = precipitationAF_avg_ctl.where(landmaskAF == 1.).sel(lat = slice(-10., 10.))
EAF_ctl = net_lheAF_avg_ctl.where(landmaskAF == 1.).sel(lat = slice(-10., 10.))
epAF_ctl = epAF_avg_ctl.where(landmaskAF == 1.).sel(lat = slice(-10., 10.))
Ep_AF_estim_ctl = Ep_AF_estim_avg_ctl.where(landmaskAF == 1.).sel(lat = slice(-10., 10.))
epAFveg = epAFveg_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.))
epAF = epAF_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.))
PAF = precipitationAF_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.))
EAF = net_lheAF_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.))
PAFveg = precipitationAFveg_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.))
EAFveg = net_lheAFveg_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.))
fu_ctlAF = (epAF_ctl/PAF_ctl) + 1. - (1. + (epAF_ctl/PAF_ctl)**(omega_opt_AF))**(1./omega_opt_AF)
fu_ctlAF_estim = (Ep_AF_estim_ctl/PAF_ctl) + 1. - (1. + (Ep_AF_estim_ctl/PAF_ctl)**(omega_opt_AF_estim))**(1./omega_opt_AF_estim)

med = 18

fig, axes = plt.subplots(1,2, sharex = True, sharey = True, figsize = (25,10))

axes[0].plot((epAM_ctl/PAM_ctl), (EAM_ctl/PAM_ctl), 'b.', label = 'control')
axes[0].plot((Ep_AM_estim_ctl/PAM_ctl), (EAM_ctl/PAM_ctl), 'b*', label = 'control estim')
axes[0].plot((epAM/PAM), (EAM/PAM), 'r.', label = 'perturbed (SB)')
axes[0].plot((epAMveg/PAMveg), (EAMveg/PAMveg), 'g.', label = 'perturbed (VP05)')
axes[0].plot([1.0,1.0],[0.0,1.0],color='dimgray',linewidth=1, linestyle = 'dashed')
axes[0].plot([1.0,10.0],[1.0,1.0],color='dimgray',linewidth=1, linestyle = 'dashed')
axes[0].plot([0.0,1.0],[0.0,1.0],color='r',linewidth=1, linestyle = 'dashed')


axes[0].set_xlim(0.0, 10.0)
axes[0].set_ylim(0.0, 1.5)
axes[0].set_title('America', fontsize = med)
axes[0].set_xlabel('E$_P$/P', fontsize = med)
axes[0].set_ylabel('E/P', fontsize = med)

axes[0].plot((epAM_ctl/PAM_ctl), fu_ctlAM, 'k.', label = 'Fu Eq.')
axes[0].plot((Ep_AM_estim_ctl/PAM_ctl), fu_ctlAM_estim, 'k*', label = 'Fu Eq. estim')

# axes[0].plot((epAM/PAM), fu, 'k*')
# axes[0].plot((epAMveg/PAMveg), fu_veg, 'kd')

axes[0].spines['right'].set_visible(False)
axes[0].spines['top'].set_visible(False)



axes[1].plot((epAF_ctl/PAF_ctl), (EAF_ctl/PAF_ctl), 'b.', label = 'control')
axes[1].plot((Ep_AF_estim_ctl/PAF_ctl), (EAF_ctl/PAF_ctl), 'b*', label = 'control estim')

axes[1].plot((epAF/PAF), (EAF/PAF), 'r.', label = 'perturbed (SB)')
axes[1].plot((epAFveg/PAFveg), (EAFveg/PAFveg), 'g.', label = 'perturbed (VP05)')
axes[1].plot([1.0,1.0],[0.0,1.0],color='dimgray',linewidth=1, linestyle = 'dashed')
axes[1].plot([1.0,10.0],[1.0,1.0],color='dimgray',linewidth=1, linestyle = 'dashed')
axes[1].plot([0.0,1.0],[0.0,1.0],color='r',linewidth=1, linestyle = 'dashed')

axes[1].set_xlim(0.0, 10.0)
axes[1].set_ylim(0.0, 1.5)
axes[1].set_title('Africa', fontsize = med)
axes[1].set_xlabel('E$_P$/P', fontsize = med)
axes[1].set_ylabel('E/P', fontsize = med)


axes[1].plot((epAF_ctl/PAF_ctl), fu_ctlAF, 'k.', label = 'Fu Eq.')
axes[1].plot((Ep_AF_estim_ctl/PAF_ctl), fu_ctlAF_estim, 'k*', label = 'Fu Eq. estim')

# axes[1].plot((epAF/PAF), fu, 'k*')
# axes[1].plot((epAFveg/PAFveg), fu_veg, 'kd')

axes[1].spines['right'].set_visible(False)
axes[1].spines['top'].set_visible(False)
axes[1].tick_params(labelsize = med)
axes[0].tick_params(labelsize = med)

fig.legend(fontsize = med, bbox_to_anchor=(0.8,0.4))

fig.savefig('/scratch/mp586/Code/Graphics/Isca/ISCA_HPC/'+dire+'/budyko_curve_fueq_ep_vs_ep_estim_'+str(runmin)+'-'+str(runmax)+'.pdf', bbox_inches = 'tight', dpi=400)
fig.savefig('/scratch/mp586/Code/Graphics/Isca/ISCA_HPC/'+dire+'/budyko_curve_fueq_ep_vs_ep_estim_'+str(runmin)+'-'+str(runmax)+'.png', bbox_inches = 'tight', dpi=400)



outdir = 'Isca/ISCA_HPC/'+dire

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(epAM_avg_ctl/precipitationAM_avg_ctl).where((epAM_avg_ctl/precipitationAM_avg_ctl)<=2.0),area_array,'','limits_ctl','energy_limit',landmaskAMxr, minval = 0., maxval = 2.0)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(epAMveg_avg/precipitationAMveg_avg).where((epAMveg_avg/precipitationAMveg_avg)<=2.0),area_array,'','limits_veg','energy_limit',landmaskAMxr, minval = 0., maxval = 2.0)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(epAM_avg/precipitationAM_avg).where((epAM_avg/precipitationAM_avg)<=2.0),area_array,'','limits_pertb','energy_limit',landmaskAMxr, minval = 0., maxval = 2.0)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(epAM_avg_ctl),area_array,'mm/d','ep_ctl','fromwhite',landmaskAMxr, minval = 0., maxval = 50.)
any_configuration_plot(outdir,runmin,runmax,-90.,90., Ep_AM_estim_avg_ctl,area_array,'mm/d','ep_estim_ctl','fromwhite',landmaskAMxr, minval = 0., maxval = 10.)

exit()

outdir = 'Isca/ISCA_HPC/'+direAF

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(epAF_avg_ctl/precipitationAF_avg_ctl).where((epAF_avg_ctl/precipitationAF_avg_ctl)<=2.),area_array,'','limits_ctl','energy_limit',landmaskAFxr, minval = 0., maxval = 2.0)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(epAFveg_avg/precipitationAFveg_avg).where((epAFveg_avg/precipitationAFveg_avg)<=2.),area_array,'','limits_veg','energy_limit',landmaskAFxr, minval = 0., maxval = 2.0)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(epAF_avg/precipitationAF_avg).where((epAF_avg/precipitationAF_avg)<=2.),area_array,'','limits_pertb','energy_limit',landmaskAFxr, minval = 0., maxval = 2.0)



fig,axes = plt.subplots(1,2,sharex = True, sharey = True, figsize = (25,20))

axes[0].plot(precipitationAM_avg_ctl.where(landmaskAM == 1.).sel(lat = slice(-10., 10.)), net_lheAM_avg_ctl.where(landmaskAM == 1.).sel(lat = slice(-10., 10.)), 'b.', label = 'SB ctl')
axes[0].plot(precipitationAM_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.)), net_lheAM_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.)), 'r.', label = 'SB pert')
axes[0].plot(precipitationAMveg_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.)), net_lheAMveg_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.)), 'g.', label = 'VP pert')
axes[0].plot(precipitationAM_avg_ctl.where(landmaskAM == 1.).sel(lat = slice(-10., 10.)), epAM_avg_ctl.where(landmaskAM == 1.).sel(lat = slice(-10., 10.)), 'k.', label = 'E$_P$ ctl')
axes[0].plot(precipitationAM_avg_ctl.where(landmaskAM == 1.).sel(lat = slice(-10., 10.)), epAMveg_avg.where(landmaskAM == 1.).sel(lat = slice(-10., 10.)), 'k*', label = 'E$_P$ veg')
axes[0].set_xlim(0.,15.)
axes[0].set_ylim(0.,50.)

axes[0].spines['right'].set_visible(False)
axes[0].spines['top'].set_visible(False)

axes[0].set_title('America', fontsize = med)
axes[0].set_ylabel('E and E$_P$ (mm/d)', fontsize = med)
axes[0].set_xlabel('P (mm/d)', fontsize = med)


axes[1].plot(precipitationAF_avg_ctl.where(landmaskAF == 1.).sel(lat = slice(-10., 10.)), net_lheAF_avg_ctl.where(landmaskAF == 1.).sel(lat = slice(-10., 10.)), 'b.', label = 'SB ctl')
axes[1].plot(precipitationAF_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.)), net_lheAF_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.)), 'r.', label = 'SB pert')
axes[1].plot(precipitationAFveg_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.)), net_lheAFveg_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.)), 'g.', label = 'VP pert')
axes[1].plot(precipitationAF_avg_ctl.where(landmaskAF == 1.).sel(lat = slice(-10., 10.)), epAF_avg_ctl.where(landmaskAF == 1.).sel(lat = slice(-10., 10.)), 'k.', label = 'E$_P$ ctl')
axes[1].plot(precipitationAF_avg_ctl.where(landmaskAF == 1.).sel(lat = slice(-10., 10.)), epAFveg_avg.where(landmaskAF == 1.).sel(lat = slice(-10., 10.)), 'k*', label = 'E$_P$ veg')


axes[1].set_xlabel('P (mm/d)', fontsize = med)
axes[1].set_title('Africa', fontsize = med)


axes[1].spines['right'].set_visible(False)
axes[1].spines['top'].set_visible(False)
axes[0].tick_params(labelsize = med)
axes[1].tick_params(labelsize = med)

fig.legend(fontsize = med, bbox_to_anchor=(0.8,0.8))

fig.savefig('/scratch/mp586/Code/Graphics/Isca/ISCA_HPC/'+dire+'/budyko_curve_AF_AM.pdf', bbox_inches = 'tight', dpi=400)
fig.savefig('/scratch/mp586/Code/Graphics/Isca/ISCA_HPC/'+dire+'/budyko_curve_AF_AM.png', bbox_inches = 'tight', dpi=400)
