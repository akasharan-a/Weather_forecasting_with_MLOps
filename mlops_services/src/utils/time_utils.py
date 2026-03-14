from datetime import datetime, timedelta
import time
from zoneinfo import ZoneInfo
import numpy as np

def add_hour(time, hour: int):
    pass

def include_time(time,format):
    time_pr = datetime.strptime(time,format)
    time_pr+=timedelta(seconds=1)
    return time_pr.strftime(format)
    
def ceil_day(time,ts_format: str):
    dt_naive = datetime.strptime(time, ts_format)
    pass

def convert_to_utc(*times ,tz: str, from_format:str, to_format:str):
    local_tz =ZoneInfo(tz)
    times_utc = []
    print(times)
    for time in times:
        dt_naive = datetime.strptime(time, from_format)
        dt_localized = dt_naive.replace(tzinfo=local_tz)
        dt_utc = dt_localized.astimezone(ZoneInfo("UTC"))
        times_utc.append(dt_utc.strftime(to_format))
    return *times_utc,

     
def darts_encoders(encoders:list):
    def _daily_cycle(idx):
        # Convert hour to radians for cosine (full cycle 24 hours)
        hour = idx.hour
        radians = 2 * np.pi * hour / 24.0
        # Cosine naturally peaks at 0 radians, so shift by 12 hours (pi radians)
        value = np.cos(radians - np.pi)
        return value
    def _monthly_cycle(idx):
        return 0
    all_encoders = {'daily_cycle':_daily_cycle,
                          'monthly_cycle':_monthly_cycle
    }
    out_encoders =[]
    for enc in encoders:
        out_encoders.append(all_encoders[enc])
    return  out_encoders

def current_time(format):
    return datetime.now().strftime(format)


class Timer:
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        if self.verbose:
            print(f"Elapsed time: {self.elapsed:.4f} seconds")
