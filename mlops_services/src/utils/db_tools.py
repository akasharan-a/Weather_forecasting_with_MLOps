import os
from pathlib import Path
import polars as pl
from influxdb_client  import InfluxDBClient , WriteOptions


class DB():
    def __init__(self,bucket,city):
        self.bucket = bucket
        self.city = city
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
        except:
            raise  
          
    def ping(self):  
        if self.health.status == "pass":
            print("InfluxDB connection successful.")
        else:
            print(f"InfluxDB connection problem: {self.health.message}")  

    def push_to_db(self,df:pl.DataFrame):
        self.write_api.write(
        bucket=self.bucket,
        org=self.org,
        record=df.to_pandas(),  # convert Polars to pandas DataFrame for compatibility
        data_frame_timestamp_column="timestamp",
        data_frame_measurement_name=f'city_{self.city}'
    )

    def pull_as_df(self,start: str, end: str) -> pl.DataFrame :
        query = f'''
        from(bucket: "{self.bucket}")
        |> range(start: {start}, stop: {end})
        |> filter(fn: (r) => r._measurement == "city_{self.city}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        tables = self.query_api.query_data_frame(query, org=self.org)
        return pl.from_pandas(tables)

    

    def check_data_exists(city:str,last_ts:str):
        
        pass