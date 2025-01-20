import logging

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = logging.getLogger('Task1Logger')
            cls._instance.setLevel(logging.INFO)

            handler = logging.FileHandler('export/execution.log')
            handler.setLevel(logging.INFO)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            cls._instance.addHandler(handler)
        return cls._instance

logger = Logger()

