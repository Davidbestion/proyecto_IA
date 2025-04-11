from pyparsing import empty
from hex_board import HexBoard
import heapq
import random
# from itertools import combinations
import time

class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id  # 1 (rojo) or 2 (azul)

    def play(self, board: "HexBoard") -> tuple:
        raise NotImplementedError("Implement this method!")
    
# def timer_decorator(func):
#     from functools import wraps
    
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

class MiniMaxPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)
        self.TOP_MOVES = 8  # Número de movimientos a considerar en la heurística
        self.directions = [
            (0, -1),   # Izquierda
            (0, 1),    # Derecha
            (-1, 0),   # Arriba
            (1, 0),    # Abajo
            (-1, 1),   # Arriba derecha
            (1, -1)    # Abajo izquierda
        ]

    # @timer_decorator
    def play(self, board: HexBoard, time, depth = 3) -> tuple:
        _, best_move = self.minimax(board, depth, -float('inf'), float('inf'), self.player_id, True)
        if best_move is None and board.get_possible_moves(): #SI best_move es None, significa que siempre pierdo. Solucion: jugar random...
            best_move = random.choice(board.get_possible_moves())
        if best_move is None:
            raise ValueError("No valid moves available.")
        return best_move
    
    def minimax(self, board, depth, alpha, beta, player, maximizing_player):
        # Casos base: profundidad 0 o juego terminado
        winner = self.check_winner(board)
        if depth == 0 or winner is not None:
            if winner == self.player_id:# minimax siempre se llama con maximizing_player = True
                return float('inf'), None   # Yo siempre maximizo
            elif winner == 3 - self.player_id:  # El otro jugador siempre minimiza
                return -float('inf'), None
            else:
                return self.heuristic(board, self.player_id, maximizing_player), None
        
        valid_moves = self.get_ordered_moves(board, player, maximizing_player)[: self.TOP_MOVES] #Filtrar por la heurística
        # valid_moves = board.get_possible_moves()
        if not valid_moves:
            return self.heuristic(board, self.player_id), None
        
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
    def check_winner(self, board:HexBoard):
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
        
    
    def heuristic(self, board, player_id, maximizing_player:bool):
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
                if player_id == 1 and row == 0 and board.board[row][col] == player_id:
                    heapq.heappush(heap, (0, 0, col))
                    distances[0][col] = 0
                if player_id == 2 and col == 0 and board.board[row][col] == player_id:
                    heapq.heappush(heap, (0, row, 0))
                    distances[row][0] = 0
                    
                    
                if board.board[row][col] == (3 - player_id):
                    distances[row][col] = -1
        visited = [[False] * size for _ in range(size)]
        
        while heap:
            distance, r, c = heapq.heappop(heap)
            if visited[r][c]:
                continue
            visited[r][c] = True
            
            if player_id == 1 and r == size - 1 or player_id == 2 and c == size - 1:
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
                ady.append((nr,nc))
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
                        
        
        
                