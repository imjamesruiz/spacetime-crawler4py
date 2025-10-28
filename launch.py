from argparse import ArgumentParser
from configparser import ConfigParser

from utils.config import Config
from utils.frontier import Frontier
from utils.worker import Worker

import sys
sys.path.append("/home/ics-home/.local/lib/python3.12/site-packages")

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)

    frontier = Frontier(config, restart)
    worker = Worker(0, config, frontier)
    worker.start()
    worker.join()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
