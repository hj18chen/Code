from netCDF4 import Dataset
import numpy as np
import matplotlib as mpl 
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
import xarray as xr
import pandas as pd
import os
from scipy.odr import *

import sys
sys.path.insert(0, '/scratch/mp586/Code/PYCODES')
from plotting_routines_kav7 import *
import stats as st

GFDL_BASE = os.environ['GFDL_BASE']
sys.path.insert(0, os.path.join(GFDL_BASE,'src/extra/python/scripts'))
import cell_area as ca





mpl.rcParams["lines.linewidth"] = 0.5 # setting linewidth for landmask contour plot doesn't work otherwise 

variable = 'precipitation' # 'bucket_depth' # 'precipitation' # 'flux_lhe' # precipitation # t_surf
colormap = 'BrBG' # 'BrBG' # 'BrBG' # 'RdBu_r'
minval = -2. # -0.05 # -2. # -2. # -10.
maxval = 2. # 0.05 #  2. # 2. # 10. 
units ='mm/d' # 'm' # 'mm/d' # 'mm/d' # 'K'
factor = 86400.# 1. # 86400. # 1./28. # 86400 # 1.
low_lim = -4.# -0.1 # -4. # 0.
up_lim = 4.  # 0.1 # 4. # 5. 


control_sb_dirs = [
'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
'narrow_six_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
'narrow_twelve_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
'narrow_twentyfour_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
'squareland_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
'two_continents_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387'
]

control_vp0_dirs = [
'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref0_commit7bb4387',
'x',
'x',
'x',
'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref0_commit7bb4387',
'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref0_commit7bb4387',
'x',
'x'
]

control_vp02_dirs = [
'x',
'x',
'x',
'x',
'x',
'x',
'x',
'x'
]

control_vp05_dirs = [
'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_commit7bb4387',
'x',
'narrow_twelve_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_commit7bb4387',
'narrow_twentyfour_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_commit7bb4387',
'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_commit7bb4387',
'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_commit7bb4387',
'squareland_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_commit7bb4387',
'two_continents_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_commit7bb4387'
]





vp0_dirs = [
'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref0_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'narrow_six_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref0_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'x',
'x',
'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref0_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref0_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'x',
'two_continents_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref0_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387'
]

vp02_dirs = [
'x',
'x',
'x',
'x',
'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref02_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref02_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'x',
'two_continents_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref02_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387'
]

vp05_dirs = [
'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'x',
'narrow_twelve_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'narrow_twentyfour_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'squareland_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'two_continents_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387'
]

vp07_dirs = [
'x',
'x',
'x',
'x',
'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref07_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref07_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'x',
'x'
]


simple_bucket_dirs = [
'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'x',
'narrow_twelve_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'narrow_twentyfour_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'squareland_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'two_continents_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387'
]


ctl_dict = {'vp0_ctl': control_vp0_dirs, 
'vp02_ctl': control_vp02_dirs,
'vp05_ctl': control_vp05_dirs, 
'sb_ctl': control_sb_dirs}

ctl_list = ['vp0_ctl','vp02_ctl','vp05_ctl','sb_ctl']

[precipitation_ctl,precipitation_avg_ctl,x,x,x]=seasonal_surface_variable('Isca_DATA/ISCA_HPC/narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387','isca',1,10,variable,units, factor=factor)


lats = precipitation_avg_ctl.lat
lons = precipitation_avg_ctl.lon


landmasks = ['narrow_three','narrow_six','narrow_twelve','narrow_twentyfour','square_South_America','square_Africa','squareland','two_AM','two_continents']

landfile=Dataset(os.path.join(GFDL_BASE,'input/'+landmasks[0]+'/land.nc'),mode='r')
landlats=landfile.variables['lat'][:]
landlons=landfile.variables['lon'][:]

landmask_array = np.zeros((len(landmasks), len(landlats), len(landlons)))

for i in range(len(landmasks)):
    landfile=Dataset(os.path.join(GFDL_BASE,'input/'+landmasks[i]+'/land.nc'),mode='r')
    landmask_array[i,:,:]=landfile.variables['land_mask'][:]




