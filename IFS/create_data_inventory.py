import glob
import intake 
import pandas as pd


for catalog in glob.glob("*.yaml"):
    if (catalog == 'tco-grids-cycle3.yaml') or (catalog == "main.yaml"):
        continue
    print(f"Processing catalog: {catalog}")
    
    fcat = intake.open_catalog(catalog)


    sources_dict = {}

    for source in fcat.keys():
        if source == "data_inventory":
            continue
        try:
            ds = fcat[source].to_dask()
        except Exception as ex:
            print(f"catalog source {source} failed to load as dataset: ",ex)
            continue
    
        varlist = []
        
        for datavar in ds.data_vars.keys():
            datavar_dim_str = str(ds.data_vars[datavar].dims).replace("'","") # adds variable with its dims to the list
                                                                          # like var(time, lat, lon)
            varlist.append(f"{datavar}") # {datavar_dim_str}")
        
        sources_dict[source] = varlist
    
    inventory_df = pd.DataFrame({'Variables': sources_dict})
    inventory_name = f"inventory_{catalog.rstrip('.yaml')}.csv"
    inventory_df.to_csv(inventory_name, index_label='data source')


