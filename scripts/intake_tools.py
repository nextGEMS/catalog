import logging
from collections.abc import Iterable

logger = logging.getLogger("intake_tools")


def iterate_user_parameters(entry, fixed_keys=None, ignore = list()):
    if fixed_keys is None:
        fixed_keys = {}
    user_parameters = {x["name"] : x for x in entry.describe()["user_parameters"] if x["name"] not in ignore}
    names = list(user_parameters.keys())
    remaining_keys = [x for x in names if x not in fixed_keys.keys()]
    if len(remaining_keys) == 0:
        if len (fixed_keys) == 0:
            yield dict()
        return
    param = user_parameters[remaining_keys[0]]
    logger.debug(param)
    key = param["name"]
    for value in param["allowed"]:
        fixed_keys[key] = value
        logger.debug(fixed_keys)
        if len(remaining_keys) == 1:
            logger.debug(fixed_keys)
            yield fixed_keys
        else:
            yield from iterate_user_parameters(entry, fixed_keys.copy())


def warn_esm_cat(cat, child, position):
    logging.warning(
        f"skipping {'.'.join(position)}.{child}, as it seems to be an intake-esm catalog"
    )


def traverse_tree(
    cat,
    subcat_callback,
    entry_callback,
    esm_cat_callback=warn_esm_cat,
    levels=0,
    position=list(),
):
    """Traverses an intake tree and call a function on everything it finds in it.
    subcat_callback is called on anything iterable (should be sub-catalogs)
    entry_callback is called on anything not iterable (should be datasets)
    esm_cat_callback will be called on intake_esm_catalogs. Defaults to a warning message, as loading them can consume a lot of memory and time.
    """
    if levels and (levels - 1 < len(position)):
        return
    for child in list(cat):
        logging.debug(f"processing {child}")
        if detect_esm_cat(cat, child, position):
            esm_cat_callback(cat, child, position)
            continue
        try:
            cat[child]
        except FileNotFoundError as missing:
            logging.critical(
                f"Error processing {'.'.join(position)}.{child}: File not found: {missing}"
            )
            continue

        if isinstance(cat[child], Iterable):
            if subcat_callback is not None:
                subcat_callback(cat, child, position)
            traverse_tree(
                cat[child],
                subcat_callback,
                entry_callback,
                levels=levels,
                position=position + [child],
            )
        else:
            if entry_callback is not None:
                entry_callback(cat, child, position)


def detect_esm_cat(cat, child, position):
    try:
        if "esm_datastore" in str(cat._entries[child]._driver):
            return True
    except Exception as e:
        logging.error(
            f"Can't really decide the type of \n{position}{child}\nran into {e}"
        )
    return False
