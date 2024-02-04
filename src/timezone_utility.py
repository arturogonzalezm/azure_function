import logging
from datetime import datetime
import pytz


class PerthTimeFormatter(logging.Formatter):
    """Custom log formatter for Perth time zone."""
    converter = datetime.now

    def formatTime(self, record, datefmt=None):
        perth_tz = pytz.timezone('Australia/Perth')
        ct = self.converter(record.created, perth_tz)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            try:
                s = ct.isoformat(timespec='milliseconds')
            except TypeError:
                s = ct.isoformat()
        return s
