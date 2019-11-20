from netCDF4 import Dataset
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
import xarray as xr
import pandas as pd
import os

import sys
sys.path.insert(0, '/scratch/mp586/Code/PYCODES')
from plotting_routines_kav7 import *
import stats as st

GFDL_BASE = os.environ['GFDL_BASE']
sys.path.insert(0, os.path.join(GFDL_BASE,'src/extra/python/scripts'))
import cell_area as ca

ctl_model = input('Enter model name as string ')
if (ctl_model == 'Isca') or (ctl_model == 'isca'): 
    control_model = 'Isca_DATA'
elif (ctl_model == 'gfdl') or (ctl_model == 'GFDL'):
    control_model = 'GFDL_DATA'


control_dir= control_model + '/' + input('Enter control directory name as string ')
#print control_dir
ctl_runmin=input('Enter runmin number ')  # Should be a January month for seasonal variables to be correct
ctl_runmax=input('Enter runmax number for comparison ')
ctl_timeseries_max = input('Enter end of ctl timeseries month ')

model = input('Enter model ')
if (model == 'Isca') or (model == 'isca'): 
    model_data = 'Isca_DATA'
    output_dir = 'Isca'
elif (model == 'gfdl') or (model == 'GFDL'):
    model_data = 'GFDL_DATA'
    output_dir = ''

testdir= input('Enter data directory name as string ')
runmin=input('Enter runmin number ')  # Should be a January month for seasonal variables to be correct
runmax=input('Enter runmax number ')


outdir = output_dir + '/' + testdir
testdir = model_data + '/' + testdir

land = input('Which landmask? ')
landfile=Dataset(os.path.join(GFDL_BASE,'input/'+land+'/land.nc'),mode='r')

landmask=landfile.variables['land_mask'][:]
landlats=landfile.variables['lat'][:]
landlons=landfile.variables['lon'][:]
# for specified lats
landmaskxr=xr.DataArray(landmask,coords=[landlats,landlons],dims=['lat','lon']) # need this in order to use .sel(... slice) on it

level = input('Which Level? ')


area_array, dx, dy = ca.cell_area_all(t_res=42,base_dir='/scratch/mp586/GFDL_BASE/GFDL_FORK/GFDLmoistModel/') # added _all because then dx and dy are also returned 
area_array = xr.DataArray(area_array) # returned in units of m bzw m^2, because radius in cell_area.py is given in metres

area_array_3D = np.expand_dims(area_array, axis=0)
area_array_3D = np.repeat(area_array_3D, 40, axis = 0) # to make area_array 3D (pressure, lat, lon)

total_sfc_area = np.sum(area_array)
#print ('total sfc area (*10^14) = '+str(np.sum(area_array/(10**14)))) # -- test: correct, equals sfc area of earth (5.1*10**14 m^2)
land_sfc_area = np.sum(area_array.where(landmask==1.))
#print ('land sfc area (*10^14) = '+str(land_sfc_area/(10**14)))
ocean_sfc_area = np.sum(area_array.where(landmask!=1.))
#print ('ocean sfc area (*10^14) = '+str(ocean_sfc_area/(10**14)))

# for plotting a spin up run ('control') timeseries followed by the timeseries from the perturbed experiment
globavg_var_timeseries_total_and_land_perturbed(testdir,outdir,model,area_array,'t_surf',1,runmax,1.,landmaskxr,control_dir,ctl_model,1,ctl_timeseries_max)
#globavg_var_timeseries_total_and_land_perturbed(testdir,outdir,model,area_array,'bucket_depth',1,runmax,1.,landmask,control_dir,ctl_model,1,ctl_timeseries_max,select='land')

# mass stream function adapted from J Penn
[msf,msf_avg,msf_seasonal_avg,msf_month_avg] = mass_streamfunction(testdir,model,runmin,runmax) # 
plot_streamfunction_seasonal(msf_seasonal_avg, outdir, runmin, runmax, ctl_pert = 'pert')

[msf_ctl,msf_avg_ctl,msf_seasonal_avg_ctl,msf_month_avg_ctl] = mass_streamfunction(control_dir,ctl_model,ctl_runmin,ctl_runmax) # 
plot_streamfunction_seasonal(msf_seasonal_avg_ctl, outdir, ctl_runmin, ctl_runmax, ctl_pert = 'ctl')

# Read in variables 

[slp,slp_avg,slp_seasonal_avg,slp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'slp','hPa',factor=10**(-2))
[tsurf,tsurf_avg,tsurf_seasonal_avg,tsurf_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'t_surf','K')
[lhe_flux,lhe_flux_avg,lhe_flux_seasonal_avg,lhe_flux_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lhe','W/m2',factor = 1.) # latent heat flux at surface (UP)
[net_lhe,net_lhe_avg,net_lhe_seasonal_avg,net_lhe_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lhe','mm/d',factor = 1./28.) # latent heat flux at surface (UP)

[precipitation,precipitation_avg,precipitation_seasonal_avg,precipitation_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'precipitation','mm/d', factor=86400)
#[bucket_depth,bucket_depth_avg,bucket_depth_seasonal_avg,bucket_depth_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'bucket_depth','m')
[rh,rh_avg,rh_seasonal_avg,rh_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'rh','%',level=level)
[net_sw,net_sw_avg,net_sw_seasonal_avg,net_sw_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_sw','W/m^2',factor = 1.) # Pretty sure this is actually pos. downward! 
[lw_down,lw_down_avg,lw_down_seasonal_avg,lw_down_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_lw','W/m^2',factor = 1.) # 
#[CIWV,CIWV_avg,CIWV_seasonal_avg,CIWV_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'sphum','kg/kg',level='all')
[net_t,net_t_avg,net_t_seasonal_avg,net_t_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_t','W/m^2',factor = 1.) # 
[toa_sw,toa_sw_avg,toa_sw_seasonal_avg,toa_sw_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'toa_sw','W/m^2',factor = 1.) # positive DOWN



[gph,gph_avg,gph_seasonal_avg,gph_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'height','m', level = 27) # geopotential height at 500 hPa
[gph_ctl,gph_avg_ctl,gph_seasonal_avg_ctl,gph_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'height','m', level = 27) # geopotential height at 500 hPa


[slp_ctl,slp_avg_ctl,slp_seasonal_avg_ctl,slp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'slp','hPa',factor=10**(-2))
[tsurf_ctl,tsurf_avg_ctl,tsurf_seasonal_avg_ctl,tsurf_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'t_surf','K')
[lhe_flux_ctl,lhe_flux_avg_ctl,lhe_flux_seasonal_avg_ctl,lhe_flux_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_lhe','W/m2',factor = 1.) # latent heat flux at surface (UP)
[net_lhe_ctl,net_lhe_avg_ctl,net_lhe_seasonal_avg_ctl,net_lhe_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_lhe','mm/d',factor = 1./28.) # latent heat flux at surface (UP)
[toa_sw_ctl,toa_sw_avg_ctl,toa_sw_seasonal_avg_ctl,toa_sw_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'toa_sw','W/m^2',factor = 1.) # positive DOWN

[precipitation_ctl,precipitation_avg_ctl,precipitation_seasonal_avg_ctl,precipitation_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'precipitation','mm/d', factor=86400)
#[bucket_depth_ctl,bucket_depth_avg_ctl,bucket_depth_seasonal_avg_ctl,bucket_depth_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'bucket_depth','m')
[rh_ctl,rh_avg_ctl,rh_seasonal_avg_ctl,rh_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'rh','%',level=level)
# [flux_oceanq_ctl,flux_oceanq_avg_ctl,flux_oceanq_seasonal_avg_ctl,flux_oceanq_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_oceanq','W/m^2')
[net_sw_ctl,net_sw_avg_ctl,net_sw_seasonal_avg_ctl,net_sw_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_sw','W/m^2',factor = 1.) # 
[lw_down_ctl,lw_down_avg_ctl,lw_down_seasonal_avg_ctl,lw_down_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_lw','W/m^2',factor = 1.) # 
[net_t_ctl,net_t_avg_ctl,net_t_seasonal_avg_ctl,net_t_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'flux_t','W/m^2',factor = 1.) # 
#[CIWV_ctl,CIWV_avg_ctl,CIWV_seasonal_avg_ctl,CIWV_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'sphum','kg/kg',level='all')

[sphum,sphum_avg,sphum_seasonal_avg,sphum_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'sphum','kg/kg',level=level)
[sphum_ctl,sphum_avg_ctl,sphum_seasonal_avg_ctl,sphum_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'sphum','kg/kg',level=level)

[div,div_avg,div_seasonal_avg,div_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'div','1/sec',level=level)
[div_ctl,div_avg_ctl,div_seasonal_avg_ctl,div_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'div','1/sec',level=level)

# rh_P_E_T(outdir,runmin,runmax,rh_avg,precipitation_avg,net_lhe_avg,tsurf_avg,landmask)


PE = precipitation - net_lhe
[PE,PE_avg,PE_seasonal_avg,PE_month_avg,time] = make_var_seasonal(PE)
PE_ctl = precipitation_ctl - net_lhe_ctl
[PE_ctl,PE_avg_ctl,PE_seasonal_avg_ctl,PE_month_avg_ctl,time] = make_var_seasonal(PE_ctl)

PE_avg_sum = area_integral(PE_avg,area_array,landmaskxr,'all_sfcs',factor = 10**(-3)) # factor to 
#convert from mm/d to m/d
#print('P avg - E avg global integral / total sfc area'+str(PE_avg_sum/total_sfc_area))



# # [flux_oceanq,flux_oceanq_avg,flux_oceanq_seasonal_avg,flux_oceanq_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'flux_oceanq','W/m^2')
[olr_ctl,olr_avg_ctl,olr_seasonal_avg_ctl,olr_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'olr','W/m^2',factor = 1.) # 
[olr,olr_avg,olr_seasonal_avg,olr_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'olr','W/m^2',factor = 1.) # 

sigma = 5.67*10**(-8)
net_lw_avg = sigma*(tsurf_avg**4) - lw_down_avg # positive upward

#positive upward: energy input to the atmosphere is pos.
SEB_areaavg = - area_weighted_avg(net_sw_avg,area_array,landmaskxr,option='all_sfcs') + area_weighted_avg(net_lw_avg,area_array,landmaskxr,option='all_sfcs') + area_weighted_avg(lhe_flux_avg,area_array,landmaskxr,option='all_sfcs') + area_weighted_avg(net_t_avg,area_array,landmaskxr,option='all_sfcs') # optional, if there is a qflux + area_weighted_avg(flux_oceanq_avg,area_array,landmaskxr,option='ocean')
print('SEB (perturbed) in W/m2 = '+str(SEB_areaavg))

SEB_avg = - net_sw_avg + net_lw_avg + lhe_flux_avg + net_t_avg ##perturbed run 
TOA_avg = toa_sw_avg - olr_avg # toa sw pos down!, olr pos up (? yep)  # TOA pos down

N_avg = SEB_avg + TOA_avg #total energy input to the atmosphere 

[omega,omega_avg,omega_seasonal_avg,omega_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'omega','Pa/s', level = 27) # geopotential height at 500 hPa
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(omega_avg),area_array,'Pa/s','omega_avg','rainnorm',landmaskxr)
globavg_N_avg = area_weighted_avg(N_avg,area_array,landmaskxr,option='all_sfcs')
any_configuration_plot(outdir,runmin,runmax,-90.,90.,N_avg,area_array,'W/m^2','N_avg','rainnorm',landmaskxr, nmb_contours = [-0.05,-0.04,-0.03,-0.02,-0.01,0.,0.01,0.02,0.03,0.04,0.05], array2 = omega_avg)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(N_avg - globavg_N_avg),area_array,'W/m^2','N_avg-globavg_N_avg','rainnorm',landmaskxr, nmb_contours = [-0.04,-0.03,-0.02,-0.01,0.,0.01,0.02,0.03,0.04], array2 = omega_avg)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(toa_sw_avg),area_array,'W/m^2','toa_sw_avg','rainnorm',landmaskxr)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(olr_avg),area_array,'W/m^2','olr_avg','rainnorm',landmaskxr)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_sw_avg),area_array,'W/m^2','net_sw_avg','rainnorm',landmaskxr)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_lw_avg),area_array,'W/m^2','net_lw_avg','rainnorm',landmaskxr)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(lhe_flux_avg),area_array,'W/m^2','lhe_flux_avg','rainnorm',landmaskxr)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_t_avg),area_array,'W/m^2','lhe_flux_avg','rainnorm',landmaskxr)

