import yaml
import os

def create_intake_catalog(years, variables_daily, variables_hourly, directory):

    # create empty urlpaths
    urlpath_daily = []
    urlpath_hourly = []
    
    # check if daily variable files exist
    for year in years:
        for var in variables_daily:
            file_path = os.path.join(directory, f'{var}_{year}.zarr')
            if os.path.exists(file_path):
                urlpath_daily.append(file_path)
    
    # check if hourly variable files exist
    for year in years:
        for month in range(1, 13):
            for var in variables_hourly:
                file_path = os.path.join(directory, f'{var}_{year}_{month}.zarr')
                if os.path.exists(file_path):
                    urlpath_hourly.append(file_path)
                
    catalog_dict = {
        'plugins': {
            'source': [
                {'module': 'intake_xarray'}
            ]
        },
        'sources': {
            '3D_daily_native_zarr': {
                'driver': 'zarr',
                'args': {
                    'consolidated': True,
                    'urlpath': urlpath_daily
                }
            },
            '3D_1h_native_zarr': {
                'driver': 'zarr',
                'args': {
                    'consolidated': True,
                    'urlpath': urlpath_hourly
                }
            },
            'elem_grid': {
                'driver': 'netcdf',
                'args': {
                    'urlpath': '/work/bm1235/a270046/meshes/NG5_griddes_elems_IFS.nc',
                }
            },
            'node_grid': {
                'driver': 'netcdf',
                'args': {
                    'urlpath': '/work/bm1235/a270046/meshes/NG5_griddes_nodes_IFS.nc',
                }
            }
        }
    }

    with open("IFS_4.4-FESOM_5-cycle3_zarr.yaml", 'w') as file:
        documents = yaml.dump(catalog_dict, file)

# specify the years and variables
years = ['2020', '2021', '2022', '2023', '2024']
variables_daily = ['temp', 'salt', 'u', 'v', 'w']
variables_hourly = ['temp_upper', 'salt_upper', 'u_upper', 'v_upper', 'w_upper']

# specify the directory where the data is located
directory = '/work/bm1344/AWI/Cycle3/test'

# generate the intake catalog
create_intake_catalog(years, variables_daily, variables_hourly, directory)
