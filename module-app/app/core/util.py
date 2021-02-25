"""
Storage

Collection of functions to interact with external storage
"""

import datetime
import json


def fillit(value, fill=2):
    """Pad the value with 0 to the given fill"""
    return str(value).zfill(fill)


def get_current_datetime():
    """Get current time in utc iso format"""
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