pert_dict = {'vp0': vp0_dirs, 
'vp02': vp02_dirs,
'vp05': vp05_dirs, 
'vp07': vp07_dirs, 
'sb': simple_bucket_dirs}

pert_list = ['vp0','vp02','vp05','vp07','sb']

precip_change_matrix = np.zeros((len(vp0_dirs),len(pert_dict),len(lats),len(lons)))
precip_ctl_matrix = np.zeros((len(vp0_dirs),len(pert_dict),len(lats),len(lons)))
precip_pert_matrix = np.zeros((len(vp0_dirs),len(pert_dict),len(lats),len(lons)))



for i in range(len(control_sb_dirs)):
    [precipitation_ctl,precipitation_avg_ctl,x,x,x]=seasonal_surface_variable('Isca_DATA/ISCA_HPC/'+control_sb_dirs[i],'isca',121,481,variable,units, factor=factor)
    
    for j in range(len(pert_list)):
        testdir = pert_dict[pert_list[j]][i]
        if testdir != 'x':
            testdir = 'Isca_DATA/ISCA_HPC/'+pert_dict[pert_list[j]][i]
            [precipitation,precipitation_avg,x,x,x]=seasonal_surface_variable(testdir,'isca',120,480,variable,units, factor=factor)
            precip_change_matrix[i,j,:,:] = precipitation_avg - precipitation_avg_ctl
            precip_ctl_matrix[i,j,:,:] = precipitation_avg_ctl
            precip_pert_matrix[i,j,:,:] = precipitation_avg
        
small = 22 #largefonts 14 # smallfonts 10 # medfonts = 14
med = 24 #largefonts 18 # smallfonts 14 # medfonts = 16
lge = 28 #largefonts 22 # smallfonts 18 # medfonts = 20


names = ['$\Delta P_{0\%cond}$', '$\Delta P_{20\%cond}$', '$\Delta P_{50\%cond}$', '$\Delta P_{70\%cond}$', '$\Delta P_{100\%cond}$']
conts = ['6$^{\circ}$','8$^{\circ}$', '14$^{\circ}$', '25$^{\circ}$', 'AM', 'AF','100$^{\circ}$','2Cont']

fig = plt.figure(figsize = (22,15))

m = Basemap(projection='cyl',resolution='c', llcrnrlat=-40, urcrnrlat=40,llcrnrlon=-30, urcrnrlon=170)

v = np.linspace(minval,maxval,41) # , endpoint=True)


for i in range(len(control_sb_dirs)):
    for j in range(len(pert_list)):
        testdir = pert_dict[pert_list[j]][i]
        ax = plt.subplot2grid((len(vp0_dirs),len(pert_dict)), (i,j))
        if i == 0:
            ax.set_title(names[j], size = lge)
        if j == 0:
            ax.set_ylabel(conts[i], size = med)
        if testdir == 'x':
            ax.xaxis.set_visible(False)
            # make spines (the box) invisible
            plt.setp(ax.spines.values(), visible=False)
            # remove ticks and labels for the left axis
            ax.tick_params(left=False, labelleft=False)
            #remove background patch (only needed for non-white background)
            # ax.patch.set_visible(False)
        else:
            array = xr.DataArray(precip_change_matrix[i,j,:,:],coords=[lats,lons],dims=['lat','lon'])
            array = np.asarray(array)
            array, lons_cyclic = addcyclic(array, lons)
            array,lons_cyclic = shiftgrid(np.max(lons_cyclic)-180.,array,lons_cyclic,start=False,cyclic=np.max(lons_cyclic))

            lon, lat = np.meshgrid(lons_cyclic, lats)
            xi, yi = m(lon, lat)

            array = xr.DataArray(array,coords=[lats,lons_cyclic],dims=['lat','lon'])

            cs = m.contourf(xi,yi,array, v, cmap=colormap, extend = 'both')

            landmask,landlons_shift = shiftgrid(np.max(landlons)-180.,landmask_array[i,:,:],landlons,start=False,cyclic=np.max(landlons))
            landmask, lons_cyclic = addcyclic(landmask, landlons_shift)
            m.contour(xi,yi,landmask, 1, colors = 'k')


# plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cb_ax = plt.axes([0.83, 0.3, 0.01, 0.4])
# # add an axes, lower left corner in [0.83, 0.3] measured in figure coordinate with axes width 0.01 and height 0.4
# cbar = plt.colorbar(cs, cax=cb_ax)

plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.9, wspace=0.02, hspace=0.02)
cb_ax = plt.axes([0.3, 0.05, 0.4, 0.03])
cbar = plt.colorbar(cs, cax=cb_ax, orientation = 'horizontal')
cbar.set_label(units, size = med)
cbar.ax.tick_params(labelsize=med)

plt.savefig('/scratch/mp586/Code/Graphics/multipanel_'+variable+'_avg_minus_ctl_120-480_lowcbar_paper.png', bbox_inches = 'tight', format = 'png', dpi = 400)
plt.savefig('/scratch/mp586/Code/Graphics/multipanel_'+variable+'_avg_minus_ctl_120-480_lowcbar_paper.pdf', bbox_inches = 'tight', format = 'pdf')
plt.savefig('/scratch/mp586/Code/Graphics/multipanel_'+variable+'_avg_minus_ctl_120-480_lowcbar_paper.eps', bbox_inches = 'tight', format = 'eps', dpi=600)


plt.close()




precip_change_matrix = xr.DataArray(precip_change_matrix, coords = [control_sb_dirs, pert_list, lats, lons], dims = ['width','exp','lat','lon'])
AM_mask = landmask_array[4]         
AF_mask = landmask_array[5]                                  
dP_AF_SB = precip_change_matrix[5,4,:,:].where(AF_mask == 1.) 
dP_AF_veg = precip_change_matrix[5,2,:,:].where(AF_mask == 1.)
dP_AM_SB = precip_change_matrix[4,4,:,:].where(AM_mask == 1.) 
dP_AM_veg = precip_change_matrix[4,2,:,:].where(AM_mask == 1.)
                                         
dP_AF_SB = np.asarray(dP_AF_SB).flatten()        
dP_AM_SB = np.asarray(dP_AM_SB).flatten()  
dP_AM_veg = np.asarray(dP_AM_veg).flatten()
dP_AF_veg = np.asarray(dP_AF_veg).flatten()
                                   
                                                                      
mask = ~np.isnan(dP_AM_SB)                                                                      
[slope, intercept, r_value, p_value, std_err] = stats.linregress(dP_AM_SB[mask],dP_AM_veg[mask])
line_AM1 = slope*dP_AM_SB + intercept     
print('AM1 r = '+str(r_value))
print('AM1 slope = '+str(slope))

[slope, intercept, r_value, p_value, std_err] = stats.linregress(dP_AM_veg[mask],dP_AM_SB[mask])
print('AM2 r = '+str(r_value))
print('AM2 slope = '+str(slope))

line_AM2 = (dP_AM_SB - intercept)/slope
[slope_lst, intercept_lst, x, x, x] = orthoregress(dP_AM_SB[mask],dP_AM_veg[mask])
line_AM_lst = slope_lst*dP_AM_SB + intercept_lst
print('AM slope = '+str(slope_lst))

                                                           
mask = ~np.isnan(dP_AF_SB)                                                                               
[slope, intercept, r_value, p_value, std_err] = stats.linregress(dP_AF_SB[mask],dP_AF_veg[mask])
line_AF1 = slope*dP_AF_SB + intercept  
print('AF1 r = '+str(r_value))
print('AF1 slope = '+str(slope))
[slope, intercept, r_value, p_value, std_err] = stats.linregress(dP_AF_veg[mask],dP_AF_SB[mask])
print('AF2 r = '+str(r_value))
print('AF2 slope = '+str(slope))
line_AF2 = (dP_AF_SB - intercept)/slope
[slope_lst, intercept_lst, x, x, x] = orthoregress(dP_AF_SB[mask],dP_AF_veg[mask])
line_AF_lst = slope_lst*dP_AF_SB + intercept_lst
print('AF slope = '+str(slope_lst))

# AM1 r = 0.558081345852
# AM1 slope = 0.894637712237
# AM2 r = 0.558081345852
# AM2 slope = 0.348135099078
# AM slope = 2.20749208202
# AF1 r = 0.770666686075
# AF1 slope = 0.788271314688
# AF2 r = 0.770666686075
# AF2 slope = 0.753455225325
# AF slope = 1.02972373001                                      



