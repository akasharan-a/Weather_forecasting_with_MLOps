import os
from pathlib import Path
from mlops_services.src.utils import db_io, time_utils, logs
import polars as pl


class GetRawData:
    def __init__(self, config,logger,filename):
        self.config = config
        self.logger = logger
        self.filename = filename
        self.df = None
        # self.logger = logs.get_parent_logger()

    def load_from_db(self, city, start, end, tz):
        self.db = db_io.InfluxDB(self.config.source.raw_online, f"city_{city}")
        start_time, end_time = time_utils.convert_to_utc(
            start,
            end,
            tz=tz,
            from_format="%Y-%m-%d %H:%M",
            to_format="%Y-%m-%dT%H:%M:%SZ",
        )
        end_time = time_utils.include_time(end_time, format="%Y-%m-%dT%H:%M:%SZ")
        assert self.db.ping()
        try:
            self.df = self.db.fetch_as_df(start_time, end_time)
            self.logger.info("Successfully loaded data from DB")
        except:
            self.logger.info("Failed to load data from DB")
    def load_from_local(self, city):
        hist_path = Path(self.config.source.raw_local) / f"historic_{city}.parquet"
        try:
            self.df = pl.read_parquet(hist_path)
            self.logger.info("Successfully loaded local data")
        except:
            self.logger.info("Failed to load local data")
            raise ValueError("Failed to load local data")

    def save(self):
        raw_folder = Path(self.config.folder.raw)
        file_path = raw_folder / f"{self.filename}.parquet"
        os.makedirs(raw_folder, exist_ok=True)
        self.df.write_parquet(file_path)
        self.logger.info(f"Data saved in : {file_path}")