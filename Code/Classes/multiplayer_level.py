import pygame
from Code.Classes.level import Level
from Code.Entities.player import Player
from Code.Entities.enemy import Enemy
from Code.Entities.powerUp import PowerUp
from Code.Utilities.settings import *

class MultiplayerLevel:
    def __init__(self, difficulty_config, network_client, player_number):
        print(f"🎮 DEBUG MultiplayerLevel: Iniciando - Jugador {player_number}")
        
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
            
            print("🎮 DEBUG: Level base y jugadores creados")
        except Exception as e:
            print(f"❌ ERROR creando Level: {e}")
            self.level = None

        self.setup_network_handlers()
        print(f"🎮 DEBUG MultiplayerLevel: Inicialización completada")

    def setup_network_handlers(self):
        def handle_player_action(message):
            if self.player_number == 1 and self.remote_player:
                player_id = message.get('player')
                if player_id == 2:
                    action_data = message.get('action_data', {})
                    direction = action_data.get('direction')
                    if direction is not None:
                        self.remote_player.direction = pygame.math.Vector2(direction)
                        
                        # --- CAMBIO #1: ACTUALIZAR EL STATUS PARA LA ANIMACIÓN ---
                        # Se actualiza el estado visual del tanque remoto basado en su dirección.
                        # Esto hará que la animación de movimiento se active en la pantalla del anfitrión.
                        if self.remote_player.direction.magnitude() != 0:
                            if abs(self.remote_player.direction.y) > abs(self.remote_player.direction.x):
                                self.remote_player.status = 'up' if self.remote_player.direction.y < 0 else 'down'
                            else:
                                self.remote_player.status = 'left' if self.remote_player.direction.x < 0 else 'right'
                        else:
                            if 'idle' not in self.remote_player.status:
                                self.remote_player.status += '_idle'

                    if action_data.get('attack'):
                        self.remote_player.attacking = True
                        self.remote_player.attack_time = pygame.time.get_ticks()
                        self.level.create_bullet(self.remote_player, self.remote_player.bullet_speed)
                        self.remote_player.sounds['attack_sound'].play()
                        
        self.network_client.register_handler('player_action', handle_player_action)

    def run(self):
        if not self.level: return 'error'

        if self.player_number == 1: # Lógica del Anfitrión
            self.level.run()
            game_state = self.create_game_state_snapshot()
            self.network_client.send_game_state(game_state)
        else: # Lógica del Invitado
            self.local_player.input() # Leer mi input
            action_data = {'direction': [self.local_player.direction.x, self.local_player.direction.y]}
            if self.local_player.attacking and (pygame.time.get_ticks() - self.local_player.attack_time < 20):
                action_data['attack'] = True
            self.network_client.send_player_action('input', action_data)

            # --- CAMBIO #2: ACTUALIZAR TODOS LOS SPRITES ---
            # Se llama al update de TODO el grupo, no solo del jugador local.
            # Esto ejecutará la lógica de animación y movimiento para los enemigos,
            # power-ups y el tanque amigo en la pantalla del invitado.
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
        state = {'entities': {}}
        for sprite in list(self.level.visible_sprites):
            if not hasattr(sprite, 'sprite_type'): continue

            if not hasattr(sprite, 'network_id'):
                sprite.network_id = self.get_new_network_id()
                self.network_entities[sprite.network_id] = sprite
            
            entity_data = {
                'pos': sprite.rect.center,
                'health': getattr(sprite, 'health', None),
                'status': getattr(sprite, 'status', None),
                'type': sprite.sprite_type
            }
            if sprite.sprite_type == 'enemy':
                entity_data['name'] = sprite.name
            elif hasattr(sprite, 'power_type'):
                 entity_data['power_type'] = sprite.power_type

            state['entities'][sprite.network_id] = entity_data
        return state

    def apply_game_state(self, state):
        if self.player_number != 2 or not self.level: return
        received_ids = set(state['entities'].keys())
        
        for net_id, data in state['entities'].items():
            if net_id in self.network_entities:
                sprite = self.network_entities[net_id]
                sprite.rect.center = data['pos']
                if data['health'] is not None and hasattr(sprite, 'health'): sprite.health = data['health']
                if data['status'] is not None and hasattr(sprite, 'status'): sprite.status = data['status']
            else:
                sprite_type = data.get('type')
                if sprite_type == 'enemy':
                    new_enemy = Enemy(data['name'], data['pos'], [self.level.visible_sprites, self.level.attackble_sprites],
                                      self.level.obstacle_sprites, self.level.create_bullet, self.local_player,
                                      self.level.structure, self.level.matrix_route, self.level.path_request)
                    new_enemy.network_id = net_id
                    self.network_entities[net_id] = new_enemy
                elif sprite_type in power_up_data or sprite_type in bonus_data:
                    power_type = data['power_type']
                    data_source = power_up_data.get(power_type) or bonus_data.get(power_type)
                    new_powerup = PowerUp(power_type, data['pos'], [self.level.visible_sprites, self.level.power_up_sprites], data_source)
                    new_powerup.network_id = net_id
                    self.network_entities[net_id] = new_powerup

        for net_id, sprite in list(self.network_entities.items()):
            if net_id not in received_ids:
                sprite.kill()
                del self.network_entities[net_id]