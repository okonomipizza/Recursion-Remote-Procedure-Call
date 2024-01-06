import socket
import os
import json
from time import sleep
import math


def main():
    #通信用のsocketを作成
    sock = SocketGenerator()
    Procedure.start(sock.socket)
    pass

#インスタンス作成時にsocketの作成と接続までを実行
class SocketGenerator:
    def __init__(self):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_address = '/tmp/rpc.sock'
        #接続をクリーンな状態で始めるためにアドレスとのリンクを削除
        try:
            os.unlink(self.server_address)
        except FileNotFoundError:
            pass
        print(f"Starting up on {self.server_address}")
        
        #サーバアドレスにソケットを接続
        self.socket.bind(self.server_address)
                

class Procedure:
    @staticmethod
    def get_function(method):
        def floor(x):
            return math.floor(x)
        
        def nroot(n, x):
            return n * math.sqrt(x)
        
        def reverse(string):
            reverse_str = ""
            for i in range(len(string)):
                reverse_str += string[-i-1]
            return reverse_str
        
        def valid_anaglam(s1, s2):
            if len(s1) != len(s2): return False
            s1 = sorted(s1)
            s2 = sorted(s2)
            for i in range(len(s1)):
                if s1[i] != s2[i]: return False
            return True
        
        def sort(string):
            sortedString = sorted(string)
            result = ""
            for i in range(len(sortedString)):
                result += sortedString[i]
            return result
        
        rpc_functions = {
            "floor": floor,
            "nroot": nroot,
            "reverse": reverse,
            "valid_anaglam": valid_anaglam,
            "sort": sort
        }

        return rpc_functions[method]
    
    @staticmethod
    def is_method_valid(method):
        methods = ['floor', 'nroot', 'reverse', 'valid_anaglam', 'sort']
        if method not in methods: return False
        return True
    
    @staticmethod
    def is_param_types_valid(json_data):
        param_types = {
            "floor": ['number'],
            "nroot": ['number', 'number'],
            "reverse": ['string'],
            "valid_anaglam": ['string', 'string'],
            "sort": ['string']
        }

        method = json_data["method"]
        type_list = param_types[method]
        input_type_list = json_data["param_types"]

        if len(type_list) != len(input_type_list): return False

        for i in range(len(type_list)):
            if type_list[i].lower() != input_type_list[i].lower(): return False
        
        return True
    
    @staticmethod
    def generate_json_string(result, result_type, id):
        json_data = {
            "results": result,
            "result_type": result_type,
            "id": id
        }
        return json.dumps(json_data)
    
    @staticmethod
    def generate_response(json_data_str):
        json_data = json.loads(json_data_str)
        method = json_data["method"]

        is_method_valid = Procedure.is_method_valid(method)
        if not is_method_valid:
            err_jason = {
                "ERROR": "invalid methods"
            }
            return json.dumps(err_jason)

        is_params_valid = Procedure.is_param_types_valid(json_data)
        if not is_params_valid:
            err_jason = {
                "ERROR": "invalid params"
            }
            return json.dumps(err_jason)


        func = Procedure.get_function(method)
        request_id = json_data["id"]

        if method == "floor":
            result = func(float(json_data["params"][0]))
            result_type = str(type(result))
            return Procedure.generate_json_string(result, result_type, request_id)
        elif method == "nroot":
            result = func(float(json_data["params"][0]), float(json_data["params"][1]))
            result_type = str(type(result))
            return Procedure.generate_json_string(result, result_type, request_id)
        elif method == "reverse":
            result = func(json_data["params"][0])
            result_type = str(type(result))
            return Procedure.generate_json_string(result, result_type, request_id)
        elif method == "valid_anaglam":
            result = func(json_data["params"][0], json_data["params"][1])
            result_type = str(type(result))
            return Procedure.generate_json_string(result, result_type, request_id)
        elif method == "sort":
            result = func(json_data["params"][0])
            result_type = str(type(result))
            return Procedure.generate_json_string(result, result_type, request_id)
        
        return None

    @staticmethod
    def start(socket):
        socket.listen(1)
        while True:
            connection, client_address = socket.accept()
            try:
                print(f"Connection from {client_address}")
                while True:
                    data = connection.recv(1024)

                    if data:
                        #取得したjsonを解析
                        json_data_str = data.decode('utf-8')
                        print(json_data_str)
                        response = Procedure.generate_response(json_data_str)
                        print(f"Response: {response}")
                        connection.sendall(response.encode())
                        break
                    else:
                        sleep(5)
                        print(f"no data from {connection}")
    
            finally:
                print('Closing current connection')
                connection.close()
    

if __name__ == "__main__":
    main()