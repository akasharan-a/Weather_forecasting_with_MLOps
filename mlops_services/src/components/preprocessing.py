import os
from pathlib import Path
import polars as pl
from sklearn.model_selection import train_test_split
from mlops_services.src.utils.dataframe import column_count


class TrainTestSet:
    def __init__(self, config, logger, filename):
        self.config = config
        self.logger = logger
        self.df = pl.read_parquet(Path(self.config.folder.raw) / f"{filename}.parquet")

    def create_split(self):
        test_size = self.config.test_split_ratio
        if (test_size != None) & (test_size > 0) & (test_size < 1):
            self.df_train, self.df_test = train_test_split(
                self.df, test_size=test_size, shuffle=False
            )
        else:
            self.df_train, self.df_test = self.df.clone(), self.df.filter(pl.lit(False))

    def save(self):
        folder = Path(self.config.path.raw_data)
        # os.makedirs(processed_folder, exist_ok=True)
        self.df_train.write_parquet(folder / f"train.parquet")
        self.df_test.write_parquet(folder / f"test.parquet")


class PreprocessData:
    def __init__(self, config, logger, filename: str):
        self.config = config
        self.logger = logger
        self.filename = filename
        self.df = pl.read_parquet(
            Path(self.config.path.raw_data) / f"{self.filename}.parquet"
        )
        self.df_orig = self.df.clone()
        self.logger.info(f">>Preprocessing : {self.filename}")

    def select_columns(self):
        self.df = self.df.rename(
            {self.config.features.time.raw: self.config.features.time.std}
        )
        selected_columns = [
            self.config.features.time.std,
            self.config.features.target,
        ] + self.config.features.past_feats
        self.df = self.df.select(selected_columns)
        self.logger.info(f"Columns feteched : {selected_columns}")

    def drop_nans(self):
        subset = self.config.features.past_feats
        count_before = self.df.height
        self.df = self.df.filter(~pl.all_horizontal(pl.col(subset).is_null()))
        count_after = self.df.height
        self.logger.info(
            f"Dropped Nulls -- Count before:{count_before} & Count After:{count_after}"
        )

    def resample(self):
        time_col = self.config.features.time.std
        resample_freq = self.config.data_process.resampling_freq
        count_before = self.df.height
        self.df = (
            self.df.sort(time_col)
            .group_by_dynamic(index_column=time_col, every=resample_freq)
            .agg(pl.all().mean())
            .with_columns(
                # Remove timezone to make datetime naive
                pl.col(time_col)
                .dt.replace_time_zone(None)
                .alias(time_col)
            )
        )
        count_after = self.df.height
        self.logger.info(
            f"Data resampled -- Frequency:{resample_freq} Count before:{count_before} & Count After:{count_after}"
        )

    def impute_features(self):
        count_before = self.df.null_count().to_dict(as_series=False)
        match self.config.data_process.impute_missing:
            case "ffill":
                self.df = self.df.fill_null(strategy="forward")
            case _:
                pass
        count_after = self.df.null_count().to_dict(as_series=False)
        self.logger.info(
            f"Features imputed -- Strategy:{self.config.data_process.impute_missing} \
                        \n Null count before:{count_before} & Null count After:{count_after}"
        )

    def save(self):
        processed_folder = Path(self.config.path.final_data)
        os.makedirs(processed_folder, exist_ok=True)
        file_path = processed_folder / f"{self.filename}.parquet"
        self.df.write_parquet(file_path)
        self.logger.info(f"{self.filename} data saved at {file_path}")
