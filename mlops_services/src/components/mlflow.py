import os
import mlflow
from mlflow.models.signature import infer_signature
import polars as pl
import pandas as pd
from mlops_services.src.components.forecasting_models import BaseModel
from typing import List, Dict, Any

class DartsForecastModel(mlflow.pyfunc.PythonModel):
    def __init__(self, darts_model: BaseModel):
        super().__init__()
        self.model = darts_model

    def predict(self, model_input, params):
        # print("type : ",type(model_input))
        if isinstance(model_input, pd.DataFrame):
            df = pl.from_dataframe(model_input)
        else:
            df = pl.from_dicts(model_input)
        forcast_horizon = params["horizon"]
        prediction = self.model.forecast(df, horizon=forcast_horizon)
        return prediction.to_dicts()


class Experiment:
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        os.environ["MLFLOW_TRACKING_USERNAME"] = os.getenv("DAGSHUB_USER_NAME")
        os.environ["MLFLOW_TRACKING_PASSWORD"] = os.getenv("DAGSHUB_USER_TOKEN")
        # print(
        #     "OS ",
        #     os.getenv("MLFLOW_TRACKING_USERNAME"),
        #     os.getenv("MLFLOW_TRACKING_PASSWORD"),
        #     "\n",
        #     os.getenv("DAGSHUB_TRACKING_URI"),
        # )
        mlflow.set_tracking_uri(os.getenv("DAGSHUB_TRACKING_URI"))
        mlflow.set_experiment(experiment_name=self.experiment_name)
        self.active_run = None
        self.run_id = None

    def create_run(self, run_name: str = None):
        self.active_run = mlflow.start_run(run_name=run_name)
        self.run_id = self.active_run.info.run_id
        mlflow.log_param("run_id", self.run_id)
        return self.active_run

    def load_run(self, run_id: str):
        self.active_run = mlflow.start_run(run_id=run_id)
        self.run_id = self.active_run.info.run_id
        return self.active_run

    def log_param(self, key: str, value):
        mlflow.log_param(key, value)

    def log_metric(self, key: str, value):
        mlflow.log_metric(key, value)

    def log_model(
        self,
        flavor,
        model,
        artifact_path: str = "model",
        pip_requirements: list = [],
        registered_model_name: str = None,
        signature=None,
    ):

        if flavor == "pyfunc":
            mlflow.pyfunc.log_model(
                artifact_path=artifact_path,
                python_model=model,
                pip_requirements=pip_requirements,
                registered_model_name=registered_model_name,
                signature=signature
            )
        elif flavor == "sklearn":
            mlflow.sklearn.log_model(sk_model=model, artifact_path=artifact_path)
        else:
            raise ValueError("Unsupported flavor type")

    def end_run(self):
        if self.active_run:
            mlflow.end_run()
            self.active_run = None

    def log(self, model, metrics: dict):
        with mlflow.start_run(experiment_id=1) as run:
            mlflow.log_param("run", run.info.run_id)
            mlflow.log_param("model_type", "XGB")  # example
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("mape", mape)
            mlflow.pyfunc.log_model(
                "darts_pyfunc_model",
                python_model=DartsForecastModel(model_xgb),
                pip_requirements=["u8darts"],
                registered_model_name="DartsXGB",
                signature=infer_signature(
                    model_input=series_test.to_dataframe(),
                    model_output=pred,
                    params={"horizon": 24},
                ),
            )


def create_signature(model_input, model_output, params):
    sign = None
    try :
        sign =  infer_signature(model_input, model_output, params)
    except Exception as e:
        print(f"Signature inference failed: {e}")
    return sign

def load_model(flavor,model_path):
    if flavor == "pyfunc":
        model = mlflow.pyfunc.load_model(model_path)
        return model
    else:
        raise ValueError("Unsupported flavor type")
    


def save_model_local(flavor, model, path,pip_requirements,
                          registered_model_name,signature=None):
    if flavor == "pyfunc":
        mlflow.pyfunc.save_model(python_model=model, path = path,pip_requirements=pip_requirements,
                                 signature=signature)
    else:
        raise ValueError("Unsupported flavor type")
