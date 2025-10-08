import socket
import pickle
import threading
from typing import Callable, Any

class NetworkClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.game_id = None
        self.player_number = None
        self.message_handlers = {}
        self.receive_thread = None
        self.username = "Player"  # Añadir nombre de jugador
        
    def connect(self, host='0.0.0.0', port=5555, username="Player"):
        try:
            self.username = username
            
            # Crear nuevo socket si no existe o está cerrado
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                    
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((host, port))
            self.connected = True
            
            # Iniciar hilo para recibir mensajes
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            print(f"Conectado al servidor {host}:{port} como {username}")
            return True
            
        except socket.timeout:
            print("Timeout: No se pudo conectar al servidor")
            return False
        except ConnectionRefusedError:
            print("Error: Servidor no disponible")
            return False
        except Exception as e:
            print(f"Error conectando al servidor: {e}")
            return False
    
    def create_game(self, username="Player"):
        if self.connected:
            self.send_message({
                'command': 'create_game', 
                'username': username
            })
        else:
            print("No conectado al servidor")
    
    def join_game(self, game_id, username="Player"):
        if self.connected:
            self.game_id = game_id
            self.send_message({
                'command': 'join_game', 
                'game_id': game_id, 
                'username': username
            })
        else:
            print("No conectado al servidor")
    
    def send_player_ready(self):
        if self.connected and self.game_id:
            self.send_message({
                'command': 'player_ready',
                'game_id': self.game_id
            })
    
    def send_game_state(self, game_state):
        if self.connected and self.game_id:
            self.send_message({
                'command': 'game_state_update', 
                'game_id': self.game_id, 
                'game_state': game_state
            })
    
    def send_player_action(self, action_type, action_data):
        """Envía acciones del jugador (movimiento, disparos, etc.)"""
        if self.connected and self.game_id and self.player_number:
            self.send_message({
                'command': 'player_action',
                'game_id': self.game_id,
                'action_type': action_type,
                'action_data': action_data,
                'player': self.player_number
            })
    
    def send_start_game(self, difficulty, game_id=None):
        """Envía al servidor el comando para iniciar el juego con la dificultad seleccionada"""
        # Usar el game_id proporcionado o el almacenado
        game_id_to_use = game_id if game_id else self.game_id
        
        print(f"🎮 [CLIENT DEBUG] send_start_game llamado:")
        print(f"🎮 [CLIENT DEBUG] - connected: {self.connected}")
        print(f"🎮 [CLIENT DEBUG] - game_id: {game_id_to_use}")
        print(f"🎮 [CLIENT DEBUG] - difficulty: {difficulty}")
        
        if self.connected and game_id_to_use:
            message = {
                "command": "start_game",
                "game_id": game_id_to_use,
                "difficulty": difficulty
            }
            success = self.send_message(message)
            print(f"🎮 [CLIENT DEBUG] - Mensaje enviado: {success}")
            return success
        else:
            print(f"❌ [CLIENT DEBUG] ERROR: No se puede enviar start_game")
            print(f"❌ [CLIENT DEBUG] - Conectado: {self.connected}")
            print(f"❌ [CLIENT DEBUG] - Game ID: {game_id_to_use}")
            return False

    def send_message(self, message):
        if not self.connected or not self.socket:
            print("No hay conexión activa")
            return False
        
        try:
            data = pickle.dumps(message)
            self.socket.send(data)
            print(f"Mensaje enviado: {message}")  # DEBUG
            return True
        except BrokenPipeError:
            print("Error: Conexión perdida con el servidor")
            self.connected = False
            return False
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            self.connected = False
            return False
    
    def receive_messages(self):
        while self.connected:
            try:
                self.socket.settimeout(10.0)  # Aumentar timeout a 10 segundos
                data = self.socket.recv(4096)
                if not data:
                    print("Servidor cerró la conexión")
                    break
                    
                message = pickle.loads(data)
                print(f"Mensaje recibido del servidor: {message}")  # DEBUG
                
                # Manejar ping del servidor
                if message.get('type') == 'ping':
                    print("Ping recibido, enviando pong...")
                    self.send_message({'command': 'pong'})
                    continue
                    
                self.handle_message(message)
                
            except socket.timeout:
                # Enviar ping propio para mantener conexión activa
                print("Timeout - enviando ping de mantenimiento...")
                try:
                    self.send_message({'command': 'ping'})
                except:
                    break
                continue
            except ConnectionResetError:
                print("Conexión reiniciada por el servidor")
                break
            except Exception as e:
                print(f"Error recibiendo mensaje: {e}")
                break
        
        self.connected = False
        print("Hilo de recepción terminado")
    
    def handle_message(self, message):
        message_type = message.get('type')
        print(f"Manejando mensaje tipo: {message_type}")
        if message_type in self.message_handlers:
            self.message_handlers[message_type](message)
        else:
            print(f"Tipo de mensaje no manejado: {message_type}")
    
    def register_handler(self, message_type: str, handler: Callable[[Any], None]):
        self.message_handlers[message_type] = handler
    
    def disconnect(self):
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        print("Desconectado del servidor")