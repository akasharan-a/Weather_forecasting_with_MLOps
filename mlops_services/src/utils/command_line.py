import argparse
class Args(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def get_args(self):
        return self.parse_args()   