# plt.plot(dP_AM_SB, dP_AM_veg, 'c.', markersize = 5., label = 'AM')
# plt.plot(dP_AF_SB, dP_AF_veg, 'm.', markersize = 5., label = 'AF')          
# plt.plot(np.linspace(low_lim,up_lim,100),np.linspace(low_lim,up_lim,100), 'dimgrey')      
# plt.plot(np.linspace(low_lim,up_lim,100),np.zeros((100)), 'dimgrey')                 
# plt.plot(np.zeros((100)), np.linspace(-4.,4.,100), 'dimgrey')                    
# plt.plot(np.linspace(low_lim,up_lim,100),np.linspace(low_lim,up_lim,100), 'dimgrey')                
# plt.legend()                                                                 
# plt.xlim(low_lim,up_lim)                                                         
# plt.ylim(low_lim,up_lim)          
# plt.xlabel(variable+' change bucket ('+units+')')     
# plt.ylabel(variable+' change 50%cond ('+units+')')
# plt.plot(dP_AM_SB, line_AM1, color = 'c', linestyle = 'dashed') 
# plt.plot(dP_AM_SB, line_AM2, color = 'c', linestyle = 'dashed') 
# plt.plot(dP_AM_SB, line_AM_lst, 'k')                                                         
# plt.plot(dP_AF_SB, line_AF1, color = 'm', linestyle = 'dashed')    
# plt.plot(dP_AF_SB, line_AF2, color = 'm', linestyle = 'dashed')
# plt.plot(dP_AF_SB, line_AF_lst, 'k') 
 

# plt.savefig('/scratch/mp586/Code/Graphics/d'+variable+'_AM_AF_veg_SB.png', dpi = 400)

plt.close()

fig, axes = plt.subplots(1,1, figsize = (10,10))

axes.plot(dP_AM_SB, dP_AM_veg, 'cD', markersize = 5., label = 'America')
axes.plot(dP_AF_SB, dP_AF_veg, '*', color = 'royalblue', markersize = 8., label = 'Africa')          
axes.plot(np.linspace(low_lim,up_lim,100),np.linspace(low_lim,up_lim,100), 'dimgrey')      
axes.plot(np.linspace(low_lim,up_lim,100),np.zeros((100)), 'dimgrey')                 
axes.plot(np.zeros((100)), np.linspace(-4.,4.,100), 'dimgrey')                    
axes.plot(np.linspace(low_lim,up_lim,100),np.linspace(low_lim,up_lim,100), 'dimgrey')                
axes.legend(fontsize = med, markerscale=1.5)                                                                 
axes.set_xlim(low_lim,up_lim)                                                         
axes.set_ylim(low_lim,up_lim)          
# axes.set_xlabel(variable+' change SB ('+units+')', fontsize = med)     
# axes.set_ylabel(variable+' change veg 0.5 ('+units+')', fontsize = med)
axes.set_xlabel('$\Delta P_{100\%cond}$ ('+units+')', fontsize = lge)     
axes.set_ylabel('$\Delta P_{50\%cond}$ ('+units+')', fontsize = lge)

axes.plot(dP_AM_SB, line_AM_lst, 'c', linewidth = 2)                                 
axes.plot(dP_AF_SB, line_AF_lst, 'darkblue', linewidth = 2) 
axes.tick_params(labelsize = med)
axes.spines['right'].set_visible(False)
axes.spines['top'].set_visible(False)
 
plt.savefig('/scratch/mp586/Code/Graphics/d'+variable+'_AM_AF_veg_SB_lstonly_paper.png', dpi = 100)
plt.savefig('/scratch/mp586/Code/Graphics/d'+variable+'_AM_AF_veg_SB_lstonly_paper.pdf', dpi = 400)
plt.savefig('/scratch/mp586/Code/Graphics/d'+variable+'_AM_AF_veg_SB_lstonly_paper.eps', dpi = 600)

























# fig = plt.figure(figsize = (25,15))

# m = Basemap(projection='cyl',resolution='c', llcrnrlat=-40, urcrnrlat=40,llcrnrlon=-30, urcrnrlon=170)

# v = np.linspace(0.,8.,41) # , endpoint=True)