net_lw_avg_ctl = sigma*(tsurf_avg_ctl**4) - lw_down_avg_ctl # positive upward

#positive upward: energy input to the atmosphere is pos.
SEB_areaavg_ctl = area_weighted_avg( - net_sw_avg_ctl,area_array,landmaskxr,option='all_sfcs') + area_weighted_avg(net_lw_avg_ctl,area_array,landmaskxr,option='all_sfcs') + area_weighted_avg(lhe_flux_avg_ctl,area_array,landmaskxr,option='all_sfcs') + area_weighted_avg(net_t_avg_ctl,area_array,landmaskxr,option='all_sfcs') # optional, if there is a qflux + area_weighted_avg(flux_oceanq_avg,area_array,landmaskxr,option='ocean')
print('SEB (control) in W/m2 = '+str(SEB_areaavg_ctl))

SEB_avg_ctl = - net_sw_avg_ctl + net_lw_avg_ctl + lhe_flux_avg_ctl + net_t_avg_ctl ##perturbed run 

TOA_avg_ctl = toa_sw_avg_ctl - olr_avg_ctl # toa sw pos down!, olr pos up (?) 

N_avg_ctl = SEB_avg_ctl + TOA_avg_ctl #total energy input to the atmosphere 

DeltaN = N_avg - N_avg_ctl

DeltaN_zonalmean = DeltaN.mean('lon')
DeltaN_zonalmean = np.expand_dims(DeltaN_zonalmean,axis = 1)
DeltaN_zonalmean = np.repeat(DeltaN_zonalmean, 128, axis = 1)
DeltaN_zonalmean = xr.DataArray(DeltaN_zonalmean, coords = [N_avg.lat, N_avg.lon], dims = ['lat','lon'])



[omega_ctl,omega_avg_ctl,omega_seasonal_avg_ctl,omega_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'omega','Pa/s', level = 27) # geopotential height at 500 hPa
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(omega_avg_ctl),area_array,'Pa/s','omega_ctl','rainnorm',landmaskxr)
globavg_N_avg_ctl = area_weighted_avg(N_avg_ctl,area_array,landmaskxr,option='all_sfcs')
any_configuration_plot(outdir,runmin,runmax,-90.,90.,N_avg_ctl,area_array,'W/m^2','N_ctl','rainnorm',landmaskxr, nmb_contours = [-0.05,-0.04,-0.03,-0.02,-0.01,0.,0.01,0.02,0.03,0.04,0.05], array2 = omega_avg_ctl)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(N_avg_ctl - globavg_N_avg_ctl),area_array,'W/m^2','N_ctl-globavg_N_ctl','rainnorm',landmaskxr, nmb_contours = [-0.04,-0.03,-0.02,-0.01,0.,0.01,0.02,0.03,0.04], array2 = omega_avg_ctl)

any_configuration_plot(outdir,runmin,runmax,-90.,90.,N_avg - N_avg_ctl,area_array,'W/m^2','N_avg_minus_ctl','rainnorm',landmaskxr, minval = -20., maxval = 20., nmb_contours = [-0.02,-0.002,0.002,0.02], array2 = (omega_avg - omega_avg_ctl))
any_configuration_plot(outdir,runmin,runmax,-90.,90.,N_avg - N_avg_ctl,area_array,'W/m^2','N_avg_minus_ctl_landcbar','rainnorm',landmaskxr, minval = -230., maxval = -170., nmb_contours = [-0.02,-0.002,0.002,0.02], array2 = (omega_avg - omega_avg_ctl))

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(N_avg - N_avg_ctl) - DeltaN_zonalmean,area_array,'W/m^2','N_avg_minus_ctl_zonalanomalies','rainnorm',landmaskxr, minval = -20., maxval = 20.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(N_avg - N_avg_ctl) - DeltaN_zonalmean,area_array,'W/m^2','N_avg_minus_ctl_zonalanomalies_landcbar','rainnorm',landmaskxr, minval = -100., maxval = 0.)

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((toa_sw_avg - toa_sw_avg_ctl)/(N_avg - N_avg_ctl))*100.,area_array,'% (W/m^2)','toa_sw_avg_minus_ctl_relchange','rainnorm',landmaskxr, minval = -80., maxval = 80.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((olr_avg - olr_avg_ctl)/(N_avg - N_avg_ctl))*100.,area_array,'% (W/m^2)','olr_avg_minus_ctl_relchange','rainnorm',landmaskxr, minval = -80., maxval = 80.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((net_sw_avg - net_sw_avg_ctl)/(N_avg - N_avg_ctl))*100.,area_array,'% (W/m^2)','net_sw_avg_minus_ctl_relchange','rainnorm',landmaskxr, minval = -80., maxval = 80.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((net_lw_avg - net_lw_avg_ctl)/(N_avg - N_avg_ctl))*100.,area_array,'% (W/m^2)','net_lw_avg_minus_ctl_relchange','rainnorm',landmaskxr, minval = -80., maxval = 80.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((sigma*(tsurf_avg**4) - sigma*(tsurf_avg_ctl**4))/(N_avg - N_avg_ctl))*100.,area_array,'% (W/m^2)','lw_up_avg_minus_ctl_relchange','rainnorm',landmaskxr, minval = -80., maxval = 80.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((lw_down_avg - lw_down_avg_ctl)/(N_avg - N_avg_ctl))*100.,area_array,'% (W/m^2)','lw_down_avg_minus_ctl_relchange','rainnorm',landmaskxr, minval = -80., maxval = 80.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((lhe_flux_avg - lhe_flux_avg_ctl)/(N_avg - N_avg_ctl))*100.,area_array,'% (W/m^2)','lhe_flux_avg_minus_ctl_relchange','rainnorm',landmaskxr, minval = -80., maxval = 80.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((net_t_avg - net_t_avg_ctl)/(N_avg - N_avg_ctl))*100.,area_array,'% (W/m^2)','sh_flux_avg_minus_ctl_relchange','rainnorm',landmaskxr, minval = -100., maxval = 100.)

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(omega_avg - omega_avg_ctl),area_array,'Pa/s','omega_avg_minus_ctl_500hPa','rainnorm',landmaskxr)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(toa_sw_avg - toa_sw_avg_ctl),area_array,'(W/m^2)','toa_sw_avg_minus_ctl','rainnorm',landmaskxr, minval = -80., maxval = 80.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(olr_avg - olr_avg_ctl),area_array,'(W/m^2)','olr_avg_minus_ctl','rainnorm',landmaskxr, minval = -80., maxval = 80.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_sw_avg - net_sw_avg_ctl),area_array,'(W/m^2)','net_sw_avg_minus_ctl','rainnorm',landmaskxr, minval = -80., maxval = 80.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_lw_avg - net_lw_avg_ctl),area_array,'(W/m^2)','net_lw_avg_minus_ctl','rainnorm',landmaskxr, minval = -80., maxval = 80.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sigma*(tsurf_avg**4) - sigma*(tsurf_avg_ctl**4)),area_array,'(W/m^2)','lw_up_avg_minus_ctl','rainnorm',landmaskxr, minval = -80., maxval = 80.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(lw_down_avg - lw_down_avg_ctl),area_array,'(W/m^2)','lw_down_avg_minus_ctl','rainnorm',landmaskxr, minval = -80., maxval = 80.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(lhe_flux_avg - lhe_flux_avg_ctl),area_array,'(W/m^2)','lhe_flux_avg_minus_ctl','rainnorm',landmaskxr, minval = -80., maxval = 80.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_t_avg - net_t_avg_ctl),area_array,'(W/m^2)','sh_flux_avg_minus_ctl','rainnorm',landmaskxr, minval = -80., maxval = 80.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_sw_avg - net_sw_avg_ctl),area_array,'(W/m^2)','net_sw_avg_minus_ctl','rainnorm',landmaskxr, minval = -80., maxval = 80.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(SEB_avg - SEB_avg_ctl),area_array,'(W/m^2)','SEB_avg_minus_ctl','rainnorm',landmaskxr, minval = -10., maxval = 10.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(TOA_avg - TOA_avg_ctl),area_array,'(W/m^2)','TOA_avg_minus_ctl','rainnorm',landmaskxr, minval = -10., maxval = 10.)
any_configuration_plot(outdir,runmin,runmax,-90.,90., - (olr_avg - olr_avg_ctl),area_array,'(W/m^2)','olr_avg_minus_ctl_narrowcbar_posdown','rainnorm',landmaskxr, minval = -10., maxval = 10.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(toa_sw_avg - toa_sw_avg_ctl),area_array,'(W/m^2)','toa_sw_avg_minus_ctl_narrowcbar','rainnorm',landmaskxr, minval = -10., maxval = 10.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(toa_sw_avg - toa_sw_avg_ctl) - (net_sw_avg - net_sw_avg_ctl),area_array,'(W/m^2)','toa_minus_sfc_sw_avg_minus_ctl','rainnorm',landmaskxr, minval = -10., maxval = 10.)

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(TOA_avg),area_array,'(W/m^2)','TOA_avg','rainnorm',landmaskxr, minval = -100., maxval = 100.)


############# RH change vs P and E changes - scatter plots #####################
rh_P_E_change(outdir,runmin,runmax,rh_avg,rh_avg_ctl,precipitation_avg,precipitation_avg_ctl,net_lhe_avg,net_lhe_avg_ctl,tsurf_avg,tsurf_avg_ctl,landmask,sfc='all')
rh_P_E_change(outdir,runmin,runmax,rh_avg,rh_avg_ctl,precipitation_avg,precipitation_avg_ctl,net_lhe_avg,net_lhe_avg_ctl,tsurf_avg,tsurf_avg_ctl,landmask, sfc='land')
rh_P_E_change(outdir,runmin,runmax,rh_avg,rh_avg_ctl,precipitation_avg,precipitation_avg_ctl,net_lhe_avg,net_lhe_avg_ctl,tsurf_avg,tsurf_avg_ctl,landmask,sfc='ocean')
################################################################################





