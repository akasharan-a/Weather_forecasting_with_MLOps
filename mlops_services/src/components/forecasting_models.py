import os
from pathlib import Path
from mlops_services.src.utils.dataframe import load_parquet

from darts import TimeSeries
from darts.models import LinearRegressionModel, XGBModel



class BaseModel:
    def __init__(self,df,params):        
        pass
    def transform_data(self):
        time_col = self.config.features.time.std
        ts_data = TimeSeries.from_dataframe(
            self.df, time_col=time_col, value_cols=self.columns[1:].values
        )
        self.y = ts_data[self.config.features.target]
        self.X_past, self.X_future = None, None

        if self.config.features.past_feats:
            self.logger.info(f"Using past features: {self.config.features.past_feats}")
            self.train_X_past = ts_data[self.config.features.past_feats]
        if self.config.features.future_feats:
            self.logger.info(
                f"Using future features: {self.config.features.future_feats}"
            )
            self.train_X_future = ts_data[self.config.features.future_feats]


    def train(self):
        self.model.fit(series = self.train_y,past_covariates = self.train_X_past, future_covariates = self.train_X_future)
    
    def save(self):
        self.model.train("mlops_services/models/XGB.model")

class XGB(BaseModel):
    def __init__(self):
        super().__init__()
        self.algorithm = "XGB"
        self.model = XGBModel(**self.base_params)


class Linear(BaseModel):
    def __init__(self):
        super().__init__()
        self.algorithm = "Linear"
        self.model = LinearRegressionModel(**self.base_params)
