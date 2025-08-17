from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


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
        
    