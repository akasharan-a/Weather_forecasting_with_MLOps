from mlops_services.src.components.data_retrieval import GetRawData
from mlops_services.src.utils import command_line, configs, logs

stage = "01_Data_Retrieval"
logger = logs.setup_logger(stage)

class DataRetrieval:
    def __init__(self,logger=logger):
        self.logger = logs.validate_logger(logger)
        self.args = self.arguments()
        self.config = configs.Config.from_yaml(
            "mlops_services/config/model_params.yaml"
        )
        self.config_weather = configs.Config.from_yaml(
            "mlops_services/config/weather_data.yaml"
        )
        logger.info(f"City : {self.args.city}")
        assert self.args.city in  list(self.config_weather.cities.__dict__.keys())
        self.tz = getattr(self.config_weather.cities, self.args.city).tz

    def arguments(self):
        parser = command_line.Args(prog="DataRetrieval")
        parser.add_argument("source", help="db/local", type=str)
        parser.add_argument("city", help="City", type=str)
        parser.add_argument("start_time", help="Start time", type=str)
        parser.add_argument("end_time", help="End time", type=str)
        return parser.get_args()

    def run(self):
        raw_data_loader = GetRawData(self.config,self.logger,"complete_set")
        if self.args.source == "db":
            self.logger.info("Trying to load historic data from DB")
            raw_data_loader.load_from_db(
                self.args.city, self.args.start_time, self.args.end_time, self.tz
            )
        else:
            logger.info("Trying to load historic data from local")
            raw_data_loader.load_from_local(self.args.city)
        raw_data_loader.save()


if __name__ == "__main__":
    logger.info(f"{stage} --> Started")
    try:
        DataRetrieval().run()
        logger.info(f"{stage} --> Completed")
    except Exception as e:
        logger.info(f"{stage} --> Failed")
        raise e