# for i in range(len(control_sb_dirs)):
#     for j in range(len(pert_list)):
#         testdir = pert_dict[pert_list[j]][i]
#         if testdir != 'x':
#             array = xr.DataArray(precip_ctl_matrix[i,j,:,:],coords=[lats,lons],dims=['lat','lon'])
#             array = np.asarray(array)
#             array, lons_cyclic = addcyclic(array, lons)
#             array,lons_cyclic = shiftgrid(np.max(lons_cyclic)-180.,array,lons_cyclic,start=False,cyclic=np.max(lons_cyclic))

#             lon, lat = np.meshgrid(lons_cyclic, lats)
#             xi, yi = m(lon, lat)

#             array = xr.DataArray(array,coords=[lats,lons_cyclic],dims=['lat','lon'])


#             ax = plt.subplot2grid((len(vp0_dirs),len(pert_dict)), (i,j))

#             cs = m.contourf(xi,yi,array, v, cmap='Blues', extend = 'max')

#             landmask,landlons_shift = shiftgrid(np.max(landlons)-180.,landmask_array[i,:,:],landlons,start=False,cyclic=np.max(landlons))
#             landmask, lons_cyclic = addcyclic(landmask, landlons_shift)
#             m.contour(xi,yi,landmask, 1, colors = 'k')


# plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cb_ax = plt.axes([0.83, 0.3, 0.01, 0.4])
# cbar = plt.colorbar(cs, cax = cb_ax)
# cbar.set_label(units, size = med)
# cbar.ax.tick_params(labelsize=med)

# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_'+variable+'_ctl_120-480.png', bbox_inches = 'tight', format = 'png', dpi = 400)
# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_'+variable+'_ctl_120-480.pdf', bbox_inches = 'tight', format = 'pdf')



# fig = plt.figure(figsize = (20,10))
# v = np.linspace(-1.,1.,41) # , endpoint=True)

# dprel_matrix = precip_change_matrix/precip_ctl_matrix

# for i in range(len(control_sb_dirs)):
#     for j in range(len(pert_list)):
#         testdir = pert_dict[pert_list[j]][i]
#         if testdir != 'x':
#             array = xr.DataArray(dprel_matrix[i,j,:,:],coords=[lats,lons],dims=['lat','lon'])
#             array = np.asarray(array)
#             array, lons_cyclic = addcyclic(array, lons)
#             array,lons_cyclic = shiftgrid(np.max(lons_cyclic)-180.,array,lons_cyclic,start=False,cyclic=np.max(lons_cyclic))

#             lon, lat = np.meshgrid(lons_cyclic, lats)
#             xi, yi = m(lon, lat)

#             array = xr.DataArray(array,coords=[lats,lons_cyclic],dims=['lat','lon'])


#             ax = plt.subplot2grid((len(vp0_dirs),len(pert_dict)), (i,j))

#             cs = m.contourf(xi,yi,array, v, cmap='BrBG', extend = 'both')

#             landmask,landlons_shift = shiftgrid(np.max(landlons)-180.,landmask_array[i,:,:],landlons,start=False,cyclic=np.max(landlons))
#             landmask, lons_cyclic = addcyclic(landmask, landlons_shift)
#             m.contour(xi,yi,landmask, 1, colors = 'k')


# plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cb_ax = plt.axes([0.83, 0.3, 0.01, 0.4])
# cbar = plt.colorbar(cs, cax = cb_ax)
# cbar.set_label(units, size = 10)
# cbar.ax.tick_params(labelsize=10)

# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_Pavg_minus_ctl_relchange_120-480.png', bbox_inches = 'tight', format = 'png', dpi = 400)
# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_Pavg_minus_ctl_relchange_120-480.pdf', bbox_inches = 'tight', format = 'pdf')




# precip_ctl_matrix = np.zeros((len(vp0_dirs),len(pert_dict),len(lats),len(lons)))

# for i in range(len(control_sb_dirs)):
#     for j in range(len(ctl_list)):
#         testdir = ctl_dict[ctl_list[j]][i]
#         if testdir != 'x':
#             testdir = 'Isca_DATA/ISCA_HPC/'+testdir
#             [precipitation_ctl,precipitation_avg_ctl,x,x,x]=seasonal_surface_variable(testdir,'isca',121,481,variable,units, factor=factor)
#             precip_ctl_matrix[i,j,:,:] = precipitation_avg_ctl



