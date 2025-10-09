import os
from supabase import create_client, Client
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
import uuid
from datetime import datetime

class GameDatabase:
    def __init__(self):
        """
        Initializes the GameDatabase instance and connects to Supabase using environment variables.
        """

        try:
            self.supabase_url = os.getenv('SUPABASE_URL', 'https://ojrxxocofzecwcrxlpar.supabase.co/')
            self.supabase_key = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9qcnh4b2NvZnplY3djcnhscGFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyODg3OTQsImV4cCI6MjA3NDg2NDc5NH0.aFlkJBq3OYs3IhAqRJj56mmcG7kJGcAXobHAxlFfKlE')
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            
            print(f"Conectado a Supabase: {self.supabase_url}")
            
        except Exception as e:
            print(f"Error inicializando base de datos: {e}")
            raise
    
    def create_or_get_player(self, username: str) -> Optional[Dict]:
        """
        Creates a new player with the given username or returns the existing player if found.

        Args:
            username (str): The username of the player.

        Returns:
            Optional[Dict]: The player record if found or created, otherwise None.
        """
       
        try:
            response = self.supabase.table('players')\
                .select('*')\
                .eq('username', username)\
                .execute()
            
            if response.data:
                print(f"Jugador existente: {username}")
                return response.data[0]
            
            new_player = {
                'username': username,
                'total_games_played': 0,
                'total_wins': 0,
                'total_kills': 0
            }
            
            response = self.supabase.table('players').insert(new_player).execute()
            
            if response.data:
                print(f"Nuevo jugador creado: {username}")
                return response.data[0]
            else:
                print(f"Error creando jugador: {username}")
                return None
            
        except Exception as e:
            print(f"Error creando/obteniendo jugador {username}: {e}")
            return None
    
    def update_player_stats(self, player_id: str, kills: int = 0, won: bool = False):
        """
        Updates the statistics of a player.

        Args:
            player_id (str): The ID of the player.
            kills (int, optional): Number of kills to add. Default is 0.
            won (bool, optional): Whether the player won the game. Default is False.
        """
        try:
            response = self.supabase.table('players')\
                .select('*')\
                .eq('id', player_id)\
                .execute()
            
            if not response.data:
                return
            
            player = response.data[0]
            updates = {
                'total_games_played': player['total_games_played'] + 1,
                'total_kills': player['total_kills'] + kills
            }
            
            if won:
                updates['total_wins'] = player['total_wins'] + 1
            
            self.supabase.table('players')\
                .update(updates)\
                .eq('id', player_id)\
                .execute()
                
            print(f"Estadísticas actualizadas para jugador {player_id}")
                
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")
    
    # --- Partidas ---
    def create_game(self, game_code: str, host_username: str, difficulty: str = "multiplayer") -> Optional[Dict]:
        """
        Creates a new game with the given code, host username, and difficulty.

        Args:
            game_code (str): The unique code for the game.
            host_username (str): The username of the host player.
            difficulty (str, optional): The difficulty level. Default is "multiplayer".

        Returns:
            Optional[Dict]: The created game record, or None if creation failed.
        """ 

        try:
            # Obtener o crear jugador host
            host_player = self.create_or_get_player(host_username)
            if not host_player:
                return None
            
            new_game = {
                'game_code': game_code,
                'host_player_id': host_player['id'],
                'difficulty': difficulty,
                'status': 'waiting',
                'max_players': 2,
                'current_players': 1
            }
            
            response = self.supabase.table('games').insert(new_game).execute()
            game = response.data[0] if response.data else None
            
            if game:
                self.add_player_to_game(game['id'], host_player['id'], 1)
                
                self.log_game_event(
                    game_id=game['id'],
                    player_id=host_player['id'],
                    event_type='game_created'
                )
                
                print(f"Partida creada en BD: {game_code} -> {game['id']}")
            
            return game
            
        except Exception as e:
            print(f"Error creando partida: {e}")
            return None
    
    def add_player_to_game(self, game_id: str, player_id: str, player_number: int) -> bool:
        """
        Adds a player to a game.

        Args:
            game_id (str): The ID of the game.
            player_id (str): The ID of the player.
            player_number (int): The player's number in the game.

        Returns:
            bool: True if the player was added successfully, False otherwise.
        """

        try:
            game_player = {
                'game_id': game_id,
                'player_id': player_id,
                'player_number': player_number
            }
            
            response = self.supabase.table('game_players').insert(game_player).execute()
            
            self.update_player_count(game_id)
            
            self.log_game_event(
                game_id=game_id,
                player_id=player_id,
                event_type='player_joined'
            )
            
            print(f"Jugador {player_id} añadido a partida {game_id}")
            return True
            
        except Exception as e:
            print(f"Error añadiendo jugador a partida: {e}")
            return False
    
    def update_player_count(self, game_id: str):
        """
        Updates the current player count for a game.

        Args:
            game_id (str): The ID of the game.
        """

        try:
            response = self.supabase.table('game_players')\
                .select('id', count='exact')\
                .eq('game_id', game_id)\
                .execute()
            
            player_count = response.count
            
            self.supabase.table('games')\
                .update({'current_players': player_count})\
                .eq('id', game_id)\
                .execute()
                
            print(f"Contador actualizado: partida {game_id} -> {player_count} jugadores")
                
        except Exception as e:
            print(f"Error actualizando contador: {e}")
    
    def start_game(self, game_id: str):
        """
        Marks a game as started and logs the event.

        Args:
            game_id (str): The ID of the game.
        """

        try:
            updates = {
                'status': 'active',
                'started_at': datetime.now().isoformat()
            }
            
            self.supabase.table('games')\
                .update(updates)\
                .eq('id', game_id)\
                .execute()
                
            self.log_game_event(
                game_id=game_id,
                event_type='game_started'
            )
            
            print(f"Partida {game_id} iniciada")
                
        except Exception as e:
            print(f"Error iniciando partida: {e}")
    
    def finish_game(self, game_id: str, winner_player_id: str = None):
        """
        Marks a game as finished and logs the event.

        Args:
            game_id (str): The ID of the game.
            winner_player_id (str, optional): The ID of the winning player.
        """

        try:
            updates = {
                'status': 'finished',
                'finished_at': datetime.now().isoformat()
            }
            
            self.supabase.table('games')\
                .update(updates)\
                .eq('id', game_id)\
                .execute()
                
            # Evento de finalización
            event_data = {'winner': winner_player_id} if winner_player_id else {}
            self.log_game_event(
                game_id=game_id,
                event_type='game_finished',
                event_data=event_data
            )
            
            print(f"Partida {game_id} finalizada")
                
        except Exception as e:
            print(f"Error finalizando partida: {e}")
    
    def save_game_stats(self, game_id: str, player_stats: List[Dict]):
        """
        Saves the final statistics for all players in a game.

        Args:
            game_id (str): The ID of the game.
            player_stats (List[Dict]): List of player statistics dictionaries.
        """

        try:
            for stats in player_stats:
                self.supabase.table('game_stats').insert(stats).execute()
                
                self.update_player_stats(
                    player_id=stats['player_id'],
                    kills=stats.get('kills', 0),
                    won=stats.get('won', False)
                )
                
                print(f"Estadísticas guardadas para jugador {stats['player_id']} en partida {game_id}")
                
        except Exception as e:
            print(f"Error guardando estadísticas: {e}")
    
    def log_game_event(self, game_id: str, event_type: str, player_id: str = None, event_data: Dict = None):
        """
        Logs an event for a game.

        Args:
            game_id (str): The ID of the game.
            event_type (str): The type of event.
            player_id (str, optional): The ID of the player related to the event.
            event_data (Dict, optional): Additional event data.
        """

        try:
            event = {
                'game_id': game_id,
                'event_type': event_type,
                'event_data': event_data or {}
            }
            
            if player_id:
                event['player_id'] = player_id
            
            self.supabase.table('game_events').insert(event).execute()
            
            print(f"Evento registrado: {event_type} para partida {game_id}")
            
        except Exception as e:
            print(f"Error registrando evento: {e}")
    
    def get_game_by_code(self, game_code: str) -> Optional[Dict]:
        """
        Retrieves a game by its code.

        Args:
            game_code (str): The unique code of the game.

        Returns:
            Optional[Dict]: The game record if found, otherwise None.
        """

        try:
            response = self.supabase.table('games')\
                .select('*')\
                .eq('game_code', game_code)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Error obteniendo partida: {e}")
            return None
    
    def get_game_players(self, game_id: str) -> List[Dict]:
        """
        Retrieves all players for a given game.

        Args:
            game_id (str): The ID of the game.

        Returns:
            List[Dict]: List of player records for the game.
        """
        
        try:
            response = self.supabase.table('game_players')\
                .select('*, players(username)')\
                .eq('game_id', game_id)\
                .execute()
            
            return response.data
            
        except Exception as e:
            print(f"Error obteniendo jugadores: {e}")
            return []