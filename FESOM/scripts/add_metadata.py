import intake
import xarray as xr
import yaml

# Load the initial catalog
fcat = intake.open_catalog("../../IFS/tco2559-ng5-cycle3.yaml")

# Create an empty dictionary to store updated sources
new_sources_dict = {}

# Iterate over the sources in the original catalog
for source in fcat.keys():
    print(source)
    # Skip unwanted sources
    if source == "data_inventory":
        continue
    
    try:
        # Load the dataset
        ds = fcat[source].to_dask()
    except Exception as ex:
        print(f"catalog source {source} failed to load as dataset: ", ex)
        continue
    
    # Extract variable names and their long names
    variables = []
    variable_long_names = []
    
    for datavar in ds.data_vars.keys():
        long_name = ds[datavar].attrs.get('long_name', ds[datavar].attrs.get('name', ''))
        
        # Skip variables with empty long names
        if not long_name.strip():
            continue

        variables.append(datavar)
        variable_long_names.append(long_name)
    print(variables)
    print(variable_long_names)
    # Construct new metadata
    metadata = {
        'variables': variables,
        'variable-long_names': variable_long_names,
    }
    
    # Get existing metadata and update it
    source_entry = fcat[source].yaml().strip().split('\n')
    existing_metadata = {}
    for entry in source_entry:
        if entry.startswith('metadata:'):
            idx = source_entry.index(entry)
            existing_metadata = yaml.safe_load('\n'.join(source_entry[idx:]))
            break
    
    # Combine new and existing metadata
    updated_metadata = {**existing_metadata, **metadata}
    
    # Update source entry in the catalog
    new_sources_dict[source] = {
        'args': fcat[source].describe()['args'],
        'metadata': updated_metadata,
        'driver': fcat[source].describe()['plugin']
    }

# Save the updated catalog to a new YAML file
new_catalog = {
    'sources': new_sources_dict
}

with open("tco2559-ng5-cycle3.yaml", "w") as f:
    yaml.dump(new_catalog, f)
