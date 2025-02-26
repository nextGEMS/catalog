from pystac import Catalog, Item, Asset, MediaType
import datetime
import pandas as pd
import numpy as np
import yaml
from collections import defaultdict
from typing import Union
from pathlib import Path
import intake_tools
import logging

logger = logging.getLogger("intake_to_stac")
logging.basicConfig()
logger.setLevel(logging.ERROR)


class catalog_generator:
    defaults: dict
    catalog: any

    def __init__(self) -> None:
        self.read_defaults()
        self.create_basic_catalog()

    def read_defaults(
        self, source: Union[Path, str] = Path(__file__).parent / "defaults.yaml"
    ):
        with open(source) as source_file:
            self.defaults = yaml.safe_load(source_file)

    def create_basic_catalog(self) -> None:
        self.catalog = Catalog(**self.defaults["catalog_properties"])

    def parse_catalog(self, catalog):
        intake_tools.traverse_tree(
            catalog,
            None,
        )

    def _gen_item(self, name, sim):
        time_range = __class__.get_time_range(sim)
        item = Item(
            id=name,
            geometry=None,  # Replace with actual geometry, if available
            bbox=None,  # Replace with actual bounding box, if available
            **time_range,
            properties=sim.describe()["metadata"],
        )
        self._add_assets(sim, item)
        return item

    def _add_assets(self, sim, item):
        for params in intake_tools.iterate_user_parameters(sim):
            asset = self._gen_asset(sim, params)
            item.add_asset(key=f"data_{asset.title}", asset=asset)

    def _gen_asset(self, sim, params) -> Asset:
        asset_href = sim(**params).urlpath
        __class__._check_href(sim, params, asset_href)
        logger.debug(asset_href)
        if asset_href.endswith (".nc"):
            return self._gen_nc_asset(sim, params)
        elif asset_href.endswith(".zarr") or asset_href.endswith(".parq") or asset_href.startswith("reference:"):
            return self._gen_zarr_asset(sim, params)
        else:
            raise RuntimeError(f"what is this? {asset_href}")
        
    def _gen_nc_asset(self, sim, params):
        asset_href = sim(**params).urlpath
        param_string = "_".join([str(x) for x in list(params.values())])
        protocol = __class__._get_protocol(asset_href)
        extra_fields = dict(
            metadata=dict(roles=["data", "netcdf", protocol]),
            xarray=dict(open_kwargs=dict(consolidated=True)),
        )
        asset = Asset(
            href=asset_href,
            media_type=MediaType.NETCDF,
            title=param_string,
            description=sim.metadata.get("description", "description"),
            extra_fields=extra_fields,
        )
        return asset

    def _get_protocol(asset_href):
        protocol = asset_href.split(":")[0]
        if protocol == asset_href:
            protocol = "file"
        return protocol

    def _gen_zarr_asset(self, sim, params) -> Asset:
        asset_href = str(sim(**params).urlpath)
        param_string = "_".join([str(x) for x in list(params.values())])
        protocol = __class__._get_protocol(asset_href)
        extra_fields = dict(
            metadata=dict(roles=["data", "zarr", protocol]),
            xarray=dict(open_kwargs=dict(consolidated=True)),
        )
        asset = Asset(
            href=asset_href,
            media_type=MediaType.ZARR,
            title=param_string,
            description="description",
            extra_fields=extra_fields,
        )
        return asset

    @staticmethod
    def _check_href(sim, params, href):
        if isinstance(href, list):
            raise RuntimeError(
                f"URI for {sim(**params).name} is a list. Can only handle single files."
            ) from None
        # elif "*" in href:
        #    raise RuntimeError("Found a * in the href for {sim(**params).name}. Needs to be a real file name: {href}") from None

    @staticmethod
    def query_metadata(entry, variants):
        for variant in variants:
            if variant in entry.metadata:
                return entry.metadata[variant]

    # default return is None

    @staticmethod
    def get_time_range(entry):
        start_datetime = __class__.query_metadata(
            entry,
            ("start_datetime", "start_time", "time_start", "date_start", "start_date"),
        )
        end_datetime = __class__.query_metadata(
            entry, ("end_datetime", "end_time", "time_end", "date_end", "end_date")
        )
        if start_datetime is None or end_datetime is None:
            try:
                ds = entry.to_dask()
                start_datetime = ds.time.values[0]
                end_datetime = ds.time.values[-1]
            except (KeyError, FileNotFoundError, IndexError):
                logger.debug(
                    f"Could not get time range for {entry.name} by loading it. Please supply 'start_datetime' and 'end_datetime' in the metadata.",
                )
                return dict(datetime=datetime.datetime.now())
            except Exception as e:
                logger.critical(
                    f"Ran into {type(e)}: {e}, when trying to get start and end times for {entry.name}"
                )
                raise e

        convert_time = __class__.convert_time
        return dict(
            start_datetime=convert_time(start_datetime),
            end_datetime=convert_time(end_datetime),
        )

    @staticmethod
    def convert_time(time: np.datetime64) -> datetime.datetime:
        return pd.to_datetime(time).to_pydatetime()

    def _sort_by_simulation_id(self, entries: dict) -> dict:
        simulations = defaultdict(list)
        for name, entry in entries.items():
            simulations[entry.describe()["metadata"]["simulation_id"]].append(entry)
        return simulations
