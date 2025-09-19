from csv import reader
from os import walk

import pygame

def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter= ',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map
    
import random

def get_random_position(matrix):
    posiciones_internas = []

    for y in range(1, len(matrix) - 1):
        for x in range(1, len(matrix[y]) - 1):
            if matrix[y][x] == '4':
                posiciones_internas.append((x, y))

    if posiciones_internas:
        posiciones_internas.sort(key=lambda pos: pos[1])
        
        ponderacion = [(x, y) for x, y in posiciones_internas for _ in range(len(matrix) - y)]

        return random.choice(ponderacion)
    else:
        return None


def import_folder(path):
    surface_list = []

    for _,__,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list   