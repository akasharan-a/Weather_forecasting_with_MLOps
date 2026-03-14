from mlops_services.src.components.model_evaluation import Evaluator
from mlops_services.src.utils import command_line, configs, logs

stage = "05_Model_Evaluation"
logger = logs.setup_logger(stage)


class ModelEvaluation:
    def __init__(self, logger=logger):
        self.logger = logger
        self.args = self.arguments()
        self.config = configs.Config.from_yaml(
            "mlops_services/config/model_params.yaml"
        )

    def arguments(self):
        parser = command_line.Args(prog="ModelEvalution")
        parser.add_argument("source", help="Source for the model", type=str)
        return parser.get_args()

    def run(self):
        model_evaluate = Evaluator(self.config, logger, "train")
        model_evaluate.load_model(self.args.source)
        model_evaluate.log_experiment()
        model_evaluate.save()


if __name__ == "__main__":
    logger.info(f"{stage} --> Started")
    try:
        ModelEvaluation().run()
        logger.info(f"{stage} --> Completed")

    except Exception as e:
        logger.info(f"{stage} --> Failed")
        raise e
