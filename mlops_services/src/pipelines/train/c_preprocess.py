from mlops_services.src.components.preprocessing import PreprocessData
from mlops_services.src.utils import command_line, configs, logs

stage="03_Data_Preprocessing"
logger = logs.setup_logger(stage)

class DataPreprocessing:
    def __init__(self,logger=logger):
        self.logger = logs.validate_logger(logger)
        self.args = self.arguments()
        self.config = configs.Config.from_yaml(
            "mlops_services/config/model_params.yaml"
        )

    def arguments(self):
        return None

    def run(self):
        ##Training set
        train_data = PreprocessData(self.config,self.logger,"train")
        train_data.select_columns()
        train_data.drop_nans()
        train_data.resample()
        train_data.impute_features()
        train_data.save()
        ##Test set
        test_data = PreprocessData(self.config,self.logger,"test")
        test_data.select_columns()
        test_data.drop_nans()
        test_data.resample()
        test_data.impute_features()
        test_data.save()


if __name__ == "__main__":
    try:
        DataPreprocessing().run()
    except Exception as e:
        logger.info(f"{stage} --> Failed")
        raise e
