import logging

from rq import Worker, Connection

from conn import r

listen = ["default"]

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d  - %(message)s')
    with Connection(r):
        logging.debug(listen)
        worker = Worker(listen)
        worker.work()
