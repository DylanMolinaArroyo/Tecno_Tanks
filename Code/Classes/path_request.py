import json

from Code.Functions.A_star import a_star
from Code.Functions.support import import_csv_layout

class PathRequest:
    def __init__(self, csv_path='Assets/Map_matrix/EscenarioJuego._Obstaculos.csv'):
        self.matrix = self.load_matrix(csv_path)

    def load_matrix(self, csv_path):
        matrix = import_csv_layout(csv_path)
        return matrix

    def solicitar_ruta(self, coordenada_enemigo, coordenada_jugador):

        ruta = a_star(coordenada_jugador,coordenada_enemigo, self.matrix)

        try:
            return ruta
        except json.JSONDecodeError as e:
            print("Error al decodificar la respuesta JSON:", e)
            return None