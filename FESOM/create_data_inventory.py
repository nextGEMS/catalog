import intake 
import pandas as pd

fcat = intake.open_catalog("combined_catalog.yaml")


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
inventory_df.to_csv("inventory.csv", index_label='data source')


