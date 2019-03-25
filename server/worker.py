import logging

import time
import zmq


def server():
    """
    Simple receiver of feeds
    :return: list
    """
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    logging.debug("Listening at *:5555.Waiting for feeds")
    while True:
        message = socket.recv()
        logging.debug(f"Received request: {message}")
        time.sleep(1)
        socket.send(b"World")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
    server()