# # Divergence
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,div_avg - div_avg_ctl,area_array,'%','div_avg_minus_ctl_lev'+str(level),'rainnorm',landmaskxr,nmb_contours=5)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,div_avg,area_array,'%','div_avg_lev'+str(level),'rainnorm',landmaskxr,nmb_contours=5)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,div_avg_ctl,area_array,'%','div_ctl_lev'+str(level),'rainnorm',landmaskxr,nmb_contours=5)


# ####### Map plots annual means 

# # Temperature 

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(tsurf_avg-tsurf_avg_ctl),area_array,'K','$T_S$_avg_minus_ctl_narrowcbar','tempdiff',landmaskxr, minval = -4., maxval = 4.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(tsurf_avg-tsurf_avg_ctl),area_array,'K','$T_S$_avg_minus_ctl','tempdiff',landmaskxr, minval = -10, maxval = 10.,steps=21)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,tsurf_avg - 273.15,area_array,'C','$T_S$_avg','temp0',landmaskxr, minval = -40., maxval = 40., steps = 41)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,tsurf_avg_ctl - 273.15,area_array,'C','$T_S$_ctl','temp0',landmaskxr, minval = -40., maxval = 40., steps = 41)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((tsurf_avg-tsurf_avg_ctl)/tsurf_avg_ctl)*100.,area_array,'%','$T_S$_avg_minus_ctl_relativechange','tempdiff',landmaskxr)


any_configuration_plot_allmonths(outdir,runmin,runmax,-90.,90.,(tsurf_month_avg-tsurf_month_avg_ctl),area_array,'K','$T_S$_avg_minus_ctl','tempdiff',landmaskxr, minval = -10, maxval = 10.)
any_configuration_plot_allmonths(outdir,runmin,runmax,-90.,90.,(tsurf_month_avg - 273.15),area_array,'C','$T_S$_avg','temp0',landmaskxr, minval = -30., maxval = 30.)
any_configuration_plot_allmonths(outdir,runmin,runmax,-90.,90.,(tsurf_month_avg_ctl - 273.15),area_array,'C','$T_S$_ctl','temp0',landmaskxr, minval = -30., maxval = 30.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((tsurf_avg-tsurf_avg_ctl)/tsurf_avg_ctl)*100.,area_array,'%','$T_S$_avg_minus_ctl_relativechange','tempdiff',landmaskxr)


# Precipitation - Evaporation
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(PE_avg - PE_avg_ctl),area_array,'mm/day','P-E_avg_minus_ctl','PE_scale',landmaskxr,minval=-2.,maxval=2.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(PE_avg),area_array,'mm/day','P-E avg','PE_scale',landmaskxr,minval=-2.,maxval=2.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(PE_avg_ctl),area_array,'mm/day','P-E_ctl','PE_scale',landmaskxr,minval=-2.,maxval=2.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(PE_avg_ctl),area_array,'mm/day','P-E_ctl_widebar','PE_scale',landmaskxr,minval=-10.,maxval=10.,steps=21)
# Precipitation
any_configuration_plot(outdir,runmin,runmax,-90.,90.,precipitation_avg,area_array,'mm/day','P_avg','fromwhite',landmaskxr, minval = 0., maxval = 8., steps = 11)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,precipitation_avg_ctl,area_array,'mm/day','P_ctl','fromwhite',landmaskxr,minval = 0., maxval = 8., steps = 11)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(precipitation_avg - precipitation_avg_ctl),area_array,'mm/day','P_avg_minus_ctl','rainnorm',landmaskxr, minval=-2.,maxval=2., nmb_contours = [-1.,1.], array2 = PE_avg_ctl)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(precipitation_avg - precipitation_avg_ctl),area_array,'mm/day','P_avg_minus_ctl_widebar','rainnorm',landmaskxr, minval=-4.,maxval=4., nmb_contours = [-1.,1.], array2 = PE_avg_ctl)

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(precipitation_avg - precipitation_avg_ctl),area_array,'mm/day','P_avg_minus_ctl_narrowbar','rainnorm',landmaskxr, minval=-1.,maxval=1., nmb_contours = [-1.,1.], array2 = PE_avg_ctl)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,((precipitation_avg - precipitation_avg_ctl) / precipitation_avg_ctl),area_array,'mm/day','P_avg_minus_ctl_relchange','rainnorm',landmaskxr, minval=-1.,maxval=1., nmb_contours = [-1.,1.], array2 = PE_avg_ctl)

any_configuration_plot_allmonths(outdir,runmin,runmax,-90.,90.,precipitation_month_avg,area_array,'mm/day','P_avg','fromwhite',landmaskxr, minval = 0., maxval = 8.)
any_configuration_plot_allmonths(outdir,runmin,runmax,-90.,90.,precipitation_month_avg_ctl,area_array,'mm/day','P_ctl','fromwhite',landmaskxr,minval = 0., maxval = 8.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,precipitation_avg_ctl,area_array,'mm/day','P_ctl_tinybar','fromwhite',landmaskxr,minval = 0., maxval = 2.) 
any_configuration_plot_allmonths(outdir,runmin,runmax,-90.,90.,(precipitation_month_avg - precipitation_month_avg_ctl),area_array,'mm/day','P_avg_minus_ctl','rainnorm',landmaskxr, minval=-4.,maxval=4.)



# Evaporation 
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_lhe_avg - net_lhe_avg_ctl),area_array,'mm/day','E_avg_minus_ctl','rainnorm',landmaskxr,minval=-2.,maxval=2.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_lhe_avg),area_array,'mm/day','E_avg','fromwhite',landmaskxr,minval=0.,maxval=8.,steps = 11)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_lhe_avg_ctl),area_array,'mm/day','E_ctl','fromwhite',landmaskxr,minval=0.,maxval=8., steps = 11)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_lhe_avg - net_lhe_avg_ctl),area_array,'mm/day','E_avg_minus_ctl_oceanscale','rainnorm',landmaskxr,minval=-0.5,maxval=0.5)


# # Surface energy fluxes 
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_sw_avg - net_sw_avg_ctl),area_array,'W/m2','SW_avg_minus_ctl','rainnorm',landmaskxr,minval=-4.,maxval=4.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_lw_avg - net_lw_avg_ctl),area_array,'W/m2','LW_avg_minus_ctl','rainnorm',landmaskxr,minval=-40.,maxval=40.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(net_t_avg - net_t_avg_ctl),area_array,'W/m2','SH_avg_minus_ctl','rainnorm',landmaskxr,minval=-30.,maxval=30.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,lhe_flux_avg - lhe_flux_avg_ctl,area_array,'W/m2','lhe_flux_minus_ctl','rainnorm',landmaskxr,minval=-30.,maxval=30.)

# # Random stuff 
any_configuration_plot(outdir,runmin,runmax,-90.,90.,rh_avg - rh_avg_ctl,area_array,'%','rh_avg_minus_ctl_lev'+str(level),'rainnorm',landmaskxr,nmb_contours=5, minval=-7., maxval = 7.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sphum_avg - sphum_avg_ctl)*10**(3.),area_array,'x10^(-3) kg/kg','sphum_avg_minus_ctl_lev'+str(level),'rainnorm',landmaskxr,nmb_contours=0, minval=-4, maxval = 4)

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(bucket_depth_avg - bucket_depth_avg_ctl),area_array,'mm/day','bucket depth avg minus ctl','rainnorm',landmaskxr)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,CIWV_avg - CIWV_avg_ctl,area_array,'kg/kg','column_IWV_minus_ctl','rainnorm',landmaskxr,nmb_contours=5, minval = -0.05, maxval = 0.05)
#any_configuration_plot(outdir,runmin,runmax,-90.,90.,flux_oceanq_avg_ctl,area_array,'W/m^2','ocean_heat_transport_ctl','tempdiff',landmaskxr,minval=-200,maxval=200)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(PE_avg - PE_avg_ctl).where(landmask==1.),area_array,'mm/day','P-E avg minus ctl','rainnorm',landmaskxr,minval=-0.5,maxval=0.5
#any_configuration_plot(outdir,runmin,runmax,-90.,90.,((precipitation_avg - precipitation_avg_ctl)/precipitation_avg_ctl)*100.,area_array,'%','P_avg_minus_ctl_relativechange_','rainnorm',landmaskxr,minval=-100.,maxval=100.)




# # Pressures
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,slp_avg - slp_avg_ctl,area_array,'hPa','slp_avg_minus_ctl_lev'+str(level),'slp',landmaskxr, nmb_contours = 8, minval = -10, maxval = 10)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,slp_avg,area_array,'hPa','slp_avg'+str(level),'slp',landmaskxr, nmb_contours = 8, minval = 980, maxval = 1020)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,slp_avg_ctl,area_array,'hPa','slp_ctl'+str(level),'slp',landmaskxr, nmb_contours = 8, minval = 980, maxval = 1020)

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,gph_avg,area_array,'m','500hPa_geopo_height_avg','slp',landmaskxr, nmb_contours = 10, minval = 5600, maxval = 5800)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,gph_avg_ctl,area_array,'m','500hPa_geopo_height_ctl','slp',landmaskxr, nmb_contours = 10, minval = 5600, maxval = 5800)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,gph_avg - gph_avg_ctl,area_array,'m','500hPa_geopo_height_avg_minus_ctl','slp',landmaskxr, nmb_contours = 8, minval = -80., maxval = 80.)

# # winds + geopoetential height @ 500hPa
# [ucomp,ucomp_avg,ucomp_seasonal_avg,ucomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'ucomp','m/s', level = 27)
# [vcomp,vcomp_avg,vcomp_seasonal_avg,vcomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'vcomp','m/s', level = 27)
# [ucomp_ctl,ucomp_avg_ctl,ucomp_seasonal_avg_ctl,ucomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'ucomp','m/s', level = 27)
# [vcomp_ctl,vcomp_avg_ctl,vcomp_seasonal_avg_ctl,vcomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'vcomp','m/s', level = 27)

# winds_one_level(outdir,runmin,runmax,'500hPa_gph_winds_avg_minus_ctl_monthlydata_',ucomp_avg - ucomp_avg_ctl,vcomp_avg - vcomp_avg_ctl,gph_avg - gph_avg_ctl,
# 	'slp','m',-80., 80.,landmaskxr,veclen=10,level=27,units_numerator = 'm', units_denom = 's', save = True)
# winds_one_level(outdir,runmin,runmax,'500hPa_gph_winds_monthlydata_avg_',ucomp_avg,vcomp_avg,gph_avg,
# 	'slp','m',5600., 5800.,landmaskxr,veclen=10.,level=27,units_numerator = 'm', units_denom = 's', save = True)
# winds_one_level(outdir,ctl_runmin,ctl_runmax,'500hPa_gph_winds_monthlydata_ctl_',ucomp_avg_ctl,vcomp_avg_ctl,gph_avg_ctl,
# 	'slp','m',5600., 5800.,landmaskxr,veclen=10.,level=27,units_numerator = 'm', units_denom = 's', save = True)



