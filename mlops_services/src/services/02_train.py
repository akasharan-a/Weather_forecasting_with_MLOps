import mlflow
import subprocess


class TrainModel():
    def __init__(self):
        pass
    def execute(self):
        with mlflow.start_run() as run:
            run_id = run.info.run_id
            # Pass run_id to other scripts via CLI or environment variable
            subprocess.run(["dvc", "preprocess.py", "--run_id", run_id])

