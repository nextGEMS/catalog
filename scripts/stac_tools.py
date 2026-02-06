from pystac import Catalog
from typing import List

def get_subcat(cat: Catalog, path : List[str]):
    for p in path:
        cat = cat.get_child(p)
    return cat