# winds + geopoetential height @ 820hPa

[gph,gph_avg,gph_seasonal_avg,gph_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'height','m', level = 37) # geopotential height at 870 hPa
[gph_ctl,gph_avg_ctl,gph_seasonal_avg_ctl,gph_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'height','m', level = 37) 

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,gph_avg,area_array,'m','870hPa_geopo_height_avg','slp',landmaskxr, nmb_contours = 10, minval = 1600, maxval = 1700)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,gph_avg_ctl,area_array,'m','870hPa_geopo_height_ctl','slp',landmaskxr, nmb_contours = 10, minval = 1600, maxval = 1700)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,gph_avg - gph_avg_ctl,area_array,'m','870hPa_geopo_height_avg_minus_ctl','slp',landmaskxr, nmb_contours = 8, minval = 14., maxval = 20.)

[ucomp,ucomp_avg,ucomp_seasonal_avg,ucomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'ucomp','m/s', level = 37)
[vcomp,vcomp_avg,vcomp_seasonal_avg,vcomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'vcomp','m/s', level = 37)
[ucomp_ctl,ucomp_avg_ctl,ucomp_seasonal_avg_ctl,ucomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'ucomp','m/s', level = 37)
[vcomp_ctl,vcomp_avg_ctl,vcomp_seasonal_avg_ctl,vcomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'vcomp','m/s', level = 37)

winds_one_level(outdir,runmin,runmax,'870hPa_gph_winds_avg_minus_ctl_monthlydata_',ucomp_avg - ucomp_avg_ctl,vcomp_avg - vcomp_avg_ctl,gph_avg - gph_avg_ctl,
	'slp','m',landmaskxr,veclen=10,level=37,units_numerator = 'm', units_denom = 's', save = True)
winds_one_level(outdir,runmin,runmax,'870hPa_gph_winds_monthlydata_avg_',ucomp_avg,vcomp_avg,gph_avg,
	'slp','m',landmaskxr,veclen=10.,level=37,units_numerator = 'm', units_denom = 's', save = True)
winds_one_level(outdir,ctl_runmin,ctl_runmax,'870hPa_gph_winds_monthlydata_ctl_',ucomp_avg_ctl,vcomp_avg_ctl,gph_avg_ctl,
	'slp','m',landmaskxr,veclen=10.,level=37,units_numerator = 'm', units_denom = 's', save = True)




# winds + geopoetential height @ 200hPa

[gph,gph_avg,gph_seasonal_avg,gph_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'height','m', level = 15) # geopotential height at 200 hPa
[gph_ctl,gph_avg_ctl,gph_seasonal_avg_ctl,gph_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'height','m', level = 15) # geopotential height at 200 hPa

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,gph_avg,area_array,'m','200hPa_geopo_height_avg','slp',landmaskxr, nmb_contours = 10, minval = 10900, maxval = 11100)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,gph_avg_ctl,area_array,'m','200hPa_geopo_height_ctl','slp',landmaskxr, nmb_contours = 10, minval = 10900, maxval = 11100)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,gph_avg - gph_avg_ctl,area_array,'m','200hPa_geopo_height_avg_minus_ctl','slp',landmaskxr, nmb_contours = 8, minval = 180., maxval = 200.)

[ucomp,ucomp_avg,ucomp_seasonal_avg,ucomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'ucomp','m/s', level = 15)
[vcomp,vcomp_avg,vcomp_seasonal_avg,vcomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'vcomp','m/s', level = 15)
[ucomp_ctl,ucomp_avg_ctl,ucomp_seasonal_avg_ctl,ucomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'ucomp','m/s', level = 15)
[vcomp_ctl,vcomp_avg_ctl,vcomp_seasonal_avg_ctl,vcomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'vcomp','m/s', level = 15)

winds_one_level(outdir,runmin,runmax,'200hPa_gph_winds_avg_minus_ctl_monthlydata_',ucomp_avg - ucomp_avg_ctl,vcomp_avg - vcomp_avg_ctl,gph_avg - gph_avg_ctl,
	'slp','m',landmaskxr,veclen=10,level=15,units_numerator = 'm', units_denom = 's', save = True)
winds_one_level(outdir,runmin,runmax,'200hPa_gph_winds_monthlydata_avg_',ucomp_avg,vcomp_avg,gph_avg,
	'slp','m',landmaskxr,veclen=10.,level=15,units_numerator = 'm', units_denom = 's', save = True)
winds_one_level(outdir,ctl_runmin,ctl_runmax,'200hPa_gph_winds_monthlydata_ctl_',ucomp_avg_ctl,vcomp_avg_ctl,gph_avg_ctl,
	'slp','m',landmaskxr,veclen=10.,level=15,units_numerator = 'm', units_denom = 's', save = True)



############################## climatology plots ###############################



for i in range(0,12):
    clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,PE_month_avg_ctl[i,:,:],
                                        area_array,'mm/day',
                                        'PE_avg_ctl','PE_scale',landmaskxr,nmb_contours=10,
                                        minval = -3., maxval = 3.,month_annotate=(i+1))
    clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/PE_clim'+str(1000+i+1)+'.png',bbox_inches='tight')


# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(sphum_month_avg - sphum_month_avg_ctl)[i,:,:],
#                                         area_array,'kg/kg',
#                                         'sphum_avg_minus_ctl','rainnorm',landmaskxr,
#                                         minval = -0.005, maxval = 0.005,month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/q_avg_minus_ctl_lev'+str(level)+'_clim'+str(1000+i+1)+'.png',bbox_inches='tight')



# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(tsurf_month_avg_ctl)[i,:,:],
#                                         area_array,'K',
#                                         'T_ctl','temp',landmaskxr,nmb_contours=10,
#                                         minval = 260., maxval = 310., month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/T_ctl_clim'+str(1000+i+1)+'.png',bbox_inches='tight')


# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(net_sw_month_avg_ctl)[i,:,:],
#                                         area_array,'W/m2',
#                                         'SW_ctl','temp',landmaskxr,nmb_contours=10,
#                                         minval = 260., maxval = 310., month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/SW_ctl_clim'+str(1000+i+1)+'.png',bbox_inches='tight')




# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(net_lhe_month_avg - net_lhe_month_avg_ctl)[i,:,:],
#                                         area_array,'mm/day',
#                                         'E_avg_minus_ctl','rainnorm',landmaskxr,nmb_contours=10,
#                                         minval = -3., maxval = 3.,month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/E-Ectl_clim'+str(1000+i+1)+'.png',bbox_inches='tight')




# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(precipitation_month_avg - precipitation_month_avg_ctl)[i,:,:],
#                                         area_array,'mm/day',
#                                         'P_avg_minus_ctl','rainnorm',landmaskxr,nmb_contours=10,
#                                         minval = -3., maxval = 3.,month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/P-Pctl_clim'+str(1000+i+1)+'.png',bbox_inches='tight')

# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(net_lhe_month_avg_ctl)[i,:,:],
#                                         area_array,'mm/day',
#                                         'E_ctl','fromwhite',landmaskxr,nmb_contours=10,
#                                         minval = 0., maxval = 8., month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/E_ctl_clim'+str(1000+i+1)+'.png',bbox_inches='tight')

# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(precipitation)[i,:,:],
#                                         area_array,'mm/day',
#                                         'P_ctl','fromwhite',landmaskxr,nmb_contours=10,
#                                         minval = 0., maxval = 8., month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/P_ctl_clim'+str(1000+i+1)+'.png',bbox_inches='tight')




# # any_configuration_plot(outdir,runmin,runmax,-90.,90.,flux_oceanq_avg_ctl,area_array,'W/m^2','ocean_heat_transport_ctl','tempdiff',landmaskxr,minval=-200,maxval=200)

# # for i in range(0,12):
# #     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(flux_oceanq_month_avg_ctl)[i,:,:],
# #                                         area_array,'W/m^2',
# #                                         'qflux_ctl','tempdiff',landmaskxr,nmb_contours=5,
# #                                         minval = -100., maxval = 100., month_annotate=(i+1))
# #     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/qflux_ctl_clim'+str(1000+i+1)+'.png',bbox_inches='tight')


# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(precipitation_month_avg)[i,:,:],
#                                         area_array,'mm/day',
#                                         'P_avg','fromwhite',landmaskxr,nmb_contours=10,
#                                         minval = 0., maxval = 8., month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/P_avg_clim'+str(1000+i+1)+'.png',bbox_inches='tight')


# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(net_lhe_month_avg)[i,:,:],
#                                         area_array,'mm/day',
#                                         'E_avg','fromwhite',landmaskxr,nmb_contours=10,
#                                         minval = 0., maxval = 8., month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/E_avg_clim'+str(1000+i+1)+'.png',bbox_inches='tight')


for i in range(0,12):
    clim_plot = any_configuration_plot(outdir,runmin,runmax,-90.,90.,PE_month_avg[i,:,:],area_array,'mm/day',
                                        'PE_avg','PE_scale',landmaskxr,nmb_contours=10,
                                        minval = -3., maxval = 3.,month_annotate=(i+1))
    clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/PE_clim'+str(2000+i+1)+'.png',bbox_inches='tight')

os.system('convert -delay 100 /scratch/mp586/Code/Graphics/'+outdir+'/PE_clim*.png /scratch/mp586/Code/Graphics/'+outdir+'/PE_clim_animation.gif')


for i in range(0,12):
    clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(PE_month_avg - PE_month_avg_ctl)[i,:,:],
                                        area_array,'mm/day',
                                        'PE_avg_minus_ctl','PE_scale',landmaskxr,nmb_contours=10,
                                        minval = -1., maxval = 1.,month_annotate=(i+1))
    clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/PE_avg_minus_ctl_clim'+str(1000+i+1)+'.png',bbox_inches='tight')


# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,bucket_depth_month_avg_ctl[i,:,:],
#                                         area_array,'mm/day',
#                                         'bucket_depth_avg_ctl','bucket',landmaskxr,nmb_contours=10,
#                                         minval = 0., maxval = .15,month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/bucket_depth_clim'+str(1000+i+1)+'.png',bbox_inches='tight')

# for i in range(0,12):
#     clim_plot = any_configuration_plot(outdir,runmin,runmax,-90.,90.,bucket_depth_month_avg[i,:,:],area_array,'mm/day',
#                                         'bucket_depth_avg','bucket',landmaskxr,nmb_contours=10,
#                                         minval = 0., maxval = .15,month_annotate=(i+1))
#     clim_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/bucket_depth_clim'+str(2000+i+1)+'.png',bbox_inches='tight')



# for i in range(0,12):
#     delta_slp_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,(slp_month_avg - slp_month_avg_ctl)[i,:,:],area_array,'hPa','slp_avg_minus_ctl','slp',landmaskxr,minval = -0.01, maxval = 0.01, month_annotate=(i+1))
#     delta_slp_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/Delta_slp'+str(1000+i+1)+'.png',bbox_inches='tight')

