from isca.util import interpolate_output
# dires = ['two_continents_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
# 'two_continents_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
# 'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
# 'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
# 'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
# 'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387']

# dires = ['narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387',
# 'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
# 'narrow_three_newbucket_fixedSSTs_from_realworld_zonallysymm_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387']


dires = ['square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commitfe93b9d',
'square_South_America_newbucket_fixedSSTs_from_realworld_zonallysymm_commitfe93b9d',
'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commitfe93b9d',
'square_Africa_newbucket_fixedSSTs_from_realworld_zonallysymm_commitfe93b9d',
'two_continents_newbucket_fixedSSTs_from_realworld_zonallysymm_corrected_vegpref05_plus_uniform_warming_and_2xCO2_spinup_361_commit7bb4387',
'two_continents_newbucket_fixedSSTs_from_realworld_zonallysymm_commit7bb4387']


from isca.util import interpolate_output
for dire in dires:
    for i in range(120, 481):
        #print(i)
            infile = '/scratch/mp586/Isca_DATA/ISCA_HPC/'+dire+'/run%04d/atmos_monthly.nc' % i   
            outfile = '/scratch/mp586/Isca_DATA/ISCA_HPC/'+dire+'/run%04d/atmos_monthly_interp.nc' % i
            interpolate_output(infile, outfile, p_levs='INPUT', var_names=['slp', 'height', 'omega', 'ucomp', 'vcomp', 'temp','rh','sphum','sphum_u','sphum_v'])