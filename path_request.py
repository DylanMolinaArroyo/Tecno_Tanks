import socket
import json
import time
from support import import_csv_layout

class PathRequest:
    def __init__(self, host='localhost', port=3000, csv_path='map/EscenarioJuego._Obstaculos.csv'):
        self.host = host
        self.port = port
        self.matrix = self.load_matrix(csv_path)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Intentando conectar al servidor en {self.host}:{self.port}...")
        self.s.connect((self.host, self.port))
        print("Conexión establecida con el servidor Haskell.")

    def load_matrix(self, csv_path):
        matrix = import_csv_layout(csv_path)
        return matrix

    def solicitar_ruta(self, coordenada_enemigo, coordenada_jugador):
        data_to_send = {
            'coordenadaEnemigo': coordenada_jugador,
            'coordenadaJugador':  coordenada_enemigo,
            'matrix': self.matrix
        }

        data_str = json.dumps(data_to_send) + "\n"
        self.s.sendall(data_str.encode())
        print("Datos enviados al servidor.")

        # Receive response
        data = self.s.recv(1024).decode()

        try:
            ruta = json.loads(data)
            return ruta
        except json.JSONDecodeError as e:
            print("Error al decodificar la respuesta JSON:", e)
            return None

    def close_connection(self):
        self.s.close()
        print("Conexión cerrada con el servidor.")