# os.system('convert -delay 100 /scratch/mp586/Code/Graphics/'+outdir+'/Delta_slp*.png /scratch/mp586/Code/Graphics/'+outdir+'/Delta_slp_animation.gif')


# avg_slp = slp_avg.mean()

# for i in range(0,12):
#     slp_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,slp_month_avg[i,:,:] - avg_slp,area_array,'hPa','slp_anomaly_avg','slp',landmaskxr,minval = - 0.03, maxval = 0.03, month_annotate=(i+1))
#     slp_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/slp_anomaly_month'+str(1000+i+1)+'.png',bbox_inches='tight')

# os.system('convert -delay 100 /scratch/mp586/Code/Graphics/'+outdir+'/slp_anomaly_month*.png /scratch/mp586/Code/Graphics/'+outdir+'/slp_animation.gif')


########## not good to have 6hrly timestep minus February control because veen the daily cycle will show up in this. .... Should make a climatology of the 6 hourly data and then compare the pertubed at each timestep to that climatology #####################

# for i in range(0,24):
#     evolution_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,tsurf_6hrly[i,:,:] - tsurf_month_avg_ctl[0,:,:],
#                                         area_array,'K',
#                                         'T_pert_minus_February_climatology_6hrlydata','tempdiff',landmaskxr,nmb_contours=10,
#                                         minval = -4., maxval = 4.)
#     evolution_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/T_pert_6hrlydata_minus_February_ctl_evolution_hour'+str(1000+6*i+1)+'.png',bbox_inches='tight')

# for i in range(0,24):
#     evolution_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,precipitation_6hrly[i,:,:] - precipitation_month_avg_ctl[0,:,:],
#                                         area_array,'mm/d',
#                                         'P_pert_minus_February_climatology_6hrlydata','rainnorm',landmaskxr,nmb_contours=10,
#                                         minval = -5., maxval = 5.)
#     evolution_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/P_pert_6hrlydata_minus_February_ctl_evolution_hour'+str(1000+6*i+1)+'.png',bbox_inches='tight')

# for i in range(0,24):
#     evolution_plot = any_configuration_plot(outdir,ctl_runmin,ctl_runmax,-90.,90.,sphum[i,:,:] - sphum_month_avg_ctl[0,:,:],
#                                         area_array,'kg/kg',
#                                         'sphum_pert_minus_February_climatology_6hrlydata','rainnorm',landmaskxr,nmb_contours=0,
#                                         minval = -0.01, maxval = 0.01)
#     evolution_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/sphum_level_'+str(level)+'_pert_6hrlydata_minus_February_ctl_evolution_hour'+str(1000+6*i+1)+'.png',bbox_inches='tight')





##############################################################################################
# Moisture flux with MONTHLY data

# [ucomp,ucomp_avg,ucomp_seasonal_avg,ucomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'ucomp','m/s', level = level)
# [vcomp,vcomp_avg,vcomp_seasonal_avg,vcomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'vcomp','m/s', level = level)
# [ucomp_ctl,ucomp_avg_ctl,ucomp_seasonal_avg_ctl,ucomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'ucomp','m/s', level = level)
# [vcomp_ctl,vcomp_avg_ctl,vcomp_seasonal_avg_ctl,vcomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'vcomp','m/s', level = level)

# qu= (ucomp*sphum)
# [qu,qu_total,qu_seasonal,qu_month_avg,time] = make_var_seasonal(qu)
# qv= (vcomp*sphum)
# [qv,qv_total,qv_seasonal,qv_month_avg,time] = make_var_seasonal(qv)
# qu_ctl = (ucomp_ctl*sphum_ctl)
# [qu_ctl,qu_total_ctl,qu_ctl_seasonal,qu_ctl_month_avg,time] = make_var_seasonal(qu_ctl)
# qv_ctl = (vcomp_ctl*sphum_ctl)
# [qv_ctl,qv_total_ctl,qv_ctl_seasonal,qv_ctl_month_avg,time] = make_var_seasonal(qv_ctl)


# any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(qu_seasonal - qu_ctl_seasonal),area_array,'kgm/kgs','qu_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-.05,maxval=.05)
# any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(qu_seasonal),area_array,'kgm/kgs','qu_avg_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)
# any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(qu_ctl_seasonal),area_array,'kgm/kgs','qu_ctl_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(qu_total - qu_total_ctl),area_array,'kgm/kgs','qu_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-.05,maxval=.05)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(qu_total),area_array,'kgm/kgs','qu_avg_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(qu_total_ctl),area_array,'kgm/kgs','qu_ctl_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)






##############################################################################################
# Moisture flux as model output 

level = 37 #37

[ucomp,ucomp_avg,ucomp_seasonal_avg,ucomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'ucomp','m/s', level = level)
[vcomp,vcomp_avg,vcomp_seasonal_avg,vcomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'vcomp','m/s', level = level)
[ucomp_ctl,ucomp_avg_ctl,ucomp_seasonal_avg_ctl,ucomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'ucomp','m/s', level = level)
[vcomp_ctl,vcomp_avg_ctl,vcomp_seasonal_avg_ctl,vcomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'vcomp','m/s', level = level)


any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(ucomp_seasonal_avg),area_array,'m/s','ucomp_avg_lev'+str(level),'slp',landmaskxr,minval=-10.,maxval=10.)
any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(ucomp_seasonal_avg_ctl),area_array,'m/s','ucomp_ctl_lev'+str(level),'slp',landmaskxr,minval=-10.,maxval=10.)
any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(ucomp_seasonal_avg - ucomp_seasonal_avg_ctl),area_array,'m/s','ucomp_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-2.,maxval=2.)

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(ucomp_avg),area_array,'m/s','ucomp_avg_lev'+str(level),'slp',landmaskxr,minval=-10.,maxval=10.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(ucomp_avg_ctl),area_array,'m/s','ucomp_ctl_lev'+str(level),'slp',landmaskxr,minval=-10.,maxval=10.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(ucomp_avg - ucomp_avg_ctl),area_array,'m/s','ucomp_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-2.,maxval=2.)

[sphum_u,sphum_u_avg,sphum_u_seasonal_avg,sphum_u_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'sphum_u','kgm/kgs', level = level)
[sphum_v,sphum_v_avg,sphum_v_seasonal_avg,sphum_v_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'sphum_v','kgm/kgs', level = level)
[sphum_u_ctl,sphum_u_avg_ctl,sphum_u_seasonal_avg_ctl,sphum_u_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'sphum_u','kgm/kgs', level = level)
[sphum_v_ctl,sphum_v_avg_ctl,sphum_v_seasonal_avg_ctl,sphum_v_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'sphum_v','kgm/kgs', level = level)

any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(sphum_u_seasonal_avg - sphum_u_seasonal_avg_ctl),area_array,'kgm/kgs','sphum_u_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-.05,maxval=.05)
any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(sphum_u_seasonal_avg),area_array,'kgm/kgs','sphum_u_avg_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)
any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(sphum_u_seasonal_avg_ctl),area_array,'kgm/kgs','sphum_u_ctl_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)


any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sphum_u_avg - sphum_u_avg_ctl),area_array,'kgm/kgs','sphum_u_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-.05,maxval=.05)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sphum_u_avg),area_array,'kgm/kgs','sphum_u_avg_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sphum_u_avg_ctl),area_array,'kgm/kgs','sphum_u_ctl_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)


level = 39 #37

[ucomp,ucomp_avg,ucomp_seasonal_avg,ucomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'ucomp','m/s', level = level)
[vcomp,vcomp_avg,vcomp_seasonal_avg,vcomp_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'vcomp','m/s', level = level)
[ucomp_ctl,ucomp_avg_ctl,ucomp_seasonal_avg_ctl,ucomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'ucomp','m/s', level = level)
[vcomp_ctl,vcomp_avg_ctl,vcomp_seasonal_avg_ctl,vcomp_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'vcomp','m/s', level = level)


any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(ucomp_seasonal_avg),area_array,'m/s','ucomp_avg_lev'+str(level),'slp',landmaskxr,minval=-10.,maxval=10.)
any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(ucomp_seasonal_avg_ctl),area_array,'m/s','ucomp_ctl_lev'+str(level),'slp',landmaskxr,minval=-10.,maxval=10.)
any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(ucomp_seasonal_avg - ucomp_seasonal_avg_ctl),area_array,'m/s','ucomp_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-2.,maxval=2.)

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(ucomp_avg),area_array,'m/s','ucomp_avg_lev'+str(level),'slp',landmaskxr,minval=-10.,maxval=10.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(ucomp_avg_ctl),area_array,'m/s','ucomp_ctl_lev'+str(level),'slp',landmaskxr,minval=-10.,maxval=10.)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(ucomp_avg - ucomp_avg_ctl),area_array,'m/s','ucomp_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-2.,maxval=2.)

[sphum_u,sphum_u_avg,sphum_u_seasonal_avg,sphum_u_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'sphum_u','kgm/kgs', level = level)
[sphum_v,sphum_v_avg,sphum_v_seasonal_avg,sphum_v_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'sphum_v','kgm/kgs', level = level)
[sphum_u_ctl,sphum_u_avg_ctl,sphum_u_seasonal_avg_ctl,sphum_u_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'sphum_u','kgm/kgs', level = level)
[sphum_v_ctl,sphum_v_avg_ctl,sphum_v_seasonal_avg_ctl,sphum_v_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'sphum_v','kgm/kgs', level = level)

any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(sphum_u_seasonal_avg - sphum_u_seasonal_avg_ctl),area_array,'kgm/kgs','sphum_u_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-.05,maxval=.05)
any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(sphum_u_seasonal_avg),area_array,'kgm/kgs','sphum_u_avg_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)
any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(sphum_u_seasonal_avg_ctl),area_array,'kgm/kgs','sphum_u_ctl_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sphum_u_avg - sphum_u_avg_ctl),area_array,'kgm/kgs','sphum_u_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-.05,maxval=.05)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sphum_u_avg),area_array,'kgm/kgs','sphum_u_avg_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sphum_u_avg_ctl),area_array,'kgm/kgs','sphum_u_ctl_lev'+str(level),'slp',landmaskxr,minval=-.2,maxval=.2)




level = 15

[sphum_u,sphum_u_avg,sphum_u_seasonal_avg,sphum_u_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'sphum_u','kgm/kgs', level = level)
[sphum_v,sphum_v_avg,sphum_v_seasonal_avg,sphum_v_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'sphum_v','kgm/kgs', level = level)
[sphum_u_ctl,sphum_u_avg_ctl,sphum_u_seasonal_avg_ctl,sphum_u_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'sphum_u','kgm/kgs', level = level)
[sphum_v_ctl,sphum_v_avg_ctl,sphum_v_seasonal_avg_ctl,sphum_v_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'sphum_v','kgm/kgs', level = level)

