import yaml
class Config:
    def __init__(self, data):
        for key, value in data.items():
            # Recursively convert nested dicts into Config objects
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            else:
                setattr(self, key, value)

    def __repr__(self):
        # Helpful string representation
        return f"{self.__class__.__name__}({self.__dict__})"

    @classmethod
    def from_yaml(cls, filepath):
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
        return cls(data)
