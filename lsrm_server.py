import json
import logging
import socket
import threading
import typing as tp

from abstract_mca import IMCA


def get_common_response(command_name: str) -> tp.Dict[str, tp.Any]:
    return {
        "command": command_name,
        "result": True,
        "data": {},
    }


def get_error_response(command_name: str) -> tp.Dict[str, tp.Any]:
    return {
        "command": command_name,
        "result": False,
    }


def make_response(response: tp.Dict[str, tp.Any]) -> str:
    return json.dumps(response) + '\r\n'


class ServerThread(threading.Thread):
    """Lsrm tcp-server"""
    def __init__(self, mca_dict: tp.Dict[str, IMCA], port: int = 23) -> None:
        super().__init__()
        self._mca_dict = mca_dict
        self.port = port
        self._stop = False

    def run(self):
        """run lsrm server: ready to accept connection"""
        hostname = 'localhost'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((hostname, self.port))
            sock.listen(socket.SOMAXCONN)
            logging.info("ready to accept connections")
            while not self._stop:
                con, addr = sock.accept()
                with con:
                    logging.info(f"input connection from address: {addr}")
                    while True:
                        data = con.recv(1024)
                        if not data or self._stop:
                            break
                        logging.info(f"data: {data}")
                        response = self.parse_request(data.decode())
                        logging.info(f"response: {response}")
                        con.send(response.encode(encoding="utf-8"))
                logging.info("disconnected")

    def parse_request(self, data: str) -> str:
        """parse input request"""
        request = json.loads(data)
        command_name = request["command"]
        logging.debug(f"command: {command_name}")
        if command_name == "getmcalist":
            return self.get_mca_list()
        elif command_name == "getmcacommonparams":
            return self.get_mca_common_params(request["arguments"])
        elif command_name == "getmcastatus":
            return self.get_mca_status(request["arguments"])
        elif command_name == "getmcaspectrum":
            return self.get_mca_spectrum(request["arguments"])
        elif command_name == "setmcastart":
            return self.set_mca_start(request["arguments"])
        elif command_name == "setmcastop":
            return self.set_mca_stop(request["arguments"])
        elif command_name == "setmcaclear":
            return self.set_mca_clear(request["arguments"])
        return make_response(get_error_response(command_name))

    def get_mca_list(self) -> str:
        response = get_common_response("getmcalist")
        response["data"] = {
            "McaList": list(self._mca_dict.keys())
        }
        return make_response(response)

    def get_mca_common_params(self, request_args: tp.Dict[str, tp.Any]) -> str:
        mca_name = request_args["McaId"]
        mca = self._mca_dict.get(mca_name)
        if not mca:
            return make_response(get_error_response("getmcastatus"))
        response = get_common_response("getmcacommonparams")
        response["data"] = {
            "Manufacturer": "Lsrm",
            "Channels": mca.get_channels(),
            "Lld": 0,
            "Uld": mca.get_channels()-1,
        }
        return make_response(response)

    def get_mca_status(self, request_args: tp.Dict[str, tp.Any]) -> str:
        mca_name = request_args["McaId"]
        mca = self._mca_dict.get(mca_name)
        if not mca:
            return make_response(get_error_response("getmcastatus"))
        response = get_common_response("getmcastatus")
        response["data"] = {
            "InRun": mca.is_running(),
        }
        return make_response(response)

    def get_mca_spectrum(self, request_args: tp.Dict[str, tp.Any]) -> str:
        mca_name = request_args["McaId"]
        mca = self._mca_dict.get(mca_name)
        if not mca:
            return make_response(get_error_response("getmcaspectrum"))
        response = get_common_response("getmcaspectrum")
        spectrum = mca.get_data()
        response["data"] = {
            "LiveTime": spectrum.info.tlive,
            "RealTime": spectrum.info.treal,
            "DataSize": len(spectrum.data),
            "Data": spectrum.data.tolist(),
        }
        return make_response(response)

    def set_mca_start(self, request_args: tp.Dict[str, tp.Any]) -> str:
        mca_name = request_args["McaId"]
        mca = self._mca_dict.get(mca_name)
        if not mca:
            return make_response(get_error_response("setmcastart"))
        mca.start()
        response = get_common_response("setmcastart")
        return make_response(response)

    def set_mca_stop(self, request_args: tp.Dict[str, tp.Any]) -> str:
        mca_name = request_args["McaId"]
        mca = self._mca_dict.get(mca_name)
        if not mca:
            return make_response(get_error_response("setmcastop"))
        mca.stop()
        response = get_common_response("setmcastop")
        return make_response(response)

    def set_mca_clear(self, request_args: tp.Dict[str, tp.Any]) -> str:
        mca_name = request_args["McaId"]
        mca = self._mca_dict.get(mca_name)
        if not mca:
            return make_response(get_error_response("setmcaclear"))
        mca.clear()
        response = get_common_response("setmcaclear")
        return make_response(response)
