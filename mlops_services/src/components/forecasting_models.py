import os
from pathlib import Path
import polars as pl

from darts import TimeSeries
from darts.models import LinearRegressionModel, XGBModel


class Base:
    def __init__(self, config,logger, filename):
        self.config = config
        self.base_settings = dict(lags=self.config.lag.y_lags,
            lags_past_covariates=self.config.lag.past_lags,
            lags_future_covariates=[self.config.lag.future_lags,self.config.lag.future_lags],
            output_chunk_length=self.config.lag.forecast_length,
            random_state=self.config.random_state)
        self.df = pl.read_parquet(Path(self.config.folder.processed) / f"{filename}.parquet")
   
    def setup_data(self):
        time_col = self.config.features.time.std
        ts_data = TimeSeries.from_dataframe(self.df,time_col=time_col,value_cols=self.columns[1:].values)
        self.train_y = ts_data[self.config.features.target]
        self.train_X_past , self.train_X_future = None , None
        
        if self.config.features.past_feats:
            self.train_X_past = ts_data[self.config.features.past_feats]
        if self.config.features.future_feats:
            self.train_X_past = ts_data[self.config.features.future_feats]
            
    def add_encoders(self):
        pass
    def train(self):
        self.model.fit()

class XGB(Base):
    def __init__(self):
        super().__init__()
        self.algorithm = "XGB"
        self.model = XGBModel(**self.base_settings
        )


class Linear(Base):
    def __init__(self):
        super().__init__()
        self.algorithm = "Linear"
        self.model = LinearRegressionModel(**self.base_settings)
        pass

