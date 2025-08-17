import os
from pathlib import Path
import polars as pl
from influxdb_client  import InfluxDBClient , WriteOptions
from datetime import datetime, timezone

class InfluxDB():
    def __init__(self,bucket,measurement):
        self.bucket = bucket
        self.measurement = measurement
        self.url=os.getenv('INFLUXDB_URL')
        self.org=os.getenv('INFLUXDB_ORG')
        self.token=os.getenv('INFLUXDB_TOKEN')
        try:
            client = InfluxDBClient(url = self.url,
                                    org = self.org,
                                    token = self.token
                                    )
            self.health = client.health()
            self.write_api = client.write_api(write_options=WriteOptions(batch_size=500))
            self.query_api = client.query_api()
            self.delete_api = client.delete_api()
        except:
            raise  
          
    def ping(self):  
        if self.health.status == "pass":
            print("InfluxDB connection successful.")
            return(True)
        else:
            print(f"InfluxDB connection problem: {self.health.message}")
            return(False)  
        
    def push_to_db(self,df:pl.DataFrame,time_col:str):
        self.write_api.write(
        bucket=self.bucket,
        org=self.org,
        record=df.to_pandas(),  # convert Polars to pandas DataFrame for compatibility
        data_frame_timestamp_column=time_col,
        data_frame_measurement_name=self.measurement
    )

    def fetch_as_df(self,start: str, end: str ) -> pl.DataFrame :
        query = f'''
        from(bucket: "{self.bucket}")
        |> range(start: {start}, stop: {end})
        |> filter(fn: (r) => r._measurement == "{self.measurement}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        tables = self.query_api.query_data_frame(query, org=self.org)
        return pl.from_pandas(tables)
    
    def delete_city(self):
        start = "1970-01-01T00:00:00Z"
        stop = datetime.now(timezone.utc).isoformat()  # Current time in RFC3339 format
        # Predicate can be empty to delete all data regardless of measurement/tags
        predicate = f'_measurement="{self.measuremnt}"'
        bucket = self.bucket 
        org = self.org
        self.delete_api.delete(start=start, stop=stop, predicate=predicate, bucket=bucket, org=org)

    def check_data_exists(city:str,last_ts:str):
        
        pass