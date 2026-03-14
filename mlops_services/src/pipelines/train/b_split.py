from mlops_services.src.components.preprocessing import TrainTestSet
from mlops_services.src.utils import command_line, configs, logs

stage = "02_Data_Split"
logger = logs.setup_logger(stage)


class DataSplit:
    def __init__(self,logger=logger):
        self.logger = logs.validate_logger(logger)
        self.args = self.arguments()
        self.config = configs.Config.from_yaml(
            "mlops_services/config/model_params.yaml"
        )

    def arguments(self):
        parser = command_line.Args(prog="DataSplit")
        return parser.get_args()

    def run(self):
        train_test_set = TrainTestSet(self.config, "complete_set")
        train_test_set.create_split()
        train_test_set.save()


if __name__ == "__main__":
    logger.info(f"{stage} --> Started")
    try:
        DataSplit().run()
        logger.info(f"{stage} --> Completed")

    except Exception as e:
        logger.info(f"{stage} --> Failed")
        raise e
