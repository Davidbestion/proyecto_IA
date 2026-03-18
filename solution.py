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
        
        # Calcular número de movimientos posibles y ratio respecto al tablero total
        num_moves = len(board.get_possible_moves())
        total_cells = board.size * board.size
        ratio = num_moves / total_cells  # fracción de casillas vacías restantes
        
        # Ajustar TOP_MOVES y depth según la fase del juego (relativo al tamaño del tablero)
        # Balance: menos profundidad → más ramas (mas casillas libres, menos decisiva la heurística)
        #          más profundidad → menos ramas (menos casillas libres, heurística más confiable)
        if ratio > 0.95:      # Inicio: muchas casillas vacías, árbol explosivo
            self.top_moves = min(20, num_moves)
            initial_depth = 4
        elif ratio > 0.87:    # Principio-medio: balances
            self.top_moves = min(15, num_moves)
            initial_depth = 5
        elif ratio > 0.80:    # Medio-final: reducir ramas, aumentar profundidad
            self.top_moves = min(12, num_moves)
            initial_depth = 6
        else:                 # Final: pocas casillas, heurística confiable
            self.top_moves = min(10, num_moves)
            initial_depth = 7
        
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

        valid_moves = self.get_ordered_moves(board, player, maximizing_player)[: self.top_moves] # Filtrar por la heurística y limitar a top_moves
        if not valid_moves:
            # Si no hay movimientos válidos, evaluamos la posición actual
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
        """
        Heurística que combina la distancia de Dijkstra y los puentes.
        SIEMPRE devuelve la puntuación desde la perspectiva de player_id.
        El minimax se encarga de maximizar/minimizar; esta función solo dice
        "qué tan buena es esta posición para player_id".
        """
        winner = self.check_winner(board)
        if winner == player_id:
            return float('inf')
        if winner == 3 - player_id:
            return -float('inf')

        # dijkstra devuelve -distancia: más cercano a 0 = mejor para el jugador
        my_dist = self.dijkstra_heuristic(board, player_id)
        enemy_dist = self.dijkstra_heuristic(board, 3 - player_id)

        my_bridges = self.find_bridges(board, player_id)
        enemy_bridges = self.find_bridges(board, 3 - player_id)

        # Pesos simétricos: avanzar propio y bloquear enemigo tienen el mismo valor.
        # (my_dist - enemy_dist): positivo cuando enemy_path > my_path (yo estoy más cerca)
        # Los puentes se añaden como bonus secundario
        return 0.7 * (my_dist - enemy_dist) + 0.3 * (my_bridges - enemy_bridges)

    def dijkstra_heuristic(self, board, player_id):
        """
        Busca el camino más corto de un borde al otro usando Dijkstra.
        Siembra desde TODAS las casillas del borde inicial:
          - Casillas propias: coste 0 (ya ocupadas, no hay que hacer nada)
          - Casillas vacías:  coste 1 (hay que colocar una ficha)
          - Casillas enemigas: se saltan (no se puede pasar por ahí)
        Retorna -distancia: más cercano a 0 es mejor.
        """
        size = board.size
        heap = []
        distances = [[float('inf')] * size for _ in range(size)]

        # Sembrar desde todo el borde inicial del jugador
        for i in range(size):
            row, col = (i, 0) if player_id == 1 else (0, i)  # player1: col0; player2: fila0
            cell = board.board[row][col]
            if cell == (3 - player_id):  # casilla enemiga en el borde: no podemos empezar aquí
                continue
            cost = 0 if cell == player_id else 1  # propia=gratis, vacía=1 ficha
            distances[row][col] = cost
            heapq.heappush(heap, (cost, row, col))

        visited = [[False] * size for _ in range(size)]

        while heap:
            distance, r, c = heapq.heappop(heap)
            if visited[r][c]:
                continue
            visited[r][c] = True

            # Comprobar si llegamos al borde opuesto
            if (player_id == 1 and c == size - 1) or (player_id == 2 and r == size - 1):
                return -distance

            for dr, dc in self.directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size:
                    cell = board.board[nr][nc]
                    if cell == (3 - player_id):  # casilla enemiga: bloqueada
                        continue
                    cost = 0 if cell == player_id else 1
                    new_dist = distance + cost
                    if new_dist < distances[nr][nc]:
                        distances[nr][nc] = new_dist
                        heapq.heappush(heap, (new_dist, nr, nc))
        return -float('inf')  # Sin camino posible (enemigo ha cortado todos los caminos)

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
