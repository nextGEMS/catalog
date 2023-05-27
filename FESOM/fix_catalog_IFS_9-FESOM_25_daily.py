import yaml


with open("IFS_28-FESOM_25-cycle3.yaml", "r") as file:
    catalog1 = yaml.safe_load(file)

catalog1["sources"]["2D_daily_native"]["args"]["urlpath"] = [
    "/work/bm1344/AWI/Cycle3/IFS_28-FESOM_25-cycle3/daily_means/*/*.nc"
]

with open("IFS_28-FESOM_25-cycle3.yaml", "w") as file:
    yaml.dump(catalog1, file)
