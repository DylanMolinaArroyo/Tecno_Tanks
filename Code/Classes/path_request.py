import json

from Code.Functions.A_star import a_star

class PathRequest:

    def solicitar_ruta(self, matriz_ruta, coordenada_enemigo, coordenada_jugador):
        ruta = a_star(coordenada_jugador,coordenada_enemigo, matriz_ruta[0])

        try:
            return ruta
        except json.JSONDecodeError as e:
            print("Error al decodificar la respuesta JSON:", e)
            return None