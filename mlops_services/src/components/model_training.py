import os
from pathlib import Path
from mlops_services.src.utils.dataframe import load_parquet
from mlops_services.src.components.forecasting_models import XGB, Linear
from mlops_services.src.utils.time_utils import darts_encoders
from sklearn.preprocessing import StandardScaler
from darts.dataprocessing.transformers import Scaler


class Trainer:
    def __init__(self,config, logger, filename):
        self.config = config
        self.logger = logger
        self.df = load_parquet(self.config.folder.processed, filename)

        self.forecaster = None
        self.features = self.config.features
        
        self.logger.info(f"Using past features: {self.features.past_feats}")
        self.logger.info(f"Using future features: {self.features.future_feats}")
        
        self.params = dict(
            lags=self.config.lag.y_lags,
            lags_past_covariates=self.config.lag.past_lags,
            lags_future_covariates=[
                self.config.lag.future_lags,
                self.config.lag.future_lags,
            ],
            output_chunk_length=self.config.forecast_length,
            random_state=self.config.random_seed,
            add_encoders=self.add_encoders(),
        )

    def add_encoders(self):
        
        custom_encoders={}
        ## 'custom': {'past': [encode_year]},
        future_encoders = self.config.features.custom_encoders.future
        if future_encoders:
            self.logger.info(
                f"Adding future encoders: {future_encoders}"
            )
            custom_encoders = custom_encoders | {'future':darts_encoders(future_encoders)}

        if custom_encoders:
            encoders = {'custom':custom_encoders}
            return encoders | {"transformer": Scaler()}
        else:
            return None

    def select_algorithm(self, algo):
        args = (self.features,self.params)
        match algo:
            case "XGB":
                self.forecaster = XGB(*args)
            case "Linear":
                self.forecaster = Linear(*args)
        self.logger.info(f"Algorithm selected: {algo}")

    def train(self):
        self.logger.info(f"Training started --->")
        try:
            self.forecaster.train(self.df)
            self.logger.info(f"Training Successfull - ✓")
        except Exception  as e:
            self.logger.info(f"Training Failed - ✕ - {e}")
            raise e


class Evaluation:
    def __init__(self,config, logger, filename):
        self.config = config
        self.logger = logger
        self.df = load_parquet(self.config.folder.processed, filename)


