import os
import time
from signal import signal, SIGINT
from sys import exit
import pymongo
import sys
import docker
from monitoring.new_monitoring import EASEMonitoring
from analysis.new_analysis import EASEAnalysis
from analysis.docker_threshold_analysis import ThresholdAnalysis
from planning.new_planning import OptimizationPlanning
from mape.planning.threshold_planning import DockerPlanning
from execution.new_execution import DockerExecution
from dotenv import load_dotenv

load_dotenv()


# from execution.docker_execution import DockerExecution
# from planning.threshold_planning import DockerPlanning


def handler(signal_received, frame):
    exit(0)


def main():
    signal(SIGINT, handler)
    URI = os.getenv("URI")
    mongo_client = pymongo.MongoClient(URI)
    monitoring = EASEMonitoring(mongo_client, docker.from_env())
    optimization_analysis = EASEAnalysis(mongo_client, monitoring)
    threshold_analysis = ThresholdAnalysis(mongo_client,80,20) 
    optimization_planning = OptimizationPlanning(optimization_analysis, mongo_client)
    docker_planning = DockerPlanning(threshold_analysis)

    execution = DockerExecution(docker_planning,optimization_planning)
    
    optimization_analysis.attach(optimization_planning)
    threshold_analysis.attach(docker_planning)
    docker_planning.attach(execution)
    optimization_planning.attach(execution)

    while True:
        monitoring.get_measurements()
        threshold_analysis.update()
        optimization_analysis.update()
        time.sleep(EASEMonitoring.interval)


if __name__ == "__main__":
    main()
