from player import Player
from board import HexBoard
import heapq
import random
# from itertools import combinations
import time

# Tiempo límite en segundos para cada jugada (margen de seguridad vs 5s del torneo)
TIME_LIMIT = 4.5

class TimeoutException(Exception):
    """Excepción para interrumpir la búsqueda cuando se agota el tiempo"""
    pass

# def timer_decorator(func):
#     from functools import wraps
#
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         elapsed_time = end_time - start_time
#         print(f" {elapsed_time:.4f} segundos")
#         if elapsed_time >= 10:
#             raise Exception("Tiempo excedido")
#         return result
#     return wrapper

class SmartPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)

        self.directions = [
            (0, -1),   # Izquierda
            (0, 1),    # Derecha
            (-1, 0),   # Arriba
            (1, 0),    # Abajo
            (-1, 1),   # Arriba derecha
            (1, -1)    # Abajo izquierda
        ]

    # @timer_decorator
    def play(self, board: HexBoard) -> tuple:
        """
        Ejecuta minimax con depth y TOP_MOVES ajustados dinámicamente.
        Optimiza el branching factor según la fase del juego.
        """
        self.start_time = time.time()
        self.time_limit = TIME_LIMIT
        
        # Calcular número de movimientos posibles
        num_moves = len(board.get_possible_moves())
        
        # Ajustar TOP_MOVES y depth según la fase del juego
        if num_moves > 50:  # Inicio: muchas opciones, branching explosivo
            self.top_moves = min(6, num_moves)  # Limitar agresivamente
            initial_depth = 3
        elif num_moves > 30:  # Principio-medio: balancear
            self.top_moves = min(8, num_moves)
            initial_depth = 3
        elif num_moves > 15:  # Medio-final: más opciones
            self.top_moves = min(10, num_moves)
            initial_depth = 4
        else:  # Final: pocas opciones, explorar todas o casi todas
            self.top_moves = min(15, num_moves)  # Prácticamente todas
            initial_depth = 5
        
        best_move = None
        
        try:
            _, best_move = self.minimax(board, initial_depth, -float('inf'), float('inf'), self.player_id, True)
        except TimeoutException:
            # Se agotó el tiempo, pero best_move ya tiene la mejor jugada encontrada
            pass
        
        # Fallback: si no encontramos ninguna jugada, jugamos random
        if best_move is None and board.get_possible_moves():
            best_move = random.choice(board.get_possible_moves())
        
        if best_move is None:
            raise ValueError("No valid moves available.")
        
        return best_move

    def minimax(self, board, depth, alpha, beta, player, maximizing_player):
        # Verificar timeout antes de continuar la búsqueda
        if time.time() - self.start_time > self.time_limit:
            raise TimeoutException()
        
        # Casos base: profundidad 0 o juego terminado
        winner = self.check_winner(board)
        if depth == 0 or winner is not None:
            if winner == self.player_id:# minimax siempre se llama con maximizing_player = True
                return float('inf'), None   # Yo siempre maximizo
            elif winner == 3 - self.player_id:  # El otro jugador siempre minimiza
                return -float('inf'), None
            else:
                return self.heuristic(board, self.player_id, maximizing_player), None

        valid_moves = self.get_ordered_moves(board, player, maximizing_player)[: self.top_moves] #Filtrar por la heurística
        # valid_moves = board.get_possible_moves()
        if not valid_moves:
            return self.heuristic(board, self.player_id, maximizing_player), None

        best_move = None
        if maximizing_player:
            max_eval = -float('inf')

            for move in valid_moves:
                row, col = move
                game_copy = board.clone()
                game_copy.place_piece(row, col, player)
                # game_copy.check_connection(player)

                evaluation, _ = self.minimax(game_copy, depth-1, alpha, beta, (3-player), False)
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move

                #Yo maximizo, mi padre minimiza
                #Si mi alpha es mayor que el beta de mi padre, dejo de buscar
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in valid_moves:
                row, col = move
                game_copy = board.clone()
                game_copy.place_piece(row, col, player)
                # game_copy.check_connection(player)

                evaluation, _ = self.minimax(game_copy, depth-1, alpha, beta, (3-player), True)
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move

                beta = min(beta, evaluation)
                #Yo minimizo, mi padre maximiza
                #Si mi beta es menor que el alpha de mi padre, dejo de buscar
                if beta <= alpha:
                    break
            return min_eval, best_move

    def check_winner(self, board: HexBoard):
        """Verifica si hay un ganador en el tablero"""
        if board.check_connection(1): return 1
        if board.check_connection(2): return 2
        return None

    def get_ordered_moves(self, board, player, max_player):
        """Devuelve una lista de movimientos ordenada por la heurística"""
        moves = board.get_possible_moves()
        result = []
        for i in range(len(moves)):
            new_board = board.clone()
            new_board.place_piece(moves[i][0], moves[i][1], player)
            result.append((self.heuristic(new_board, self.player_id, max_player), moves[i]))
        result.sort(reverse=(max_player))
        return [move for _, move in result]

    def heuristic(self, board, player_id, maximizing_player: bool):
        """Heurística que combina la distancia de Dijkstra y el control del centro"""
        winner = self.check_winner(board)
        if winner == player_id:
            return float('inf')
        if winner == 3 - player_id:
            return -float('inf')

        dijkstra_distance = self.dijkstra_heuristic(board, player_id)
        my_bridges = self.find_bridges(board, player_id)

        enemy_dijkstra_distance = self.dijkstra_heuristic(board, 3 - player_id)
        enemy_bridges = self.find_bridges(board, 3 - player_id)

        if maximizing_player:
            return 0.7 * dijkstra_distance + 0.3 * my_bridges - 0.3 * enemy_dijkstra_distance - 0.7 * enemy_bridges
        else:
            return 0.7 * enemy_dijkstra_distance + 0.3 * enemy_bridges - 0.3 * dijkstra_distance - 0.7 * my_bridges

    def dijkstra_heuristic(self, board, player_id):
        """Busca la distancia mas corta usando Dijkstra"""
        size = board.size
        heap = []
        distances = [[float('inf')] * size for _ in range(size)]
        for row in range(size):
            for col in range(size):
                if player_id == 1 and col == 0 and board.board[row][col] == player_id:  # player1: izq->der
                    heapq.heappush(heap, (0, row, 0))
                    distances[row][0] = 0
                if player_id == 2 and row == 0 and board.board[row][col] == player_id:  # player2: arr->abajo
                    heapq.heappush(heap, (0, 0, col))
                    distances[0][col] = 0

                if board.board[row][col] == (3 - player_id):
                    distances[row][col] = -1
        visited = [[False] * size for _ in range(size)]

        while heap:
            distance, r, c = heapq.heappop(heap)
            if visited[r][c]:
                continue
            visited[r][c] = True

            if player_id == 1 and c == size - 1 or player_id == 2 and r == size - 1:
                return -distance
            
            for dr, dc in self.directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size and distances[nr][nc] != -1:
                    cost = 0 if board.board[nr][nc] == player_id else 1
                    new_dist = distance + cost
                    if new_dist < distances[nr][nc]:
                        distances[nr][nc] = new_dist
                        heapq.heappush(heap, (new_dist, nr, nc))
        return -float('inf')

    def _get_empty_adyacents(self, board, row, col):
        ady = []
        for dr, dc in self.directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < board.size and 0 <= nc < board.size and board.board[nr][nc] == 0:
                ady.append((nr, nc))
        return ady

    def find_bridges(self, board, player_id):
        """Encuentra los puentes en el tablero para el jugador dado"""
        size = board.size
        count_bridges = 0
        player_cells = [(i, j) for i in range(size) for j in range(size) if board.board[i][j] == player_id]

        # Verificación más eficiente de vecindad
        for i in range(len(player_cells)):
            for j in range(i+1, len(player_cells)):
                (x1, y1), (x2, y2) = player_cells[i], player_cells[j]
                #Si se encuentran en una distancia de 2 o menos
                if abs(x1 - x2) <= 2 and abs(y1 - y2) <= 2:
                    #Buscar las casillas adyacentes en comun
                    common = set(self._get_empty_adyacents(board, x1, y1)).intersection(set(self._get_empty_adyacents(board, x2, y2)))
                    #Si hay dos => hay dos caminos de tamano 1 entre ambas => un puente.
                    if len(common) >= 2:
                        count_bridges += 1
        return count_bridges