any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(sphum_u_seasonal_avg - sphum_u_seasonal_avg_ctl),area_array,'kgm/kgs','sphum_u_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-.05,maxval=.05)
any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(sphum_u_seasonal_avg),area_array,'kgm/kgs','sphum_u_avg_lev'+str(level),'slp',landmaskxr,minval=-.002,maxval=.002)
any_configuration_plot_seasonal(outdir,runmin,runmax,-90.,90.,(sphum_u_seasonal_avg_ctl),area_array,'kgm/kgs','sphum_u_ctl_lev'+str(level),'slp',landmaskxr,minval=-.002,maxval=.002)

any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sphum_u_avg - sphum_u_avg_ctl),area_array,'kgm/kgs','sphum_u_avg_minus_ctl_lev'+str(level),'slp',landmaskxr,minval=-.003,maxval=.003)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sphum_u_avg),area_array,'kgm/kgs','sphum_u_avg_lev'+str(level),'slp',landmaskxr,minval=-.003,maxval=.003)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(sphum_u_avg_ctl),area_array,'kgm/kgs','sphum_u_ctl_lev'+str(level),'slp',landmaskxr,minval=-.003,maxval=.003)




[omega,omega_avg,omega_seasonal_avg,omega_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'omega','Pa/s', level = 27) # geopotential height at 500 hPa
[omega_ctl,omega_avg_ctl,omega_seasonal_avg_ctl,omega_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'omega','Pa/s', level = 27) # geopotential height at 500 hPa
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(omega_avg_ctl),area_array,'Pa/s','omega_ctl_lev27','rainnorm',landmaskxr, minval = -0.1, maxval = 0.1)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(omega_avg),area_array,'Pa/s','omega_avg_lev27','rainnorm',landmaskxr, minval = -0.1, maxval = 0.1)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(omega_avg - omega_avg_ctl),area_array,'Pa/s','omega_avg_minus_ctl_lev27','rainnorm',landmaskxr, minval = -0.1, maxval = 0.1)
any_configuration_plot(outdir,runmin,runmax,-90.,90.,(omega_avg - omega_avg_ctl),area_array,'Pa/s','omega_avg_minus_ctl_lev27','rainnorm',landmaskxr, minval = -0.03, maxval = 0.03)

















# qu decomposition: qu_new = qu_old + u_old * delta_sphum + q_old * delta_u + delta_u*delta_sphum -- again don't use uctl * deltaq on each month but the climatologies because the delta in month 38 is not the corresponding one to uctl (month38)

delta_sphum = sphum - sphum_ctl
[delta_sphum,delta_sphum_total,delta_sphum_seasonal,delta_sphum_month_avg,time] = make_var_seasonal(delta_sphum)

delta_ucomp = ucomp - ucomp_ctl
[delta_ucomp,delta_ucomp_total,delta_ucomp_seasonal,delta_ucomp_month_avg,time] = make_var_seasonal(delta_ucomp)

delta_vcomp = vcomp - vcomp_ctl
[delta_vcomp,delta_vcomp_total,delta_vcomp_seasonal,delta_vcomp_month_avg,time] = make_var_seasonal(delta_vcomp)

uctl_dq_month_avg = ucomp_month_avg_ctl * delta_sphum_month_avg 
vctl_dq_month_avg = vcomp_month_avg_ctl * delta_sphum_month_avg 

qctl_du_month_avg = sphum_month_avg_ctl * delta_ucomp_month_avg 
qctl_dv_month_avg = sphum_month_avg_ctl * delta_vcomp_month_avg 

deltaq_deltau_month_avg = delta_sphum_month_avg * delta_ucomp_month_avg
deltaq_deltav_month_avg = delta_sphum_month_avg * delta_vcomp_month_avg


# for i in range(0,12):

#     month_plot = winds_one_level(outdir,runmin,runmax,'qctl_deltau',qctl_du_month_avg[i,:,:],qctl_dv_month_avg[i,:,:],(PE_month_avg-PE_month_avg_ctl)[i,:,:],'PE_scale','mm/d',-4.,4.,landmaskxr,veclen=0.01,level=level,units_numerator = 'kg m', units_denom = 'kg s')

#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/qctl_deltau_level='+str(level)+'_clim'+str(1000+i+1)+'.png')
#     plt.close()



# for i in range(0,12):

#     month_plot = winds_one_level(outdir,runmin,runmax,'uctl_deltaq',uctl_dq_month_avg[i,:,:],vctl_dq_month_avg[i,:,:],(PE_month_avg-PE_month_avg_ctl)[i,:,:],'PE_scale','mm/d',-4.,4.,landmaskxr,veclen=0.01,level=level,units_numerator = 'kg m', units_denom = 'kg s')

#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/uctl_deltaq_level='+str(level)+'_clim'+str(1000+i+1)+'.png')
#     plt.close()



# for i in range(0,12):

#     month_plot = winds_one_level(outdir,runmin,runmax,'deltau_deltaq',deltaq_deltau_month_avg[i,:,:],deltaq_deltav_month_avg[i,:,:],(PE_month_avg-PE_month_avg_ctl)[i,:,:],'PE_scale','mm/d',-4.,4.,landmaskxr,veclen=0.01,level=level,units_numerator = 'kg m', units_denom = 'kg s')

#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/deltau_deltaq_level='+str(level)+'_clim'+str(1000+i+1)+'.png')
#     plt.close()


winds_one_level(outdir,runmin,runmax,'qctl_deltau_monthlydata_avg',qctl_du_month_avg.mean('month'),qctl_dv_month_avg.mean('month'),(PE_month_avg-PE_month_avg_ctl).mean('month'),'PE_scale','mm/d',-4.,4.,landmaskxr,veclen=0.01,level=level,units_numerator = 'kg m', units_denom = 'kg s', save = True)

winds_one_level(outdir,runmin,runmax,'uctl_deltaq_monthlydata_avg',uctl_dq_month_avg.mean('month'),vctl_dq_month_avg.mean('month'),(PE_month_avg-PE_month_avg_ctl).mean('month'),'PE_scale','mm/d',-4.,4.,landmaskxr,veclen=0.01,level=level,units_numerator = 'kg m', units_denom = 'kg s', save = True)

qu_stationary = (ucomp_avg*sphum_avg)
qv_stationary = (vcomp_avg*sphum_avg)

qu_stationary_ctl = (ucomp_avg_ctl*sphum_avg_ctl)
qv_stationary_ctl = (vcomp_avg_ctl*sphum_avg_ctl)
# annual mean plots 
winds_one_level(outdir,runmin,runmax,'moisture_flux_total_avg_minus_ctl_monthlydata_',qu_total - qu_total_ctl,qv_total - qv_total_ctl,(PE_avg-PE_avg_ctl),'PE_scale','mm/d',-2.,2.,landmaskxr,veclen=0.01,level=level,units_numerator = 'kg m', units_denom = 'kg s', save = True)

