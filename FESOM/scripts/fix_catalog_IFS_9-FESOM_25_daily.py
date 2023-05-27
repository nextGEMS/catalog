import yaml


with open("IFS_28-FESOM_25-cycle3.yaml", "r") as file:
    catalog1 = yaml.safe_load(file)

catalog1["sources"]["2D_daily_native"]["args"]["urlpath"] = [
    "/work/bm1344/AWI/Cycle3/IFS_28-FESOM_25-cycle3/daily_means/*/*.nc"
]

catalog1["sources"]["2D_daily_0.25deg"] = {
    "args": {
        "chunks": {"nod2": -1, "time": 1},
        "urlpath": [
            "/work/bm1344/AWI/Cycle3/FESOM/IFS_28-FESOM_25-cycle3/025/2D_daily_native/*/*.nc"
        ],
    },
    "driver": "netcdf",
    "metadata": {"source": "2D_daily_native"},
}

catalog1["sources"]["2D_daily_1deg"] = {
    "args": {
        "chunks": {"nod2": -1, "time": 1},
        "urlpath": [
            "/work/bm1344/AWI/Cycle3/FESOM/IFS_28-FESOM_25-cycle3/100/2D_daily_native/*/*.nc"
        ],
    },
    "driver": "netcdf",
    "metadata": {"source": "2D_daily_native"},
}

catalog1["sources"]["3D_monthly_0.25deg"] = {
    "args": {
        "chunks": {"nod2": -1, "elem": -1, "time": 1},
        "urlpath": [
            "/work/bm1344/AWI/Cycle3/IFS_28-FESOM_25-cycle3/monthly_means/025/*/*.nc"
        ],
    },
    "driver": "netcdf",
    "metadata": {"source": "3D_monthly_native"},
}

catalog1["sources"]["3D_monthly_1deg"] = {
    "args": {
        "chunks": {"nod2": -1, "elem": -1, "time": 1},
        "urlpath": [
            "/work/bm1344/AWI/Cycle3/IFS_28-FESOM_25-cycle3/monthly_means/100/*/*.nc"
        ],
    },
    "driver": "netcdf",
    "metadata": {"source": "3D_monthly_native"},
}
with open("IFS_28-FESOM_25-cycle3.yaml", "w") as file:
    yaml.dump(catalog1, file)
