import socket
import threading
import pickle
import time
import os
from datetime import datetime
import random 

# Importar el módulo de base de datos
try:
    from database import GameDatabase
    DB_AVAILABLE = True
except ImportError:
    print("Advertencia: No se pudo importar database.py. El servidor funcionará sin base de datos.")
    DB_AVAILABLE = False

class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # CORRECCIÓN: Esta línea va DESPUÉS de crear el socket
        self.connections = []
        self.games = {}  # {game_id: {connections: [player1_conn, player2_conn], game_state: {}, db_id: None, host_username: ''}}
        self.game_counter = 0
        self.running = True
        
        # Base de datos
        if DB_AVAILABLE:
            self.db = GameDatabase()
            print("Base de datos conectada correctamente")
        else:
            self.db = None
            print("Servidor ejecutándose sin base de datos")
        
        # Mapeo de conexiones a usuarios
        self.connection_users = {}  # {conn: username}
        self.connection_game = {}   # {conn: game_id}
        
    def start(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen()
            print(f"Servidor iniciado en {self.host}:{self.port}")
            print("Comandos disponibles: 'quit' para salir, 'status' para estado del servidor")
            
            # Obtener y mostrar IPs disponibles
            self.show_network_info()
            
            # Hilo para aceptar conexiones
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            # Hilo principal para manejar comandos del servidor
            self.handle_commands()
            
        except Exception as e:
            print(f"Error al iniciar servidor: {e}")
        finally:
            self.cleanup()
    
    def show_network_info(self):
        """Muestra información de red para ayudar a la conexión"""
        try:
            # Obtener nombre del host
            hostname = socket.gethostname()
            print(f"Hostname: {hostname}")
            
            # Obtener IP local
            local_ip = socket.gethostbyname(hostname)
            print(f"IP Local: {local_ip}")
            
            # Obtener todas las IPs de interfaces de red
            print("Interfaces de red disponibles:")
            try:
                import netifaces
                for interface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr_info in addrs[netifaces.AF_INET]:
                            ip = addr_info['addr']
                            if ip != '127.0.0.1':
                                print(f"  - {interface}: {ip}")
            except ImportError:
                print("  (Instala netifaces para ver todas las interfaces: pip install netifaces)")
                
        except Exception as e:
            print(f"Error obteniendo información de red: {e}")
    
    def accept_connections(self):
        while self.running:
            try:
                conn, addr = self.socket.accept()
                print(f"Conexión establecida desde {addr}")
                
                # Crear hilo para manejar el cliente
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
                
                self.connections.append(conn)
            except Exception as e:
                if self.running:
                    print(f"Error aceptando conexión: {e}")
                break
    
    def handle_client(self, conn, addr):
        print(f"Manejando cliente desde {addr}")
    
        # Configurar timeout más largo y opciones de socket
        # Configurar timeout más largo
        conn.settimeout(60.0)  # 60 segundos en lugar de 30
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        try:
            while self.running:
                try:
                    data = conn.recv(4096)
                    if not data:
                        print(f"Cliente {addr} desconectado (sin datos)")
                        break
                    
                    message = pickle.loads(data)
                    print(f"Procesando mensaje de {addr}: {message}")
                    self.process_message(conn, message, addr)
                
                except socket.timeout:
                    # Enviar ping para mantener la conexión activa
                    try:
                        print(f"Enviando ping a {addr}")
                        conn.send(pickle.dumps({'type': 'ping'}))
                    except Exception as e:
                        print(f"Error enviando ping a {addr}: {e}")
                        break
                    continue
                except ConnectionResetError:
                    print(f"Conexión reiniciada por cliente {addr}")
                    break
                except Exception as e:
                    print(f"Error con cliente {addr}: {e}")
                    break
                    
        except Exception as e:
            print(f"Error grave con cliente {addr}: {e}")
        finally:
            self.remove_connection(conn)
            try:
                conn.close()
            except:
                pass
            print(f"Conexión con {addr} cerrada")
    
    def process_message(self, conn, message, addr):
        command = message.get('command')
        
        if command == 'create_game':
            username = message.get('username', 'Anonymous')
            self.connection_users[conn] = username
            
            game_id = self.create_game(conn, username)
            if game_id:
                conn.send(pickle.dumps({
                    'type': 'game_created', 
                    'game_id': game_id, 
                    'player_number': 1
                }))
            else:
                conn.send(pickle.dumps({
                    'type': 'error', 
                    'message': 'No se pudo crear el juego'
                }))
            
        elif command == 'join_game':
            game_id = message.get('game_id')
            username = message.get('username', 'Anonymous')
            self.connection_users[conn] = username
            
            if self.join_game(conn, game_id, username):
                conn.send(pickle.dumps({
                    'type': 'game_joined', 
                    'game_id': game_id, 
                    'player_number': 2
                }))
            else:
                conn.send(pickle.dumps({
                    'type': 'join_failed', 
                    'reason': 'Juego no encontrado o lleno'
                }))
                
        elif command == 'game_state_update':
            game_id = message.get('game_id')
            game_state = message.get('game_state')
            self.broadcast_to_game(game_id, {
                'type': 'state_update', 
                'game_state': game_state
            }, conn)
            
        elif command == 'player_action':
            game_id = message.get('game_id')
            action_type = message.get('action_type')  # CORRECCIÓN: usar action_type
            action_data = message.get('action_data')  # CORRECCIÓN: usar action_data
            self.broadcast_to_game(game_id, {
                'type': 'player_action', 
                'action_type': action_type,
                'action_data': action_data,
                'player': message.get('player')
            }, conn)
            
        elif command == 'start_game':
            game_id = message.get('game_id')
            #self.start_game(game_id)
            difficulty = message.get('difficulty')
            print(f"DEBUG: start_game recibido - game_id: {game_id}, difficulty: {difficulty}")
            self.start_game(game_id, difficulty)
            
        elif command == 'game_stats':
            game_id = message.get('game_id')
            stats = message.get('stats')
            self.save_game_stats(game_id, stats)
            
        elif command == 'player_ready':
            game_id = message.get('game_id')
            self.handle_player_ready(game_id, conn)
            
        elif command == 'ping':
            conn.send(pickle.dumps({'type': 'pong'}))
    
    def create_game(self, conn, username: str):
        """Crea juego en base de datos y en memoria"""
        try:
            self.game_counter += 1
            game_code = f"game_{self.game_counter}"
            
            # VERIFICAR SI EL JUEGO YA EXISTE EN MEMORIA
            while game_code in self.games:
                self.game_counter += 1
                game_code = f"game_{self.game_counter}"
            
            db_game_id = None
            # Crear en base de datos si está disponible
            if self.db:
                try:
                    db_game = self.db.create_game(game_code, username)
                    if db_game:
                        db_game_id = db_game['id']
                        print(f"Juego creado en BD: {db_game_id}")
                    else:
                        print("Advertencia: No se pudo crear juego en base de datos")
                except Exception as db_error:
                    print(f"Error en BD (continuando sin BD): {db_error}")
            
            # Crear en memoria
            self.games[game_code] = {
                'connections': [conn, None],
                'game_state': {
                    'players_ready': 0,
                    'game_started': False,
                    'players': [username, None]
                },
                'db_id': db_game_id,
                'host_username': username
            }
            
            self.connection_game[conn] = game_code
            
            print(f"Juego creado: {game_code} (Jugadores: 1/2)")
            return game_code
            
        except Exception as e:
            print(f"Error creando juego: {e}")
            return None
    
    def join_game(self, conn, game_id, username: str):
        """Une jugador a partida en base de datos y memoria"""
        try:
            if game_id in self.games and self.games[game_id]['connections'][1] is None:
                
                # Actualizar en base de datos si está disponible
                if self.db and self.games[game_id]['db_id']:
                    db_game = self.db.get_game_by_code(game_id)
                    if db_game:
                        player = self.db.create_or_get_player(username)
                        if player:
                            success = self.db.add_player_to_game(db_game['id'], player['id'], 2)
                            if not success:
                                print("Error añadiendo jugador a partida en BD")
                
                # Actualizar en memoria
                self.games[game_id]['connections'][1] = conn
                self.games[game_id]['game_state']['players'][1] = username
                self.connection_game[conn] = game_id
                
                # Notificar al primer jugador
                host_conn = self.games[game_id]['connections'][0]
                self.send_to_connection(host_conn, {
                    'type': 'player_joined', 
                    'game_id': game_id, 
                    'username': username
                })
                
                print(f"Jugador {username} unido a {game_id} (Jugadores: 2/2)")
                return True
                
            else:
                print(f"Intento de unión fallido: {game_id} no existe o está lleno")
                return False
                
        except Exception as e:
            print(f"Error uniendo jugador a partida: {e}")
            return False
            
    def start_game(self, game_id, difficulty=None):
        """Inicia una partida con la dificultad especificada y una semilla aleatoria"""
        print(f"🎮 SERVER DEBUG: start_game llamado - game_id: {game_id}, existe: {game_id in self.games}")
        try:
            if game_id in self.games:
                print(f"🎮 SERVER DEBUG: Iniciando juego {game_id}")
                self.games[game_id]['game_state']['game_started'] = True
            
                # Guardar la dificultad si se proporciona
                if difficulty:
                    self.games[game_id]['game_state']['difficulty'] = difficulty
            
                # Actualizar en base de datos
                if self.db and self.games[game_id]['db_id']:
                    self.db.start_game(self.games[game_id]['db_id'])
            
                # --- CAMBIO IMPORTANTE: Generar y enviar una semilla aleatoria ---
                game_seed = random.randint(0, 999999) # Genera una semilla única para esta partida
                
                game_message = {
                    'type': 'game_started',
                    'difficulty': difficulty or self.games[game_id]['game_state'].get('difficulty', {}),
                    'seed': game_seed  # Añade la semilla al mensaje
                }
                
                print(f"🎮 SERVER DEBUG: Enviando mensaje a jugadores: {game_message}")
                self.broadcast_to_game(game_id, game_message)
            
                print(f"🎮 SERVER: Juego {game_id} iniciado con semilla: {game_seed}")
            else:
                print(f"❌ SERVER ERROR: Juego {game_id} no encontrado")
                
        except Exception as e:
            print(f"❌ SERVER ERROR iniciando juego: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_player_ready(self, game_id, conn):
        """Maneja cuando un jugador está listo"""
        try:
            if game_id in self.games:
                self.games[game_id]['game_state']['players_ready'] += 1
                ready_count = self.games[game_id]['game_state']['players_ready']
                
                print(f"Jugador listo en {game_id} ({ready_count}/2)")
                
                # Notificar a ambos jugadores
                self.broadcast_to_game(game_id, {
                    'type': 'player_ready',
                    'ready_count': ready_count
                })
                
                # Si ambos están listos, iniciar juego
                if ready_count == 2:
                    self.start_game(game_id)
                    
        except Exception as e:
            print(f"Error manejando jugador listo: {e}")
    
    def save_game_stats(self, game_id, stats):
        """Guarda estadísticas de la partida"""
        try:
            if self.db and game_id in self.games and self.games[game_id]['db_id']:
                # Preparar estadísticas para la base de datos
                game_stats = []
                for player_stats in stats:
                    game_stats.append({
                        'game_id': self.games[game_id]['db_id'],
                        'player_id': player_stats.get('player_id'),
                        'final_health': player_stats.get('final_health'),
                        'kills': player_stats.get('kills', 0),
                        'damage_dealt': player_stats.get('damage_dealt', 0),
                        'damage_received': player_stats.get('damage_received', 0),
                        'survival_time': player_stats.get('survival_time', 0),
                        'won': player_stats.get('won', False)
                    })
                
                self.db.save_game_stats(self.games[game_id]['db_id'], game_stats)
                print(f"Estadísticas guardadas para {game_id}")
                
        except Exception as e:
            print(f"Error guardando estadísticas: {e}")
    
    def broadcast_to_game(self, game_id, message, sender_conn=None):
        """Envía mensaje a todos los jugadores de una partida"""
        print(f"🎮 SERVER DEBUG: broadcast_to_game - game_id: {game_id}, mensaje: {message}")
        if game_id in self.games:
            for conn in self.games[game_id]['connections']:
                if conn and conn != sender_conn:
                    try:
                        print(f"🎮 SERVER DEBUG: Enviando a conexión: {conn}")
                        conn.send(pickle.dumps(message))
                        print(f"🎮 SERVER DEBUG: Mensaje enviado exitosamente")
                    except Exception as e:
                        print(f"❌ SERVER ERROR enviando mensaje a jugador: {e}")
                        self.remove_connection(conn)
        else:
            print(f"❌ SERVER ERROR: Juego {game_id} no encontrado para broadcast")
    
    def send_to_connection(self, conn, message):
        """Envía mensaje a una conexión específica"""
        try:
            conn.send(pickle.dumps(message))
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            self.remove_connection(conn)
    
    def remove_connection(self, conn):
        """Maneja desconexión limpiando memoria y base de datos"""
        try:
            if conn in self.connections:
                self.connections.remove(conn)
            
            username = self.connection_users.get(conn, 'Unknown')
            game_id = self.connection_game.get(conn)
            
            # Remover de juegos
            if game_id and game_id in self.games:
                game = self.games[game_id]
                
                # Encontrar índice del jugador
                player_index = None
                for i, game_conn in enumerate(game['connections']):
                    if game_conn == conn:
                        player_index = i
                        break
                
                if player_index is not None:
                    # Notificar al otro jugador
                    other_index = 1 - player_index
                    other_conn = game['connections'][other_index]
                    
                    if other_conn:
                        self.send_to_connection(other_conn, {
                            'type': 'player_disconnected',
                            'username': username
                        })
                    
                    # Limpiar conexión
                    game['connections'][player_index] = None
                    game['game_state']['players'][player_index] = None
                    
                    print(f"Jugador {username} desconectado de {game_id}")
                    
                    # Si ambos jugadores están desconectados, eliminar juego
                    if all(conn is None for conn in game['connections']):
                        # Marcar como finalizado en base de datos
                        if self.db and game['db_id']:
                            self.db.finish_game(game['db_id'])
                        
                        del self.games[game_id]
                        print(f"Juego {game_id} eliminado (todos desconectados)")
                    # Si solo queda un jugador, reducir contador
                    elif game['connections'][other_index] is not None:
                        game['game_state']['players_ready'] = 0
                        print(f"Juego {game_id} continúa con 1 jugador")
            
            # Limpiar mapeos
            if conn in self.connection_users:
                del self.connection_users[conn]
            if conn in self.connection_game:
                del self.connection_game[conn]
                
        except Exception as e:
            print(f"Error removiendo conexión: {e}")
    
    def get_server_status(self):
        """Obtiene estado del servidor"""
        active_games = sum(1 for game in self.games.values() 
                          if any(conn is not None for conn in game['connections']))
        total_players = sum(1 for game in self.games.values() 
                           for conn in game['connections'] if conn is not None)
        
        return {
            'active_connections': len(self.connections),
            'active_games': active_games,
            'total_players': total_players,
            'total_games_created': self.game_counter,
            'database_connected': self.db is not None
        }
    
    def handle_commands(self):
        """Maneja comandos de consola del servidor"""
        while self.running:
            try:
                cmd = input().lower().strip()
                
                if cmd == 'quit' or cmd == 'exit':
                    print("Cerrando servidor...")
                    self.running = False
                    break
                    
                elif cmd == 'status':
                    status = self.get_server_status()
                    print("\n--- Estado del Servidor ---")
                    print(f"Conexiones activas: {status['active_connections']}")
                    print(f"Partidas activas: {status['active_games']}")
                    print(f"Jugadores totales: {status['total_players']}")
                    print(f"Total partidas creadas: {status['total_games_created']}")
                    print(f"Base de datos: {'Conectada' if status['database_connected'] else 'No conectada'}")
                    
                    # Mostrar partidas activas
                    if self.games:
                        print("\nPartidas activas:")
                        for game_id, game in self.games.items():
                            players = []
                            for i, conn in enumerate(game['connections']):
                                if conn:
                                    username = self.connection_users.get(conn, 'Unknown')
                                    players.append(f"P{i+1}:{username}")
                            
                            if players:
                                status = "Activa" if game['game_state']['game_started'] else "Esperando"
                                print(f"  {game_id}: {', '.join(players)} [{status}]")
                    
                    print("")
                    
                elif cmd == 'games':
                    print("\nPartidas en memoria:")
                    for game_id, game in self.games.items():
                        print(f"  {game_id}: {game}")
                    print("")
                    
                elif cmd == 'help':
                    print("\nComandos disponibles:")
                    print("  status  - Mostrar estado del servidor")
                    print("  games   - Mostrar partidas en memoria")
                    print("  quit    - Cerrar servidor")
                    print("  help    - Mostrar esta ayuda\n")
                    
                else:
                    print(f"Comando desconocido: {cmd}. Escribe 'help' para ayuda.")
                    
            except (EOFError, KeyboardInterrupt):
                print("\nCerrando servidor...")
                self.running = False
                break
            except Exception as e:
                print(f"Error procesando comando: {e}")
    
    def cleanup(self):
        """Limpieza antes de cerrar el servidor"""
        print("Realizando limpieza...")
        
        # Cerrar todas las conexiones
        for conn in self.connections:
            try:
                conn.close()
            except:
                pass
        
        # Marcar partidas como finalizadas en BD
        if self.db:
            for game_id, game in self.games.items():
                if game['db_id']:
                    try:
                        self.db.finish_game(game['db_id'])
                        print(f"Partida {game_id} marcada como finalizada en BD")
                    except Exception as e:
                        print(f"Error finalizando partida {game_id}: {e}")
        
        try:
            self.socket.close()
        except:
            pass
        
        print("Servidor cerrado correctamente")

if __name__ == "__main__":
    server = GameServer()
    server.start()