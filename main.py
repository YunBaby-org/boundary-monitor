from src.models.BoundaryModel import Boundary
from src.app import Application
import logging
import sys 




if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Boundary Monitor Start")
    app = Application()
    app.start()