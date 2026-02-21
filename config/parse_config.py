import json

class Configuration:
    def __init__(self, file_path: str = "config/config.json") -> None:
        # parse config file
        with open(file_path) as config_file:
            parsed_config = json.load(config_file)

        self.map = parsed_config  # whole map
        self.database_tables = parsed_config["database_tables"]  # DB tables
    

default_config = Configuration()


if __name__ == "__main__":
    pass
