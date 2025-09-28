import heapq

def adjacent_coords(x, y):
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

def manhattan_distance(a, b):
    (x1, y1), (x2, y2) = a, b
    return abs(x1 - x2) + abs(y1 - y2)

def es_transitable(matrix, x, y):
    """Chequea si una celda es transitable."""
    if y < 0 or y >= len(matrix) or x < 0 or x >= len(matrix[0]):
        return False
    return matrix[y][x] in ("-1")

def reconstruir_ruta(came_from, current):
    ruta = [current]
    while current in came_from:
        current = came_from[current]
        ruta.append(current)
    ruta.reverse()
    return ruta

def a_star(jugador, enemigo, matrix):
    """Algoritmo A* puro. Retorna la ruta como lista de coordenadas o None si no hay ruta."""

    jugador = tuple(jugador)
    enemigo = tuple(enemigo)

    open_set = [(manhattan_distance(jugador, enemigo), jugador)]
    came_from = {}
    g_score = {jugador: 0}
    f_score = {jugador: manhattan_distance(jugador, enemigo)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == enemigo:
            return reconstruir_ruta(came_from, current)

        for vecino in adjacent_coords(*current):
            x, y = vecino
            if not es_transitable(matrix, x, y):
                continue

            tentative_g = g_score.get(current, float("inf")) + 1
            if tentative_g < g_score.get(vecino, float("inf")):
                came_from[vecino] = current
                g_score[vecino] = tentative_g
                f_score[vecino] = tentative_g + manhattan_distance(vecino, enemigo)
                heapq.heappush(open_set, (f_score[vecino], vecino))

    return None