# fig = plt.figure(figsize = (10,8))
# v = np.linspace(minval,maxval,41) # , endpoint=True)

# warming = np.zeros((len(vp0_dirs),len(pert_dict),len(lats),len(lons)))
# stomata = np.zeros((len(vp0_dirs),len(pert_dict),len(lats),len(lons)))

# for i in range(len(control_sb_dirs)):
#     for j in range(len(ctl_list) - 1):
#         testdir = ctl_dict[ctl_list[j]][i]
#         if testdir != 'x':
#             stomata[i,j,:,:] = precip_ctl_matrix[i,j,:,:] - precip_ctl_matrix[i,3,:,:]
#             array = xr.DataArray(stomata[i,j,:,:],coords=[lats,lons],dims=['lat','lon'])
#             array = np.asarray(array)
#             array, lons_cyclic = addcyclic(array, lons)
#             array,lons_cyclic = shiftgrid(np.max(lons_cyclic)-180.,array,lons_cyclic,start=False,cyclic=np.max(lons_cyclic))

#             lon, lat = np.meshgrid(lons_cyclic, lats)
#             xi, yi = m(lon, lat)

#             array = xr.DataArray(array,coords=[lats,lons_cyclic],dims=['lat','lon'])


#             ax = plt.subplot2grid((len(vp0_dirs),len(pert_dict)), (i,j))

#             cs = m.contourf(xi,yi,array, v, cmap=colormap, extend = 'both')

#             landmask,landlons_shift = shiftgrid(np.max(landlons)-180.,landmask_array[i,:,:],landlons,start=False,cyclic=np.max(landlons))
#             landmask, lons_cyclic = addcyclic(landmask, landlons_shift)
#             m.contour(xi,yi,landmask, 1, colors = 'k')


# plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cb_ax = plt.axes([0.83, 0.3, 0.01, 0.4])
# cbar = plt.colorbar(cs, cax = cb_ax)
# cbar.set_label(units, size = med)
# cbar.ax.tick_params(labelsize=med)

# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_stomata_only_'+variable+'_change_120-480.png', bbox_inches = 'tight', format = 'png', dpi = 400)
# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_stomata_only_'+variable+'_change_120-480.pdf', bbox_inches = 'tight', format = 'pdf')
# plt.close()

# fig = plt.figure(figsize = (20,15))
# v = np.linspace(minval,maxval,41) # , endpoint=True)

# for i in range(len(control_sb_dirs)):
#     for j in range(len(ctl_list) - 1):
#         testdir = ctl_dict[ctl_list[j]][i]
#         if testdir != 'x':
#             warming[i,j,:,:] = precip_pert_matrix[i,3,:,:] - precip_ctl_matrix[i,3,:,:]
#             array = xr.DataArray(warming[i,j,:,:],coords=[lats,lons],dims=['lat','lon'])
#             array = np.asarray(array)
#             array, lons_cyclic = addcyclic(array, lons)
#             array,lons_cyclic = shiftgrid(np.max(lons_cyclic)-180.,array,lons_cyclic,start=False,cyclic=np.max(lons_cyclic))

#             lon, lat = np.meshgrid(lons_cyclic, lats)
#             xi, yi = m(lon, lat)

#             array = xr.DataArray(array,coords=[lats,lons_cyclic],dims=['lat','lon'])


#             ax = plt.subplot2grid((len(vp0_dirs),len(pert_dict)), (i,j))

#             cs = m.contourf(xi,yi,array, v, cmap=colormap, extend = 'both')

#             landmask,landlons_shift = shiftgrid(np.max(landlons)-180.,landmask_array[i,:,:],landlons,start=False,cyclic=np.max(landlons))
#             landmask, lons_cyclic = addcyclic(landmask, landlons_shift)
#             m.contour(xi,yi,landmask, 1, colors = 'k')


# plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cb_ax = plt.axes([0.83, 0.3, 0.01, 0.4])
# cbar = plt.colorbar(cs, cax = cb_ax)
# cbar.set_label(units, size = med)
# cbar.ax.tick_params(labelsize=med)

# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_warming_only_'+variable+'_change_120-480.png', bbox_inches = 'tight', format = 'png', dpi = 400)
# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_warming_only_'+variable+'_change_120-480.pdf', bbox_inches = 'tight', format = 'pdf')
# plt.close()

# fig = plt.figure(figsize = (20,15))

# for i in range(len(control_sb_dirs)):
#     for j in range(len(ctl_list) - 1):
#         testdir = ctl_dict[ctl_list[j]][i]
#         if testdir != 'x':
#             array = xr.DataArray(warming[i,j,:,:] + stomata[i,j,:,:],coords=[lats,lons],dims=['lat','lon'])
#             array = np.asarray(array)
#             array, lons_cyclic = addcyclic(array, lons)
#             array,lons_cyclic = shiftgrid(np.max(lons_cyclic)-180.,array,lons_cyclic,start=False,cyclic=np.max(lons_cyclic))

#             lon, lat = np.meshgrid(lons_cyclic, lats)
#             xi, yi = m(lon, lat)

#             array = xr.DataArray(array,coords=[lats,lons_cyclic],dims=['lat','lon'])


#             ax = plt.subplot2grid((len(vp0_dirs),len(pert_dict)), (i,j))

#             cs = m.contourf(xi,yi,array, v, cmap=colormap, extend = 'both')

#             landmask,landlons_shift = shiftgrid(np.max(landlons)-180.,landmask_array[i,:,:],landlons,start=False,cyclic=np.max(landlons))
#             landmask, lons_cyclic = addcyclic(landmask, landlons_shift)
#             m.contour(xi,yi,landmask, 1, colors = 'k')


# plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cb_ax = plt.axes([0.83, 0.3, 0.01, 0.4])
# cbar = plt.colorbar(cs, cax = cb_ax)
# cbar.set_label(units, size = med)
# cbar.ax.tick_params(labelsize=med)

# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_addition_'+variable+'_change_120-480.png', bbox_inches = 'tight', format = 'png', dpi = 400)
# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_addition_'+variable+'_change_120-480.pdf', bbox_inches = 'tight', format = 'pdf')
# plt.close()

# fig = plt.figure(figsize = (20,15))


# for i in range(len(control_sb_dirs)):
#     for j in range(len(ctl_list) - 1):
#         testdir = ctl_dict[ctl_list[j]][i]
#         if testdir != 'x':
#             array = xr.DataArray(precip_change_matrix[i,j,:,:] - (warming[i,j,:,:] + stomata[i,j,:,:]),coords=[lats,lons],dims=['lat','lon'])
#             array = np.asarray(array)
#             array, lons_cyclic = addcyclic(array, lons)
#             array,lons_cyclic = shiftgrid(np.max(lons_cyclic)-180.,array,lons_cyclic,start=False,cyclic=np.max(lons_cyclic))

#             lon, lat = np.meshgrid(lons_cyclic, lats)
#             xi, yi = m(lon, lat)

#             array = xr.DataArray(array,coords=[lats,lons_cyclic],dims=['lat','lon'])


#             ax = plt.subplot2grid((len(vp0_dirs),len(pert_dict),), (i,j))

#             cs = m.contourf(xi,yi,array, v, cmap=colormap, extend = 'both')

#             landmask,landlons_shift = shiftgrid(np.max(landlons)-180.,landmask_array[i,:,:],landlons,start=False,cyclic=np.max(landlons))
#             landmask, lons_cyclic = addcyclic(landmask, landlons_shift)
#             m.contour(xi,yi,landmask, 1, colors = 'k')


# plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.8, wspace=0.02, hspace=0.02)
# cb_ax = plt.axes([0.83, 0.3, 0.01, 0.4])
# cbar = plt.colorbar(cs, cax = cb_ax)
# cbar.set_label(units, size = med)
# cbar.ax.tick_params(labelsize=med)

# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_full_minus_addition_'+variable+'_change_120-480.png', bbox_inches = 'tight', format = 'png', dpi = 400)
# plt.savefig('/scratch/mp586/Code/Graphics/multipanel_full_minus_addition_'+variable+'_change_120-480.pdf', bbox_inches = 'tight', format = 'pdf')
# plt.close()






