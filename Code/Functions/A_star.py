import heapq

def get_adjacent_coords(x, y):
    """
    Returns the coordinates of adjacent cells (up, down, left, right).

    Args:
        x (int): X coordinate.
        y (int): Y coordinate.

    Returns:
        list: List of adjacent (x, y) tuples.
    """

    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

def manhattan_distance(a, b):
    """
    Calculates the Manhattan distance between two points.

    Args:
        a (tuple): First coordinate (x1, y1).
        b (tuple): Second coordinate (x2, y2).

    Returns:
        int: Manhattan distance.
    """

    (x1, y1), (x2, y2) = a, b
    return abs(x1 - x2) + abs(y1 - y2)

def is_walkable(matrix, x, y):
    """
    Checks if a cell in the matrix is walkable/transitable.

    Args:
        matrix (list): 2D map matrix.
        x (int): X coordinate.
        y (int): Y coordinate.

    Returns:
        bool: True if cell is transitable, False otherwise.
    """
    
    if y < 0 or y >= len(matrix) or x < 0 or x >= len(matrix[0]):
        return False
    return matrix[y][x] in ('-1')

def reconstruct_path(came_from, current):
    """
    Reconstructs the path from the start to the current node.

    Args:
        came_from (dict): Map of node predecessors.
        current (tuple): Current node.

    Returns:
        list: List of coordinates representing the path.
    """

    ruta = [current]
    while current in came_from:
        current = came_from[current]
        ruta.append(current)
    ruta.reverse()
    return ruta

def a_star(jugador, enemigo, matrix):
    """
    Pure A* algorithm. Returns the path as a list of coordinates or None if no path exists.

    Args:
        jugador (tuple): Start position (usually player).
        enemigo (tuple): Goal position (usually enemy).
        matrix (list): 2D map matrix.

    Returns:
        list or None: List of coordinates for the path, or None if no path found.
    """
    
    jugador = tuple(jugador)
    enemigo = tuple(enemigo)

    open_set = [(manhattan_distance(jugador, enemigo), jugador)]
    came_from = {}
    g_score = {jugador: 0}
    f_score = {jugador: manhattan_distance(jugador, enemigo)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == enemigo:
            return reconstruct_path(came_from, current)

        for vecino in get_adjacent_coords(*current):
            x, y = vecino
            if not is_walkable(matrix, x, y):
                continue

            tentative_g = g_score.get(current, float("inf")) + 1
            if tentative_g < g_score.get(vecino, float("inf")):
                came_from[vecino] = current
                g_score[vecino] = tentative_g
                f_score[vecino] = tentative_g + manhattan_distance(vecino, enemigo)
                heapq.heappush(open_set, (f_score[vecino], vecino))

    return None