winds_one_level(outdir,runmin,runmax,'moisture_flux_total_monthlydata_',qu_total,qv_total,precipitation_avg,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s', save = True)

winds_one_level(outdir,ctl_runmin,ctl_runmax,'moisture_flux_total_monthlydata_ctl_',qu_total_ctl,qv_total_ctl,precipitation_avg_ctl,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s', save = True)


winds_one_level(outdir,runmin,runmax,'moisture_flux_stationary_monthlydata_Pavg_',qu_stationary,qv_stationary,precipitation_avg,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s', save = True)

winds_one_level(outdir,ctl_runmin,ctl_runmax,'moisture_flux_stationary_monthlydata_ctl_Pctl_',qu_stationary_ctl,qv_stationary_ctl,precipitation_avg_ctl,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s', save = True)


winds_one_level(outdir,runmin,runmax,'winds_avg_minus_ctl_monthlydata_',ucomp_avg - ucomp_avg_ctl,vcomp_avg - vcomp_avg_ctl,precipitation_avg - precipitation_avg_ctl,'rainnorm','mm/d',-2.,2.,landmaskxr,veclen=1,level=level,units_numerator = 'm', units_denom = 's', save = True)

winds_one_level(outdir,runmin,runmax,'winds_monthlydata_',ucomp_avg,vcomp_avg,precipitation_avg,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=10,level=level,units_numerator = 'm', units_denom = 's', save = True)

winds_one_level(outdir,ctl_runmin,ctl_runmax,'winds_monthlydata_ctl_',ucomp_avg_ctl,vcomp_avg_ctl,precipitation_avg_ctl,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=10,level=level,units_numerator = 'm', units_denom = 's', save = True)





####################### seasonal plots

winds_seasons_one_level(ucomp_seasonal_avg,vcomp_seasonal_avg,'u_avg',level,precipitation_seasonal_avg,'fromwhite','mm/d',0.,20.,landmaskxr,outdir,runmin,runmax,units_numerator = 'm', units_denom = 's',veclen=30.)
winds_seasons_one_level(ucomp_seasonal_avg_ctl,vcomp_seasonal_avg_ctl,'u_ctl',level,precipitation_seasonal_avg_ctl,'fromwhite','mm/d',0.,20.,landmaskxr,outdir,runmin,runmax,units_numerator = 'm', units_denom = 's',veclen=30.)
winds_seasons_one_level(ucomp_seasonal_avg - ucomp_seasonal_avg_ctl,vcomp_seasonal_avg - vcomp_seasonal_avg_ctl,'u_avg_minus_ctl',level,precipitation_seasonal_avg - precipitation_seasonal_avg_ctl,'rainnorm','mm/d',-5.,5.,landmaskxr,outdir,runmin,runmax,units_numerator = 'm', units_denom = 's',veclen=3., scale = 10.)


winds_seasons_one_level(qu_seasonal,qv_seasonal,'qu_avg',level,PE_seasonal_avg,'PE_scale','mm/d',-10.,10.,landmaskxr,outdir,runmin,runmax,units_numerator = 'kg m', units_denom = 'kg s',veclen=0.5, scale = 1.)
winds_seasons_one_level(qu_ctl_seasonal,qv_ctl_seasonal,'qu_ctl',level,PE_seasonal_avg_ctl,'PE_scale','mm/d',-10.,10.,landmaskxr,outdir,runmin,runmax,units_numerator = 'kg m', units_denom = 'kg s',veclen=0.5, scale = 1.)
winds_seasons_one_level(qu_seasonal - qu_ctl_seasonal,qv_seasonal - qv_ctl_seasonal,'qu_avg_minus_ctl',level,PE_seasonal_avg - PE_seasonal_avg_ctl,'PE_scale','mm/d',-5.,5.,landmaskxr,outdir,runmin,runmax,units_numerator = 'kgm', units_denom = 'kgs',veclen=0.05, scale = 0.2)






# ########## monthly plots 
# for i in range(0,12):

#     month_plot = winds_one_level(outdir,runmin,runmax,'moisture_flux_avg_minus_ctl_monthlydata_PE_minus_PEctl',(qu_month_avg - qu_ctl_month_avg)[i,:,:],(qv_month_avg - qv_ctl_month_avg)[i,:,:],(PE_month_avg-PE_month_avg_ctl)[i,:,:],'PE_scale','mm/d',-4.,4.,landmaskxr,veclen=0.01,level=level,units_numerator = 'kg m', units_denom = 'kg s')

#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/qu_level='+str(level)+'_avg_minus_ctl_clim'+str(1000+i+1)+'.png')
#     plt.close()


# for i in range(0,12):

#     month_plot = winds_one_level(outdir,runmin,runmax,'moisture_flux_relative_change_monthlydata_PE_minus_PEctl',((qu_month_avg - qu_ctl_month_avg)/(qu_ctl_month_avg))[i,:,:],((qv_month_avg - qv_ctl_month_avg)/qv_ctl_month_avg)[i,:,:],(PE_month_avg-PE_month_avg_ctl)[i,:,:],'PE_scale','mm/d',-2.,2.,landmaskxr,veclen=1,level=level,units_numerator = '1', units_denom = '1')

#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/qu_level='+str(level)+'_relative_change_monthlydata_PE-PEctl_clim'+str(1000+i+1)+'.png')



# for i in range(0,12):

#     month_plot = winds_one_level(outdir,runmin,runmax,'moisture_flux_total_avg',(qu_month_avg)[i,:,:],(qv_month_avg)[i,:,:],PE_month_avg[i,:,:],'PE_scale','mm/d',-4.,4.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s')

#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/qu_level='+str(level)+'_avg_clim'+str(1000+i+1)+'.png')
#     plt.close()


# for i in range(0,12):

#     month_plot = winds_one_level(outdir,runmin,runmax,'moisture_flux_total_ctl',(qu_ctl_month_avg)[i,:,:],(qv_ctl_month_avg)[i,:,:],PE_month_avg_ctl[i,:,:],'PE_scale','mm/d',-4.,4.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s')

#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/qu_level='+str(level)+'_ctl_clim'+str(1000+i+1)+'.png')
#     plt.close()




# for i in range(0,12):

#     month_plot = winds_one_level(outdir,runmin,runmax,'winds_avg_minus_ctl_monthlydata_PE_minus_PE_ctl_',(ucomp_month_avg - ucomp_month_avg_ctl)[i,:,:],(vcomp_month_avg - vcomp_month_avg_ctl)[i,:,:],(PE_month_avg-PE_month_avg_ctl)[i,:,:],'PE_scale','mm/d',-2.,2.,landmaskxr,veclen=0.5,level=level,units_numerator = '1', units_denom = '1')

#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/winds_avg_minus_ctl_monthlydata_level='+str(level)+'_PE_minus_PE_ctl_clim'+str(1000+i+1)+'.png')
#     plt.close()


# for i in range(0,12):

#     month_plot = winds_one_level(outdir,runmin,runmax,'winds_avg_monthlydata_PE_avg_',(ucomp_month_avg)[i,:,:],(vcomp_month_avg)[i,:,:],(PE_month_avg)[i,:,:],'PE_scale','mm/d',-4.,4.,landmaskxr,veclen=10,level=level,units_numerator = 'm', units_denom = 's')

#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/winds_avg_monthlydata_level='+str(level)+'_PE_avg_clim'+str(1000+i+1)+'.png')

#     plt.close()

# for i in range(0,12):

#     month_plot = winds_one_level(outdir,runmin,runmax,'winds_ctl_monthlydata_PE_avg_',(ucomp_month_avg_ctl)[i,:,:],(vcomp_month_avg_ctl)[i,:,:],(PE_month_avg_ctl)[i,:,:],'PE_scale','mm/d',-4.,4.,landmaskxr,veclen=10,level=level,units_numerator = 'm', units_denom = 's')

#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+outdir+'/winds_ctl_monthlydata_level='+str(level)+'_PE_ctl_clim'+str(1000+i+1)+'.png')

#     plt.close()

################################################################################################################




####### LAND SEA WARMING CONTRAST ####### 

tropicalavg_deltaT = area_weighted_avg((tsurf_avg - tsurf_avg_ctl),area_array,landmaskxr,'all_sfcs',minlat = -30., maxlat = 30.)

land_sea_contrast(tsurf_avg, tsurf_avg_ctl, area_array, landmaskxr, outdir, runmin, runmax, 'K', 'land_sea_warming_contrast', 'tempdiff', minval = None, maxval = None)



####################################
# Moisture flux 6 hourly data

ctl_runmin_6hrly = 121
ctl_runmax_6hrly = 481

runmin_6hrly = 1
runmax_6hrly = 13

[sphum_6hrly,sphum_6hrly_avg,time]=seasonal_surface_variable_6hrly(testdir,model,runmin_6hrly,runmax_6hrly,'sphum','kg/kg',level=level)
#[sphum_6hrly_ctl,sphum_6hrly_avg_ctl,time]=seasonal_surface_variable_6hrly(control_dir,ctl_model,ctl_runmin_6hrly,ctl_runmax_6hrly,'sphum','kg/kg',level=level)

[tsurf_6hrly,tsurf_6hrly_avg,time]=seasonal_surface_variable_6hrly(testdir,model,runmin_6hrly,runmax_6hrly,'t_surf','K')
#[tsurf_6hrly_ctl,tsurf_6hrly_avg_ctl,time]=seasonal_surface_variable_6hrly(control_dir,ctl_model,ctl_runmin_6hrly,ctl_runmax_6hrly,'tsurf','K')

[precipitation_6hrly,precipitation_6hrly_avg,time]=seasonal_surface_variable_6hrly(testdir,model,runmin_6hrly,runmax_6hrly,'precipitation','mm/d',factor=86400.)
#[precipitation_6hrly_ctl,precipitation_6hrly_avg_ctl,time]=seasonal_surface_variable_6hrly(control_dir,ctl_model,ctl_runmin_6hrly,ctl_runmax_6hrly,'precipitation','mm/d',factor=86400.)

# [ucomp_6hrly,ucomp_6hrly_avg,time]=seasonal_surface_variable_6hrly(testdir,model,runmin_6hrly,runmax_6hrly,'ucomp','m/s',level=level)
# [vcomp_6hrly,vcomp_6hrly_avg,time]=seasonal_surface_variable_6hrly(testdir,model,runmin_6hrly,runmax_6hrly,'vcomp','m/s',level=level)
# [ucomp_6hrly_ctl,ucomp_6hrly_avg_ctl,time]=seasonal_surface_variable_6hrly(control_dir,ctl_model,ctl_runmin_6hrly,ctl_runmax_6hrly,'ucomp','m/s',level=level)
# [vcomp_6hrly_ctl,vcomp_6hrly_avg_ctl,time]=seasonal_surface_variable_6hrly(control_dir,ctl_model,ctl_runmin_6hrly,ctl_runmax_6hrly,'vcomp','m/s',level=level)


# any_configuration_plot(outdir,runmin_6hrly,runmax_6hrly,-90.,90.,(precipitation_6hrly_avg - precipitation_6hrly_avg_ctl),area_array,'mm/day','P_6hrly_avg_minus_ctl','rainnorm',landmaskxr,minval=-2.,maxval=2.)

# qu_total = (ucomp_6hrly*sphum_6hrly).mean('time')
# qv_total = (vcomp_6hrly*sphum_6hrly).mean('time')
# qu_total_ctl = (ucomp_6hrly_ctl*sphum_6hrly_ctl).mean('time')
# qv_total_ctl = (vcomp_6hrly_ctl*sphum_6hrly_ctl).mean('time')

# qu_stationary = (ucomp_6hrly_avg*sphum_6hrly_avg)
# qv_stationary = (vcomp_6hrly_avg*sphum_6hrly_avg)

# qu_stationary_ctl = (ucomp_6hrly_avg_ctl*sphum_6hrly_avg_ctl)
# qv_stationary_ctl = (vcomp_6hrly_avg_ctl*sphum_6hrly_avg_ctl)

# winds_one_level(outdir,runmin_6hrly,runmax_6hrly,'moisture_flux_total_',qu_total,qv_total,precipitation_6hrly_avg,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s')
# winds_one_level(outdir,ctl_runmin_6hrly,ctl_runmax_6hrly,'moisture_flux_total_ctl_',qu_total_ctl,qv_total_ctl,precipitation_6hrly_avg_ctl,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s')

# winds_one_level(outdir,runmin_6hrly,runmax_6hrly,'moisture_flux_stationary_',qu_stationary,qv_stationary,precipitation_6hrly_avg,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s')

# winds_one_level(outdir,runmin_6hrly,runmax_6hrly,'moisture_flux_eddy_contribution_',((qu_total - qu_stationary)/qu_total),((qv_total - qv_stationary)/qv_total), precipitation_6hrly_avg,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s')

# winds_one_level(outdir,ctl_runmin_6hrly,ctl_runmax_6hrly,'moisture_flux_stationary_ctl_',qu_stationary_ctl,qv_stationary_ctl,precipitation_6hrly_avg_ctl,'fromwhite','mm/d',0.,8.,landmaskxr,veclen=0.1,level=level,units_numerator = 'kg m', units_denom = 'kg s')


# winds_one_level(outdir,runmin_6hrly,runmax_6hrly,'moisture_flux_total_avg_minus_ctl_',qu_total - qu_total_ctl,qv_total - qv_total_ctl,precipitation_6hrly_avg - precipitation_6hrly_avg_ctl,'rainnorm','mm/d',-2.,2.,landmaskxr,veclen=0.01,level=level,units_numerator = 'kg m', units_denom = 'kg s')

# winds_one_level(outdir,runmin_6hrly,runmax_6hrly,'moisture_flux_stationary_avg_minus_ctl_',qu_stationary - qu_stationary_ctl,qv_stationary - qv_stationary_ctl,precipitation_6hrly_avg - precipitation_6hrly_avg_ctl,'rainnorm','mm/d',-2.,2.,landmaskxr,veclen=0.01,level=level,units_numerator = 'kg m', units_denom = 'kg s')



##### DECOMPOSITION OF PRECIPITATION CHANGE ######################

########## calculating the products of the climatologies, not at each monthly 'timestep'


# M_ctl = precipitation_ctl / sphum_ctl
# [M_ctl,M_ctl_avg,M_ctl_seasonal_avg,M_ctl_month_avg,time] = make_var_seasonal(M_ctl)
# M_new = precipitation / sphum
# [M_new,M_new_avg,M_new_seasonal_avg,M_new_month_avg,time] = make_var_seasonal(M_new)
# Delta_M = M_new_month_avg - M_ctl_month_avg
# Delta_P_circ = sphum_month_avg_ctl * Delta_M
# Delta_P_q = M_ctl_month_avg * (sphum_month_avg - sphum_month_avg_ctl)
# Delta_P_cross = (sphum_month_avg - sphum_month_avg_ctl) * (M_new_month_avg - M_ctl_month_avg)
# Delta_P_sum = Delta_P_cross + Delta_P_q + Delta_P_circ
# Delta_P_sum_avg = Delta_P_sum.mean(axis=0)
# Diff_DeltaPs = (precipitation_avg - precipitation_avg_ctl) - Delta_P_sum_avg
# #print('Diff_DeltaPs.max()'+str(Diff_DeltaPs.max()))
# #print('Diff_DeltaPs.min()'+str(Diff_DeltaPs.min()))
# #print('Diff_DeltaPs.mean()'+str(Diff_DeltaPs.mean()))

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_circ.mean('month'),area_array,'mm/day','Delta_P_circ','rainnorm',landmaskxr,minval=-2.,maxval=2.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_q.mean('month'),area_array,'mm/day','Delta_P_q','rainnorm',landmaskxr,minval=-2.,maxval=2.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_cross.mean('month'),area_array,'mm/day','Delta_P_cross','rainnorm',landmaskxr,minval=-2.,maxval=2.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Diff_DeltaPs,area_array,'mm/day','Diff_Delta_Ps','rainnorm',landmaskxr,minval=-2.,maxval=2.)

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_circ.mean('month'),area_array,'mm/day','Delta_P_circ_narrowcbar','rainnorm',landmaskxr,minval=-1.,maxval=1.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_q.mean('month'),area_array,'mm/day','Delta_P_q_narrowcbar','rainnorm',landmaskxr,minval=-1.,maxval=1.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_cross.mean('month'),area_array,'mm/day','Delta_P_cross_narrowcbar','rainnorm',landmaskxr,minval=-1.,maxval=1.)

# globavg_deltaT = area_weighted_avg((tsurf_avg - tsurf_avg_ctl),area_array,landmask,'all_sfcs')

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(Delta_M/globavg_deltaT).mean('month'),area_array,'mm/day/K','Delta_M_normalized','rainnorm',landmaskxr,minval=-40.,maxval=40) # change in circulation normalized by global mean T change # following Chadwick et al., 2013 (Fig. 8)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,sphum_avg - sphum_avg_ctl,area_array,'kg/kg','q_avg_minus_ctl_levlevel','rainnorm',landmaskxr) 
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,sphum_avg_ctl,area_array,'kg/kg','q_ctl_levlevel','fromwhite',landmaskxr,nmb_contours=10) 
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,sphum_avg,area_array,'kg/kg','q_avg_levlevel','fromwhite',landmaskxr,nmb_contours=10) 
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,M_ctl.mean('time'),area_array,'mm/day','M_ctl','fromwhite',landmaskxr)  
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,M_new.mean('time'),area_array,'mm/day','M_avg','fromwhite',landmaskxr) 
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(Delta_M).mean('month')/M_ctl_avg,area_array,' ','DeltaM_avg_div_M_ctl_avg','rainnorm',landmaskxr,minval=-1.0,maxval=1.0)

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((sphum_avg - sphum_avg_ctl)/sphum_avg_ctl),area_array,' ','Deltaq_div_q_ctl','rainnorm',landmaskxr)

