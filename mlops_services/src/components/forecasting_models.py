import os
from pathlib import Path
import polars as pl
from mlops_services.src.utils import logs, time_utils
import warnings
warnings.filterwarnings("ignore")  # suppress all warnings
from darts import TimeSeries
from darts.models import LinearRegressionModel, XGBModel


class BaseModel:
    def __init__(self, features, params):
        self.target = features.target
        self.time_feature = features.time.std
        self.past_features = features.past_feats
        self.future_features = features.future_feats
        self.base_params = params
        self.created_at = time_utils.current_time(format="%Y-%m-%d %H:%M:%S")
        self.model = None
        self.is_trained = False
        self.max_forecast= params['output_chunk_length'] if self.past_features else None

    def transform_input(self, df:pl.DataFrame):
        ts_data = TimeSeries.from_dataframe(
            df,
            time_col=self.time_feature,
            value_cols=df.drop(self.time_feature).columns,
        )
        y = ts_data[self.target]
        X_past, X_future = None, None

        if self.past_features:
            X_past = ts_data[self.past_features]
        if self.future_features:
            X_future = ts_data[self.future_features]
        return y, X_past, X_future
    
    def transform_output(self, ts: TimeSeries):
        if ts:
            output = ts.to_dataframe(backend='polars',time_as_index=False)
        else:
            output = None    
        return output

    def train(self, df):
        train_y, train_X_past, train_X_future = self.transform_input(df)
        self.model.fit(
            series=train_y,
            past_covariates=train_X_past,
            future_covariates=train_X_future,
        )
        self.is_trained = True

    def historical_forecast(self,df,horizon:int):
        y_hat = None
        if self._model_fitted:
            hist_y,hist_X_past,hist_X_future = self.transform_input(df)
            pred_ts = self.model.historical_forecasts(series=hist_y,past_covariates=hist_X_past,future_covariates=hist_X_future,
                                                    forecast_horizon=horizon,stride=1,last_points_only = True,retrain=False)
            y_hat = self.transform_output(pred_ts)
        return y_hat    

    def forecast(self, df, horizon: int):
        y_hat = None
        if self.is_trained:
            predict_y, predict_X_past, pedict_X_future = self.transform_input(df)
            pred_ts = self.model.predict(
                horizon,
                series=predict_y,
                past_covariates=predict_X_past,
                future_covariates=pedict_X_future,
            )
            y_hat = self.transform_output(pred_ts)
        return y_hat


class XGB(BaseModel):
    def __init__(self, *args):
        super().__init__(*args)
        self.algorithm = "XGB"
        self.model = XGBModel(**self.base_params)


class Linear(BaseModel):
    def __init__(self, *args):
        super().__init__(*args)
        self.algorithm = "Linear"
        self.model = LinearRegressionModel(**self.base_params)
