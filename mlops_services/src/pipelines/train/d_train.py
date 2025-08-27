from mlops_services.src.components.forecasting_models import XGB
from mlops_services.src.utils import command_line, configs, logs

stage = "04_Model_Training"
logger = logs.setup_logger(stage)


class ModelTraining:
    def __init__(self,logger=logger):
        self.logger = logs.validate_logger(logger)
        self.args = self.arguments()
        self.config = configs.Config.from_yaml(
            "mlops_services/config/model_params.yaml"
        )
        assert self.args.algo in self.config.algorithms.__dict__.keys()


    def arguments(self):
        parser = command_line.Args(prog="ModelTraining")
        parser.add_argument("algo", help="Forecasting Algorithm", type=str)
        return parser.get_args()

    def run(self):
        pass

if __name__ == "__main__":
    logger.info(f"{stage} --> Started")
    try:
        ModelTraining().run()
        logger.info(f"{stage} --> Completed")

    except Exception as e:
        logger.info(f"{stage} --> Failed")
        raise e
