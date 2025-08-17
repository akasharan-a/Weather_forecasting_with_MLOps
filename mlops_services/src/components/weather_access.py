import os
import requests
import polars as pl
from mlops_services.src.utils import time_utils


class HistoricWeather():
    '''
    Open meteo historic API
    
    '''
    def __init__(self, config,city :str,):
        self.config = config
        if city  in self.config.all_cities:
            self.city = city
        else:
            raise ValueError("Undefined City is used")    
        self.base_url=os.getenv('HISTORIC_WEATHER_URL')
        city_co_ords = getattr(self.config.co_ordinates,self.city)
        self.params  = {
        "latitude": city_co_ords.latitude,
        "longitude": city_co_ords.longitude,
        "timezone": self.config.time.timezone,
        "timeformat": self.config.time.timeformat
        }
        
    def pull_data(self):
        
        if self.config.measurements.units == 'metric':
            units = {"temperature_unit": self.config.measurements.metric.temperature_unit,
                    "wind_speed_unit": self.config.measurements.metric.wind_speed_unit,
                    "precipitation_unit": self.config.measurements.metric.precipitation_unit
                    }
            self.params = self.params | units
        if self.config.time.frequency == 'hourly':
            self.params['hourly'] = ",".join(self.config.historic_parameters)
    
        response = requests.get(self.base_url, params=self.params)
        response.raise_for_status()

        data = response.json()
        if (self.config.time.frequency == 'hourly') & ('hourly' not in data):
            raise ValueError("Invalid response structure: 'hourly' data missing")
        return data 
            
    def get_df(self,start,end):
        
        self.params["start_date"] = start
        self.params["end_date"] = end
        data = self.pull_data()
        try:
            df= pl.DataFrame(data['hourly'])
            df = df.with_columns(pl.col("time").str.to_datetime(
                                                    format="%Y-%m-%dT%H:%M",
                                                    time_zone=data['timezone'])
                                                    .alias("time_local"))
            df = df.with_columns(pl.col("time_local").dt.convert_time_zone("UTC")
                                                    .alias("time"),
                                pl.lit(self.city).alias("city")
                                )
            for key in data.keys():
                if key not in ['hourly','hourly_units']:
                    df = df.with_columns(pl.lit(data[key]).alias(key))
        except:
            raise 
        return df
        
