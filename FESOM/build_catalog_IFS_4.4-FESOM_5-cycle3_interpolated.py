import os
import glob
import yaml

# directory paths
dir_paths = [
    "/work/bm1344/AWI/Cycle3/FESOM/IFS_4.4-FESOM_5-cycle3/025",
    "/work/bm1344/AWI/Cycle3/FESOM/IFS_4.4-FESOM_5-cycle3/100",
]

# mapping for resolution replacements
resolution_map = {"025": "0.25deg", "100": "1deg"}

# initialize an empty dictionary for the catalog
catalog = {"plugins": {"source": [{"module": "intake_xarray"}]}, "sources": {}}

for path in dir_paths:
    # get the resolution from the path
    resolution = resolution_map[path.split("/")[-1]]

    # get the subdirectories
    subdirs = next(os.walk(path))[1]
    for subdir in subdirs:
        # replace 'native' with the resolution
        source_name = subdir.replace("native", resolution)

        # get all netCDF files in the subdir
        netcdf_files = glob.glob(f"{path}/{subdir}/**/*.nc", recursive=True)

        # construct the source for the catalog
        catalog["sources"][source_name] = {
            "description": f"{source_name} data",
            "driver": "netcdf",
            "args": {
                "urlpath": sorted(netcdf_files),
                # "concat_dim": "time",
                # "chunks": {},
            },
        }

# write the catalog to a yaml file
with open("IFS_4.4-FESOM_5-cycle3_interpolated.yaml", "w") as file:
    yaml.dump(catalog, file, sort_keys=False)
