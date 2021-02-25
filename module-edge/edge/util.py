"""
Util

- Convert Dynamodb json to regular json
- Get timestampe
"""

import datetime
import json
import re
from datetime import datetime, timezone
from decimal import Decimal


def _object_hook(dct):  # pylint: disable=too-many-branches,too-many-return-statements
    """Dynamodb object hook to return python values"""

    try:
        # First - Try to parse the dct as DynamoDB parsed
        if "BOOL" in dct:
            return dct["BOOL"]
        if "S" in dct:
            val = dct["S"]
            try:
                return datetime.strptime(val, "%Y-%m-%dT%H:%M:%S.%f")
            except:  # pylint: disable=bare-except
                return str(val)
        if "SS" in dct:
            return list(dct["SS"])
        if "N" in dct:
            if (  # pylint: disable=no-else-return
                re.match(r"^-?\d+?\.\d+?$", dct["N"]) is not None
            ):
                return float(dct["N"])
            else:
                try:
                    return int(dct["N"])
                except:  # pylint: disable=bare-except
                    return int(dct["N"])
        if "B" in dct:
            return str(dct["B"])
        if "NS" in dct:
            return set(dct["NS"])
        if "BS" in dct:
            return set(dct["BS"])
        if "M" in dct:
            return dct["M"]
        if "L" in dct:
            return dct["L"]
        if "NULL" in dct and dct["NULL"] is True:
            return None
    except:  # pylint: disable=bare-except
        return dct

    # In a Case of returning a regular python dict
    for key, val in dct.items():
        if isinstance(val, str):
            try:
                dct[key] = datetime.strptime(val, "%Y-%m-%dT%H:%M:%S.%f")
            except:  # pylint: disable=bare-except
                # This is a regular Basestring object
                pass

        if isinstance(val, Decimal):
            if val % 1 > 0:
                dct[key] = float(val)
            else:
                dct[key] = int(val)

    return dct


def dynamodb_loads(content: str, *args, **kwargs):
    """
    Load dynamodb json format to a python dict.

    :param content - the json string to convert
    :returns python dict object

    """

    kwargs["object_hook"] = _object_hook

    return json.loads(content, *args, **kwargs)


def get_current_datetime():
    """Get current time in utc iso format"""
    return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
