from csv import reader
import os
from os import walk
import pygame
import random
from Code.Utilities.settings import tanks_data

ASSET_CACHE = {}

def load_all_assets():
    """Carga todas las animaciones del juego una sola vez al inicio."""
    print("Cargando todos los assets...")
    
    player_path = 'Assets/Entities/Player/'
    ASSET_CACHE['player'] = {}
    for animation in ['up', 'down', 'left', 'right', 'up_idle', 'down_idle', 'left_idle', 'right_idle']:
        ASSET_CACHE['player'][animation] = import_folder(player_path + animation)

    # Cargar animaciones de los enemigos 
    for enemy_name in tanks_data.keys():
        enemy_path = f'Assets/Entities/Enemies/{enemy_name}/'
        ASSET_CACHE[enemy_name] = {}
        for animation in ['up', 'down', 'left', 'right', 'up_idle', 'down_idle', 'left_idle', 'right_idle', 'attack']:
            full_path = enemy_path + animation
            ASSET_CACHE[enemy_name][animation] = import_folder(full_path)
            
    explosion_path = "Assets/Effects/Circle_explosion"
    ASSET_CACHE['explosion'] = []
    for filename in sorted(os.listdir(explosion_path)):
        if filename.endswith(".png"):
            full_path = os.path.join(explosion_path, filename)
            img = pygame.image.load(full_path).convert_alpha()
            img = pygame.transform.scale(img, (180, 180))
            ASSET_CACHE['explosion'].append(img)

    print("Assets cargados exitosamente.")


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