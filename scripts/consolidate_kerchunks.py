#!/usr/bin/env python3

import re
import os
import fsspec
from pathlib import Path
from kerchunk.combine import MultiZarrToZarr
from fsspec.implementations.reference import LazyReferenceMapper
import logging


import intake
import intake_tools
from intake_xarray.xzarr import ZarrSource
from tempfile import TemporaryDirectory
import shutil


logger = logging.getLogger("consolidate_kerchunk")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def consolidate_fsspec(entry: ZarrSource, storage_prefix: Path) -> None:
    print(type(entry))
    Path(storage_prefix).mkdir(parents=True, exist_ok=True)
    files = [re.sub("reference::", "", x) for x in entry.urlpath]
    id = entry.name
    parqdir = str(storage_prefix / f"{id}.parq")
    if Path(parqdir).exists():
        raise FileExistsError(
            f"Target dir for Parquet file already exists: {parqdir}"
        ) from None
    fs = fsspec.filesystem("file")
    with TemporaryDirectory(dir=str(storage_prefix), prefix=f"{id}_") as tpd:
        logger.debug (f" {tpd=}")
        tempparqdir = f"{tpd}/{id}.parq"
        logger.debug(f"consolidating to {tempparqdir}")
        out = LazyReferenceMapper.create(record_size=1000, root=tempparqdir, fs=fs)
        MultiZarrToZarr(files, concat_dims="time", out=out).translate()
        out.flush()
        shutil.move(tempparqdir, parqdir)


def process_entry(cat, child, position):
    sim = cat[child]
    for params in intake_tools.iterate_user_parameters(sim, ignore=["variables"]):
        print(f"processing {'.'.join(position)}.{child}")
        asset = sim(**params)
        urlpath = asset.urlpath
        storage_prefix = Path("/scratch/k/k202134/kerchunks/") / ("/".join(position))
        if isinstance(urlpath, list):
            if len(urlpath) > 1:
                if urlpath[0].startswith("reference::"):
                    if len(params):
                        raise RuntimeError(
                            f"Cannot handle parameterized datasets with multiple assets! {'.'.join(position)}.{child}"
                        )
                    try:
                        consolidate_fsspec(asset, storage_prefix)
                    except FileExistsError as e:
                        logging.warning(
                            f"cannot process {'.'.join(position)}.{child}: {e}"
                        )


def consolidate_catalog(uri):
    cat = intake.open_catalog(uri)
    intake_tools.traverse_tree(
        cat=cat, subcat_callback=None, entry_callback=process_entry
    )


if __name__ == "__main__":
    consolidate_catalog("../catalog.yaml")
