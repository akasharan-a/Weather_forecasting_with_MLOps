import os
from pathlib import Path
from mlops_services.src.utils.dataframe import load_parquet
from mlops_services.src.components.forecasting_models import XGB, Linear
from mlops_services.src.utils.time_utils import darts_encoders ,current_time ,Timer
from sklearn.preprocessing import StandardScaler
from darts.dataprocessing.transformers import Scaler
from mlops_services.src.components.mlflow import DartsForecastModel , Experiment ,create_signature ,save_model_local
from mlops_services.src.utils.misc import get_versions , save_as_yaml , create_folder


class Trainer:
    def __init__(self,config, logger, filename):
        self.config = config
        self.logger = logger
        self.df = load_parquet(self.config.path.final_data, filename)

        self.forecaster :XGB= None
        self.forecaster_packaged :DartsForecastModel = None
        
        self.features= self.config.features
        
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
        self.requirements = get_versions(['polars','u8darts'])
        self.model_sign = None
        self.info = {'type':self.config.experiment_name}
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


    def train(self,algo):
        args = (self.features,self.params)
        match algo:
            case "XGB":
                self.forecaster = XGB(*args)
            case "Linear":
                self.forecaster = Linear(*args)
        self.info['algorithm'] = algo    
        self.info['target'] =  self.features.target 
        self.logger.info(f"Algorithm selected: {algo}")
        
        self.logger.info(f"Training model for {self.features.target}")
        try:
            with Timer() as t:
                self.forecaster.train(self.df)
                self.forecaster_packaged = DartsForecastModel(self.forecaster)
            self.logger.info(f"Training Successfully completed in: {t.elapsed:.4f} seconds")
        except Exception  as e:
            self.logger.info(f"Training Failed - ✕ - {e}")
            raise e

    def log_experiment(self):
        self.logger.info(f"Tracking experiment using MLflow")
        exp = Experiment(experiment_name=self.config.experiment_name)
        self.info['run_id'] = None
        algo = self.forecaster.algorithm
        self.info['registered_name'] = f"Forecaster_{algo}"
        try:
            run_name = f"{algo}_{current_time('%Y_%m_%d_%H_%M_%S')}" 
            exp.create_run(run_name=run_name)
            self.info['run_id'] = exp.run_id
            self.info['run_name'] = run_name
            exp.log_param("type","DartsForecastingModel")
            exp.log_param("algorithm",algo)
            
            sig_input,sig_output,params_sig = self.sample_forecast(sample_size=100)
            self.model_sign = create_signature(model_input=sig_input,model_output=sig_output,params=params_sig)
            exp.log_model(flavor="pyfunc",model=self.forecaster_packaged,pip_requirements=self.requirements,
                            registered_model_name=self.info['registered_name'],signature=self.model_sign)
            self.logger.info(f"Experiment logged with run_id: {exp.run_id}")
        except Exception  as e:
            self.logger.info(f"Experiment logging Failed - ✕ - {e}")
        exp.end_run()
        
    def sample_forecast(self,sample_size):
        data =self.df.head(sample_size).to_dicts()
        params = {'horizon':self.config.forecast_length}
        pred = self.forecaster_packaged.predict(model_input=data,params= params)
        return (data,pred,params)
    
    def save(self):
        self.logger.info(f"Saving Model....")
        path=Path(self.config.path.model)
        model_path = path/self.info['registered_name']/'model'
        create_folder(model_path)    
        try:
            save_model_local(flavor='pyfunc',model=self.forecaster_packaged,path=model_path,pip_requirements=self.requirements,
                          registered_model_name=self.info['registered_name'],signature=self.model_sign)
            save_as_yaml(self.info,path/"model_info.yaml")

            self.logger.info(f"Model saved successfully")
        except Exception  as e:
            self.logger.info(f"Failed to save the model -> {e}")
            raise e

        

