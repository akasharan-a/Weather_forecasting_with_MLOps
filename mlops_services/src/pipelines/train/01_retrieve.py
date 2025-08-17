from mlops_services.src.components.data_operations import GetRawData
from mlops_services.src.utils import command_line, load_config

class DataRetrieval:
    def __init__(self):
        self.args = self.arguments()
        self.config = load_config.Config.from_yaml('mlops_services/config/model_train.yaml')
        self.config_weather = load_config.Config.from_yaml('mlops_services/config/weather_data.yaml')
        assert self.args.city in self.config_weather.all_cities
        self.tz = getattr(self.config_weather.co_ordinates,self.args.city).tz
        self.config.city = self.args.city
    
    def arguments(self):
        parser = command_line.Args(prog='DataRetrieval')
        parser.add_argument("source", help="db/local", type=str)
        parser.add_argument("city", help="City", type=str)
        parser.add_argument("start_time", help="Start time", type=str)
        parser.add_argument("end_time", help="End time", type=str)
        return parser.get_args()

    def run(self):
        raw_data_loader = GetRawData(self.config)
        if self.args.source == "db":
            raw_data_loader.load_from_db(self.args.start_time , self.args.end_time, self.tz)
            print("loading historic data from DB")
        else:
            raw_data_loader.load_from_local()
            print("loading data from local")

        raw_data_loader.split_test()
        raw_data_loader.save()

if __name__=="main":
    try:
        DataRetrieval().run()
    except Exception as e:
        raise e
                