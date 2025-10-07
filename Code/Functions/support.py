from csv import reader
from os import walk

import pygame
import random

def import_csv_layout(path):
    """
    Loads a CSV file and returns a 2D list representing the terrain map.

    Args:
        path (str): Path to the CSV file.

    Returns:
        list: 2D list of terrain map values.
    """

    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter= ',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map
    

def get_random_position(matrix, index: str ):
    """
    Returns a random internal position from the matrix where the cell matches the given index.
    Positions closer to the top are more likely to be chosen.

    Args:
        matrix (list): 2D map matrix.
        index (str): Value to match in the matrix.

    Returns:
        tuple or None: (x, y) position or None if no match found.
    """

    posiciones_internas = []

    for y in range(1, len(matrix) - 1):
        for x in range(1, len(matrix[y]) - 1):
            if matrix[y][x] == index:
                posiciones_internas.append((x, y))

    if posiciones_internas:
        posiciones_internas.sort(key=lambda pos: pos[1])
        
        ponderacion = [(x, y) for x, y in posiciones_internas for _ in range(len(matrix) - y)]

        return random.choice(ponderacion)
    else:
        return None


def import_folder(path):
    """
    Loads all images from a folder and returns them as a list of pygame surfaces.

    Args:
        path (str): Path to the folder containing images.

    Returns:
        list: List of loaded pygame.Surface objects.
    """
    
    surface_list = []

    for _,__,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list   