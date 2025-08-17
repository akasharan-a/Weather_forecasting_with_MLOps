import os
from pathlib import Path
from mlops_services.src.utils import db_io,time_utils
import polars as pl
from sklearn.model_selection import train_test_split

class GetRawData:
    def __init__(self,config):
        self.config = config
        self.db = db_io.InfluxDB(self.config.source.raw_bucket,f"city_{self.config.city}")
        self.df = None
        self.df_train = None
        self.df_test = None
                    
    def load_from_db(self,start,end,tz):   
        start_time,end_time  = time_utils.convert_to_utc(start,end,
                                                        tz=tz,
                                                        from_format="%Y-%m-%d %H:%M",
                                                        to_format="%Y-%m-%dT%H:%M:%SZ"
                                                        )
        end_time = time_utils.include_time(end_time,format="%Y-%m-%dT%H:%M:%SZ")
        assert self.db.ping()
        self.df = self.db.fetch_as_df(start_time,end_time)
        
    def load_from_local(self):
        hist_path = Path(self.config.source.raw_local)
        try:
            self.df = pl.read_parquet(hist_path)
        except:
            raise ValueError('Failed to load local data')
        
    def split_test(self,):
        self.df_train , self.df_test = train_test_split(self.df,test_size=self.config.ML.test_split_ratio,shuffle=False)
        
    def save(self): 
        raw_folder = Path(self.config.path.raw).parent
        os.makedirs(raw_folder, exist_ok=True)        
        self.df_train.write_parquet(Path(self.config.path.raw))
        self.df_test.write_parquet(Path(self.config.path.raw_test))
    