###################################################################


################### Finding the level 'CH' were delta T over land and ocean is the same, (see Joshi et al., 2008) ###

# [temp,temp_avg,temp_seasonal_avg,temp_month_avg,temp_annual_avg,time]=seasonal_4D_variable(testdir,model,runmin,runmax,'temp','K')

# [temp_ctl,temp_ctl_avg,temp_ctl_seasonal_avg,temp_ctl_month_avg,temp_ctl_annual_avg,time]=seasonal_4D_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'temp','K')


# delta_temp_avg = temp_avg - temp_ctl_avg
# # global mean
# delta_temp_awave_ocean = xr.DataArray(area_weighted_avg_4D(delta_temp_avg,area_array_3D,landmaskxr,'ocean',minlat=-90.,maxlat=90.,axis=(1,2)))
# delta_temp_awave_land = xr.DataArray(area_weighted_avg_4D(delta_temp_avg,area_array_3D,landmaskxr,'land',minlat=-90.,maxlat=90.,axis=(1,2)))

# # tropical mean 
# delta_temp_awave_ocean_tropics = xr.DataArray(area_weighted_avg_4D(delta_temp_avg,area_array_3D,landmaskxr,'ocean',minlat=-30.,maxlat=30.,axis=(1,2)))
# delta_temp_awave_land_tropics = xr.DataArray(area_weighted_avg_4D(delta_temp_avg,area_array_3D,landmaskxr,'land',minlat=-30.,maxlat=30.,axis=(1,2)))

# levs = temp_avg.pres_lev

# fig, ax = plt.subplots(1,2,sharex = True, sharey=True,figsize=(25,10))
# ax[0].plot(delta_temp_awave_land_tropics,levs,'r',label = 'Delta T land (tropics)')
# ax[0].plot(delta_temp_awave_ocean_tropics,levs,'b',label = 'Delta T ocean (tropics)')

# ax[1].plot(delta_temp_awave_land,levs,'r',label = 'Delta T land (global)')
# ax[1].plot(delta_temp_awave_ocean,levs,'b',label = 'Delta T ocean (global)')

# ax[0].set_xlabel("Delta T (K)")
# ax[1].set_xlabel("Delta T (K)")
# ax[0].tick_params()
# ax[1].tick_params()
# ax[0].legend()
# ax[1].legend()
# fig.gca().invert_yaxis()
# ax[0].set_ylabel('Pressure (hPa)')

################################################################################################


# #[omega,omega_avg,omega_seasonal_avg,omega_month_avg,omega_annual_avg,time]=seasonal_4D_variable(testdir,model,runmin,runmax,'omega','Pa/s')

# #[omega_ctl,omega_avg_ctl,omega_seasonal_avg_ctl,omega_month_avg_ctl,omega_annual_avg_ctl,time]=seasonal_4D_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'omega','Pa/s')


# winds_seasons((ucomp_seasonal_avg-ucomp_seasonal_avg_ctl),(vcomp_seasonal_avg-vcomp_seasonal_avg_ctl),level,(precipitation_seasonal_avg-precipitation_seasonal_avg_ctl),'rainnorm','mm/d',-2.,2.,landmaskxr,outdir,runmin,runmax)




#[convection_rain_ctl,convection_rain_avg_ctl,convection_rain_seasonal_avg_ctl,convection_rain_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'convection_rain','kg/m2s')
#[condensation_rain_ctl,condensation_rain_avg_ctl,condensation_rain_seasonal_avg_ctl,condensation_rain_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'condensation_rain','kg/m2s')



# maxval_precip = np.absolute((precipitation_month_avg*86400).max())

# for i in range(1,13):

#     month_plot = winds_at_heightlevel(ucomp_month_avg.sel(month=i),vcomp_month_avg.sel(month=i),level,precipitation_month_avg.sel(month=i)*86400,'fromwhite','mm/day',0,maxval_precip)
#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+testdir+'/anim_plot_precip'+str(i)+'.png',bbox_inches='tight')
# os.system('convert -delay 100 /scratch/mp586/Code/Graphics/'+testdir+'/anim_plot_precip*.png /scratch/mp586/Code/Graphics/'+testdir+'/precip_wind_monthly_clim.gif')

# maxval_omega_surf = np.absolute((omega_month_avg[:,level,:,:]).max())
# minval_omega_surf = np.absolute((omega_month_avg[:,level,:,:]).min())


# for i in range(1,13):

#     month_plot = winds_at_heightlevel(ucomp_month_avg.sel(month=i),vcomp_month_avg.sel(month=i),level,(omega_month_avg[:,level,:,:]).sel(month=i),'rainnorm','mm/day',minval_omega_surf,maxval_omega_surf)
#     month_plot.savefig('/scratch/mp586/Code/Graphics/'+testdir+'/anim_plot_omega'+str(i)+'.png',bbox_inches='tight')
# os.system('convert -delay 100 /scratch/mp586/Code/Graphics/'+testdir+'/anim_plot_omega*.png /scratch/mp586/Code/Graphics/'+testdir+'/omega_wind_monthly_clim.gif')






# Decomposition of precipitation change
#### this is wrong because using each month instead of a climatology
# M_ctl = precipitation_ctl / sphum_ctl
# M_new = precipitation / sphum
# Delta_M = M_new - M_ctl
# Delta_P_circ = sphum* Delta_M
# Delta_P_q = M_ctl * (sphum - sphum_ctl)
# Delta_P_cross = (sphum - sphum_ctl) * (M_new - M_ctl)
# Delta_P_sum = Delta_P_cross + Delta_P_q + Delta_P_circ
# Delta_P_sum_avg = Delta_P_sum.mean('time')
# Diff_DeltaPs = (precipitation_avg - precipitation_avg_ctl) - Delta_P_sum_avg
# #print('Diff_DeltaPs.max()'+str(Diff_DeltaPs.max()))
# #print('Diff_DeltaPs.min()'+str(Diff_DeltaPs.min()))
# #print('Diff_DeltaPs.mean()'+str(Diff_DeltaPs.mean()))

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_circ.mean('time'),area_array,'mm/day','Delta_P_circ','rainnorm',landmaskxr,minval=-2.,maxval=2.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_q.mean('time'),area_array,'mm/day','Delta_P_q','rainnorm',landmaskxr,minval=-2.,maxval=2.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_cross.mean('time'),area_array,'mm/day','Delta_P_cross','rainnorm',landmaskxr,minval=-2.,maxval=2.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Diff_DeltaPs,area_array,'mm/day','Diff_Delta_Ps','rainnorm',landmaskxr,minval=-2.,maxval=2.)

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_circ.mean('time'),area_array,'mm/day','Delta_P_circ_narrowcbar','rainnorm',landmaskxr,minval=-1.,maxval=1.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_q.mean('time'),area_array,'mm/day','Delta_P_q_narrowcbar','rainnorm',landmaskxr,minval=-1.,maxval=1.)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,Delta_P_cross.mean('time'),area_array,'mm/day','Delta_P_cross_narrowcbar','rainnorm',landmaskxr,minval=-1.,maxval=1.)

# globavg_deltaT = area_weighted_avg((tsurf_avg - tsurf_avg_ctl),area_array,landmask,'all_sfcs')

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(Delta_M/globavg_deltaT).mean('time'),area_array,'mm/day/K','Delta_M_normalized','rainnorm',landmaskxr,minval=-40.,maxval=40) # change in circulation normalized by global mean T change # following Chadwick et al., 2013 (Fig. 8)
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,sphum_avg - sphum_avg_ctl,area_array,'kg/kg','q_avg_minus_ctl_levlevel','rainnorm',landmaskxr) 
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,sphum_avg_ctl,area_array,'kg/kg','q_ctl_levlevel','fromwhite',landmaskxr,nmb_contours=10) 
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,sphum_avg,area_array,'kg/kg','q_avg_levlevel','fromwhite',landmaskxr,nmb_contours=10) 
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,M_ctl.mean('time'),area_array,'mm/day','M_ctl','fromwhite',landmaskxr)  
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,M_new.mean('time'),area_array,'mm/day','M_avg','fromwhite',landmaskxr) 
# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(Delta_M).mean('time')/M_ctl.mean('time'),area_array,' ','DeltaM_avg_div_M_ctl_avg','rainnorm',landmaskxr,minval=-1.0,maxval=1.0)

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,((sphum_avg - sphum_avg_ctl)/sphum_avg_ctl),area_array,' ','Deltaq_div_q_ctl','rainnorm',landmaskxr)

# any_configuration_plot(outdir,runmin,runmax,-90.,90.,(Delta_M).mean('time')*(sphum_avg - sphum_avg_ctl).mean('time'),area_array,'mm/day','DeltaM_avg_dot_Deltaq_avg','rainnorm',landmaskxr,minval=-2.0,maxval=2.0)
                                 
