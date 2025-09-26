import socket
import threading
import pickle
import time

class GameServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.games = {}  # {game_id: [player1_conn, player2_conn, game_state]}
        self.game_counter = 0
        self.running = True
        
    def start(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen()
            print(f"Servidor iniciado en {self.host}:{self.port}")
            
            # Hilo para aceptar conexiones
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.start()
            
            # Hilo principal para manejar comandos del servidor
            self.handle_commands()
            
        except Exception as e:
            print(f"Error al iniciar servidor: {e}")
    
    def accept_connections(self):
        while self.running:
            try:
                conn, addr = self.socket.accept()
                print(f"Conexión establecida desde {addr}")
                
                # Crear hilo para manejar el cliente
                client_thread = threading.Thread(target=self.handle_client, args=(conn,))
                client_thread.start()
                
                self.connections.append(conn)
            except:
                break
    
    def handle_client(self, conn):
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break
                    
                message = pickle.loads(data)
                self.process_message(conn, message)
                
        except Exception as e:
            print(f"Error con cliente: {e}")
        finally:
            self.remove_connection(conn)
            conn.close()
    
    def process_message(self, conn, message):
        command = message.get('command')
        
        if command == 'create_game':
            game_id = self.create_game(conn)
            conn.send(pickle.dumps({'type': 'game_created', 'game_id': game_id, 'player_number': 1}))
            
        elif command == 'join_game':
            game_id = message.get('game_id')
            if self.join_game(conn, game_id):
                conn.send(pickle.dumps({'type': 'game_joined', 'game_id': game_id, 'player_number': 2}))
            else:
                conn.send(pickle.dumps({'type': 'join_failed', 'reason': 'Juego no encontrado'}))
                
        elif command == 'game_state_update':
            game_id = message.get('game_id')
            game_state = message.get('game_state')
            self.broadcast_to_game(game_id, {'type': 'state_update', 'game_state': game_state}, conn)
            
        elif command == 'player_action':
            game_id = message.get('game_id')
            action = message.get('action')
            self.broadcast_to_game(game_id, {'type': 'player_action', 'action': action, 'player': message.get('player')}, conn)
    
    def create_game(self, conn):
        self.game_counter += 1
        game_id = f"game_{self.game_counter}"
        self.games[game_id] = [conn, None, {'players_ready': 0, 'game_started': False}]
        print(f"Juego creado: {game_id}")
        return game_id
    
    def join_game(self, conn, game_id):
        if game_id in self.games and self.games[game_id][1] is None:
            self.games[game_id][1] = conn
            # Notificar al primer jugador
            self.send_to_connection(self.games[game_id][0], {'type': 'player_joined', 'game_id': game_id})
            print(f"Jugador unido a {game_id}")
            return True
        return False
    
    def broadcast_to_game(self, game_id, message, sender_conn=None):
        if game_id in self.games:
            for conn in self.games[game_id][:2]:
                if conn and conn != sender_conn:
                    try:
                        conn.send(pickle.dumps(message))
                    except:
                        self.remove_connection(conn)
    
    def send_to_connection(self, conn, message):
        try:
            conn.send(pickle.dumps(message))
        except:
            self.remove_connection(conn)
    
    def remove_connection(self, conn):
        if conn in self.connections:
            self.connections.remove(conn)
        
        # Remover de juegos
        for game_id, game_data in list(self.games.items()):
            for i in range(2):
                if game_data[i] == conn:
                    # Notificar al otro jugador
                    other_player = game_data[1-i] if game_data[1-i] else None
                    if other_player:
                        self.send_to_connection(other_player, {'type': 'player_disconnected'})
                    
                    del self.games[game_id]
                    print(f"Juego {game_id} eliminado")
                    break
    
    def handle_commands(self):
        while self.running:
            try:
                cmd = input("Comando del servidor (quit para salir): ").lower()
                if cmd == 'quit':
                    self.running = False
                    self.socket.close()
                    break
            except:
                break

if __name__ == "__main__":
    server = GameServer()
    server.start()