import os
from pathlib import Path
from mlops_services.src.utils.dataframe import load_parquet
from mlops_services.src.utils.misc import read_yaml
from mlops_services.src.components.mlflow import DartsForecastModel , Experiment
from mlops_services.src.components.mlflow import load_model
from darts.metrics import mape ,mae , rmse , r2_score ,ae
from mlops_services.src.utils.static_visuals import line_chart

class Evaluator:
    def __init__(self, config, logger, filename):
        self.config = config
        self.logger = logger
        self.df = load_parquet(self.config.path.final_data, filename)
        self.info = read_yaml(Path(self.config.path.model) / "model_info.yaml")
        self.forecaster_packaged : DartsForecastModel = None
        self.forecaster = None

    def load_model(self, source="local"):
        fetch_model_from_registry = True
        if source == "local":
            model_path = (
                Path(self.config.path.model) / self.info["registered_name"] / "model"
            )
            self.logger.info(f"Loading Forescater from local..")
            try:
                self.forecaster_packaged = load_model(
                    flavor="pyfunc", model_path=model_path
                )
                self.logger.info(f"Successful!!")
                fetch_model_from_registry = False

            except Exception as e:
                self.logger.info(f"Failed to load from local -- X  -- {e}")

        if fetch_model_from_registry:
            self.logger.info(f"Loading Forescater from online registry..")
            try:
                model_uri = f"runs:/{self.info['run_id']}/model"
                self.forecaster_packaged = load_model("pyfunc", model_uri)
                self.logger.info(f"Successful!!")

            except Exception as e:
                self.logger.info(f"Failed -- X  -- {e}")

        if self.forecaster_packaged:
            self.forecaster = self.forecaster_packaged.unwrap_python_model().model
        else:
            raise ValueError("Model not loaded")
    
    def backtest(self,horizon=1):
        metrics_to_use = [mape ,mae , rmse] 
        metrics = {}
        y_test, X_past_test, X_future_test = self.forecaster.transform_input(self.df)
        backtest_metrics =  self.forecaster.model.backtest(series = y_test, past_covariates=X_past_test, future_covariates = X_future_test,
                                                           forecast_horizon=horizon,retrain=False,metric=metrics_to_use)
        metrics = dict(zip([str(element.__name__) for element in metrics_to_use],backtest_metrics.tolist()))
        return metrics
    
    def hist_forecast(self,horizon=1):
        return self.forecaster.historical_forecast(self.df,horizon=1)
    
    def generate_plots(self,historical_forecast):
        data = 
        charts={
           "line_chart": line_chart( , x:str ,y:list,xlabel=None, ylabel=None, title=None)
        }
        pass
    
    def evaluate_model(self):
        ##histrical_forecast
        historical_forecast = self.hist_forecast(horizon=1)
        self.logger.info(f"Historical forecast done!")

        ##Backtesting
        backtest_metrics = self.backtest(horizon=1)
        self.logger.info(f"Backtesting results : {backtest_metrics}")
        
        ##
        plots = self.generate_plots(historical_forecast)
        self.logger.info(f"Generated visuals : {plots.keys()}")

        
        pass
