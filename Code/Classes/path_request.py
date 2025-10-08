import json

from Code.Functions.A_star import a_star

class PathRequest:
    """
    Handles pathfinding requests using the A* algorithm.
    """
    def solicitar_ruta(self, matriz_ruta, coordenada_enemigo, coordenada_jugador):
        """
        Requests a path from the enemy to the player using the A* algorithm.

        Args:
            matriz_ruta (list): Matrix representing the map for pathfinding.
            coordenada_enemigo (tuple): (x, y) grid position of the enemy.
            coordenada_jugador (tuple): (x, y) grid position of the player.

        Returns:
            list: The calculated path as a list of coordinates, or None if an error occurs.
        """
    
        ruta = a_star(coordenada_jugador,coordenada_enemigo, matriz_ruta[0])

        try:
            return ruta
        except json.JSONDecodeError as e:
            print("Error al decodificar la respuesta JSON:", e)
            return None