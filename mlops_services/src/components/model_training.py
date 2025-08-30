import os
from pathlib import Path
from mlops_services.src.utils.dataframe import load_parquet
from mlops_services.src.components.forecasting_models import XGB,Linear
from mlops_services.src.utils.time_utils import darts_encoders
from sklearn.preprocessing import StandardScaler
from darts.dataprocessing.transformers import Scaler

class Common:
    def __init__(self, config, logger, filename):
        self.config = config
        self.logger = logger
        self.df = load_parquet(self.config.folder.processed, filename)

class Trainer(Common):
        def __init__(self):
            super().__init__()
            self.params = dict(
                lags=self.config.lag.y_lags,
                lags_past_covariates=self.config.lag.past_lags,
                lags_future_covariates=[
                    self.config.lag.future_lags,
                    self.config.lag.future_lags,
                ],
                output_chunk_length=self.config.lag.forecast_length,
                random_state=self.config.random_state,
                add_encoders=self.add_encoders(),
            )
            self.model = None
        
        def add_encoders(self):
            encoders = {}
            if self.config.features.past_encoders:
                self.logger.info(
                    f"Using past encoders: {self.config.features.past_encoders}"
                )
                encoders = encoders | darts_encoders(self.config.features.past_encoders,"past")

            if self.config.features.future_encoders:
                self.logger.info(
                    f"Using future encoders: {self.config.features.future_encoders}"
                )
                encoders = encoders | darts_encoders(self.config.features.future_encoders,"future")
            
            if encoders:
                return encoders|{'transformer': Scaler()}   
            else:
                return None    
                                        
        def select_algorithm(self,algo):
            match algo:
                case 'XGB':
                       self.model = XGB(selfself.params)
                case 'Linear':       
                        self.model = Linear(self.params)

        def train(self):
            self.model