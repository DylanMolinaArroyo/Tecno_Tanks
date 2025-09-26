"""import socket
import pickle
import threading
from typing import Callable, Any

class NetworkClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.game_id = None
        self.player_number = None
        self.message_handlers = {}
        
    def connect(self, host='localhost', port=5555):
        try:
            self.socket.connect((host, port))
            self.connected = True
            # Iniciar hilo para recibir mensajes
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            return True
        except Exception as e:
            print(f"Error conectando al servidor: {e}")
            return False
    
    def create_game(self):
        if self.connected:
            self.send_message({'command': 'create_game'})
    
    def join_game(self, game_id):
        if self.connected:
            self.game_id = game_id
            self.send_message({'command': 'join_game', 'game_id': game_id})
    
    def send_game_state(self, game_state):
        if self.connected and self.game_id:
            self.send_message({
                'command': 'game_state_update', 
                'game_id': self.game_id, 
                'game_state': game_state
            })
    
    def send_player_action(self, action):
        if self.connected and self.game_id and self.player_number:
            self.send_message({
                'command': 'player_action',
                'game_id': self.game_id,
                'action': action,
                'player': self.player_number
            })
    
    def send_message(self, message):
        try:
            data = pickle.dumps(message)
            self.socket.send(data)
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            self.connected = False
    
    def receive_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                    
                message = pickle.loads(data)
                self.handle_message(message)
                
            except Exception as e:
                print(f"Error recibiendo mensaje: {e}")
                self.connected = False
                break
    
    def handle_message(self, message):
        message_type = message.get('type')
        if message_type in self.message_handlers:
            self.message_handlers[message_type](message)
    
    def register_handler(self, message_type: str, handler: Callable[[Any], None]):
        self.message_handlers[message_type] = handler
    
    def disconnect(self):
        self.connected = False
        try:
            self.socket.close()
        except:
            pass"""
            
###

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
        
    def connect(self, host='localhost', port=5555):
        try:
            # Crear nuevo socket si no existe o está cerrado
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                    
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # Timeout para conexión
            self.socket.connect((host, port))
            self.connected = True
            
            # Iniciar hilo para recibir mensajes
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            print(f"Conectado al servidor {host}:{port}")
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
    
    def create_game(self):
        if self.connected:
            self.send_message({'command': 'create_game'})
        else:
            print("No conectado al servidor")
    
    def join_game(self, game_id):
        if self.connected:
            self.game_id = game_id
            self.send_message({'command': 'join_game', 'game_id': game_id})
        else:
            print("No conectado al servidor")
    
    def send_game_state(self, game_state):
        if self.connected and self.game_id:
            self.send_message({
                'command': 'game_state_update', 
                'game_id': self.game_id, 
                'game_state': game_state
            })
    
    def send_player_action(self, action):
        if self.connected and self.game_id and self.player_number:
            self.send_message({
                'command': 'player_action',
                'game_id': self.game_id,
                'action': action,
                'player': self.player_number
            })
    
    def send_message(self, message):
        if not self.connected or not self.socket:
            print("No hay conexión activa")
            return False
            
        try:
            data = pickle.dumps(message)
            self.socket.send(data)
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
                # Configurar timeout para poder verificar si aún estamos conectados
                self.socket.settimeout(1.0)
                data = self.socket.recv(4096)
                if not data:
                    print("Servidor cerró la conexión")
                    break
                    
                message = pickle.loads(data)
                print(f"Mensaje recibido: {message}")  # Debug
                self.handle_message(message)
                
            except socket.timeout:
                # Timeout normal, continuar escuchando
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
        print(f"Manejando mensaje tipo: {message_type}")  # Debug
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