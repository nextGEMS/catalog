import glob
import intake
import xarray as xr


for catalog in ["IFS_4.4-FESOM_5-cycle3.yaml"]: #use glob.glob("*.yaml") to test all
    print(f"Testing datasets in catalog: {catalog}")
    fcat = intake.open_catalog(catalog)
    for k in fcat.keys():
       try:
          fcat[k].to_dask()
       except Exception as ex:
          print(f'Error making dataset in {catalog} with {k} as source', ex)

