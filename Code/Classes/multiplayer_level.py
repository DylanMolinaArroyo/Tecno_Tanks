import pygame
from Code.Classes.level import Level
from Code.Entities.player import Player
from Code.Entities.enemy import Enemy
from Code.Entities.powerUp import PowerUp
from Code.Utilities.settings import *
from Code.Entities.bullet import Bullet
from Code.Entities.Explosion import Explosion

class MultiplayerLevel:
    def __init__(self, difficulty_config, network_client, player_number):
        print(f"DEBUG MultiplayerLevel: Iniciando - Jugador {player_number}")
        
        self.difficulty_config = difficulty_config
        self.network_client = network_client
        self.player_number = player_number
        self.display_surface = pygame.display.get_surface()

        try:
            self.level = Level(difficulty_config)
            self.network_entities = {}
            self.next_network_id = 0
            host_spawn_pos = (2020, 2700)
            guest_spawn_pos = (2120, 2700)

            if self.player_number == 1: # Soy Anfitrión
                self.local_player = self.level.player
                self.local_player.is_local = True
                self.remote_player = Player(guest_spawn_pos, [self.level.visible_sprites, self.level.attackble_sprites], 
                                            self.level.obstacle_sprites, self.level.create_bullet, is_local=False)
            else: # Soy Invitado
                self.remote_player = self.level.player
                self.remote_player.is_local = False
                self.remote_player.rect.topleft = host_spawn_pos
                self.local_player = Player(guest_spawn_pos, [self.level.visible_sprites, self.level.attackble_sprites], 
                                           self.level.obstacle_sprites, self.level.create_bullet, is_local=True)
                self.level.player = self.local_player

            self.local_player.network_id = self.player_number
            self.remote_player.network_id = 1 if self.player_number == 2 else 2
            self.network_entities[self.local_player.network_id] = self.local_player
            self.network_entities[self.remote_player.network_id] = self.remote_player
            
            print("DEBUG: Level base y jugadores creados")
        except Exception as e:
            print(f"ERROR creando Level: {e}")
            self.level = None

        self.setup_network_handlers()
        print(f"DEBUG MultiplayerLevel: Inicialización completada")

    def setup_network_handlers(self):
    
        def handle_player_action(message):
            # Esta función solo la usa el ANFITRIÓN para procesar las acciones del INVITADO
            if self.player_number == 1 and self.remote_player:
                player_id = message.get('player')
                
                if player_id == 2:
                    action_data = message.get('action_data', {})
                    
                    direction_data = action_data.get('direction')
                    if direction_data is not None:
                        # Paso 1: Actualizamos la dirección de movimiento
                        self.remote_player.direction = pygame.math.Vector2(direction_data)

                        # Paso 2: ACTUALIZAMOS LA ANIMACIÓN (EL STATUS)
                        # Esta es la parte clave que hace que el tanque se vea en movimiento.
                        if self.remote_player.direction.magnitude() == 0:
                            if 'idle' not in self.remote_player.status:
                                self.remote_player.status += '_idle'
                        else:
                            if abs(self.remote_player.direction.y) > abs(self.remote_player.direction.x):
                                self.remote_player.status = 'up' if self.remote_player.direction.y < 0 else 'down'
                            else:
                                self.remote_player.status = 'left' if self.remote_player.direction.x < 0 else 'right'

                    # Gestionar ataque del jugador remoto
                    if action_data.get('attack') and not self.remote_player.attacking:
                        self.remote_player.attacking = True
                        self.remote_player.attack_time = pygame.time.get_ticks()
                        self.level.create_bullet(self.remote_player, self.remote_player.bullet_speed)
                        self.remote_player.sounds['attack_sound'].play()
                        
        self.network_client.register_handler('player_action', handle_player_action)
        
    def run(self):
        if not self.level: return 'error'

        if self.player_number == 1: 
            
            self.level.run() 
            
            game_state = self.create_game_state_snapshot()
            
            self.network_client.send_game_state(game_state)

        else: 
            
            self.local_player.input() 
            
            
            action_data = {
                'direction': [self.local_player.direction.x, self.local_player.direction.y],
                'attack': self.local_player.attacking 
            }
            self.network_client.send_player_action('input', action_data)
            
            self.level.visible_sprites.update()
            
            self.level.visible_sprites.custom_draw(self.local_player)
            self.level.ui.display(self.local_player, self.difficulty_config["name"], self.level.total_rounds, self.level.current_round)
        
        if self.local_player.health <= 0 or self.level.structure.destroyed: return 'lose'
        if self.level.all_enemies_defeated() and not self.level.enemy_queue: return 'win'
        return 'playing'

    def get_new_network_id(self):
        self.next_network_id += 1
        return f"ent_{self.next_network_id}"
    
    def create_game_state_snapshot(self):
        """
        Crea una "foto" instantánea del estado actual de todos los elementos importantes del juego.
        Esta función la ejecuta únicamente el ANFITRIÓN.
        """
        if not self.level: return {'entities': {}}

        state = {
            'entities': {},
            'destroyed_tiles': self.level.destroyed_tiles_since_last_snapshot
        }
        
        for sprite in list(self.level.visible_sprites):
            if not hasattr(sprite, 'sprite_type'): 
                continue

            if not hasattr(sprite, 'network_id'):
                sprite.network_id = self.get_new_network_id()
                self.network_entities[sprite.network_id] = sprite
            
            entity_data = {
                'type': sprite.sprite_type,
                'pos': sprite.rect.center,
            }

            sprite_type = sprite.sprite_type
            if sprite_type == 'player' or sprite_type == 'enemy':
                entity_data['health'] = getattr(sprite, 'health', None)
                entity_data['status'] = getattr(sprite, 'status', None)
                if sprite_type == 'enemy':
                    entity_data['name'] = sprite.name
            
            elif sprite_type == 'powerup' or sprite_type == "bonus":
                entity_data['power_type'] = sprite.power_type

            elif sprite_type == 'bullet':
                pass
            
            elif sprite_type == 'explosion':
                pass
            
            elif sprite_type in ['grass', 'walls', 'rocks', 'barrier', 'fortress']:
                if sprite_type == 'fortress':
                    entity_data['health'] = getattr(sprite, 'health', None)
                else:
                    continue

            state['entities'][sprite.network_id] = entity_data
            
        self.level.destroyed_tiles_since_last_snapshot = []
        
        return state

    def apply_game_state(self, state):
        """
        Aplica el estado del juego recibido del anfitrión.
        Esta función la ejecuta únicamente el INVITADO para actualizar su mundo.
        """
        if self.player_number != 2 or not self.level or not state: 
            return

        received_ids = set(state['entities'].keys())
        
        for net_id, data in state['entities'].items():
            if net_id in self.network_entities:
                sprite = self.network_entities[net_id]
                
                current_pos = pygame.math.Vector2(sprite.rect.center)
                target_pos = pygame.math.Vector2(data['pos'])
                sprite.rect.center = current_pos.lerp(target_pos, 0.25) 

                if 'health' in data and hasattr(sprite, 'health'):
                    sprite.health = data['health']
                if 'status' in data and hasattr(sprite, 'status'):
                    if sprite is not self.local_player:
                        sprite.status = data['status']
            else:
                sprite_type = data.get('type')
                pos = data.get('pos')
                
                new_sprite = None
                if sprite_type == 'enemy':
                    new_sprite = Enemy(data['name'], pos, [self.level.visible_sprites, self.level.attackble_sprites],
                                      self.level.obstacle_sprites, self.level.create_bullet, 
                                      self.remote_player, 
                                      self.level.structure, self.level.matrix_route, self.level.path_request)
                
                elif sprite_type == 'powerup' or sprite_type == 'bonus':
                    power_type = data['power_type']
                    data_source = power_up_data.get(power_type) or bonus_data.get(power_type)
                    if data_source:
                        new_sprite = PowerUp(power_type, pos, [self.level.visible_sprites, self.level.power_up_sprites], data_source)

                elif sprite_type == 'bullet':
                    bullet = pygame.sprite.Sprite() 
                    bullet.image = pygame.image.load('Assets/Entities/Bullet/bullet.png').convert_alpha()
                    bullet.image = pygame.transform.scale(bullet.image, (25, 25))
                    bullet.rect = bullet.image.get_rect(center=pos)
                    bullet.sprite_type = 'bullet' 
                    self.level.visible_sprites.add(bullet)
                    new_sprite = bullet

                elif sprite_type == 'explosion':
                    new_sprite = Explosion(pos, [self.level.visible_sprites])

                if new_sprite:
                    new_sprite.network_id = net_id
                    self.network_entities[net_id] = new_sprite

        for net_id, sprite in list(self.network_entities.items()):
            if net_id not in received_ids:
                if sprite is not self.local_player and sprite is not self.remote_player:
                    sprite.kill()
                    del self.network_entities[net_id]

        if 'destroyed_tiles' in state:
            for row, col in state['destroyed_tiles']:
                if (row, col) in self.level.tile_map:
                    tile_to_destroy = self.level.tile_map[(row, col)]
                    tile_to_destroy.kill()
                    del self.level.tile_map[(row, col)]