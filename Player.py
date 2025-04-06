from HexBoard import HexBoard
import random
import heapq
# from copy import deepcopy
class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id  # Tu identificador (1 o 2)

    def play(self, board: HexBoard) -> tuple:
        raise NotImplementedError("¡Implementa este método!")
    
class MonteCarloPlayer(Player):
    def __init__(self, player_id, heuristic=None):
        super().__init__(player_id)
        self.heuristic = self.monte_carlo_heuristic if heuristic is None else heuristic
        
    def play(self, board: HexBoard) -> tuple:
        return self.monte_carlo_heuristic(board, self.player_id)   
           
    def monte_carlo_heuristic(self, board, player_id):
        num_simulations = 1000
        best_move = None
        best_score = float('-inf')
        for move in board.get_possible_moves():
            row, col = move
            current_player = player_id
            for _ in range(num_simulations):
                board_copy = board.clone()
                board_copy.place_piece(row, col, current_player)
                current_player = 3 - player_id
                wins = 0
                if board_copy.check_connection(current_player) and current_player == player_id:
                    wins += 1
                    
                while True:
                    possible_moves = board_copy.get_possible_moves()
                    if not possible_moves:
                        break
                    move = random.choice(possible_moves)
                    row, col = move
                    board_copy.place_piece(row, col, current_player)
                    
                    if board_copy.check_connection(current_player) and current_player == player_id:
                        wins += 1
                        break
                    
                    current_player = 3 - current_player
            score = wins / num_simulations
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move

class MiniMaxPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)
    
    def play(self, board: HexBoard, depth = 6) -> tuple:
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
                return self.heuristic(board, self.player_id), None
        
        valid_moves = board.get_possible_moves()
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
        if board.check_connection(1): return 1
        if board.check_connection(2): return 2
        return None
    
    def heuristic(self, board, player_id):
        """Busca la distancia mas corta usando Dijkstra"""
        size = board.size
        heap = []
        distances = [[float('inf')] * size for _ in range(size)]
        for row in range(size):
            for col in range(size):
                if board.board[row][col] == (3 - player_id):
                    distances[row][col] = -1
        visited = [[False] * size for _ in range(size)]
        
        if player_id == 1:
            for row in range(size):
                if board.board[row][0] == player_id:
                    heapq.heappush(heap, (0, row, 0))
                    distances[row][0] = 0
        else:
            for col in range(size):
                if board.board[0][col] == player_id:
                    heapq.heappush(heap, (0, 0, col))
                    distances[0][col] = 0
        
        directions_fila_par = [
            (-1, 0),  # Arriba
            (1, 0),   # Abajo
            (0, -1),  # Izquierda
            (0, 1),   # Derecha
            (-1, 1),  # Arriba-Derecha
            (1, 1)    # Abajo-Derecha
        ]
        directions_fila_impar = [
            (-1, 0),  # Arriba
            (1, 0),   # Abajo
            (0, -1),  # Izquierda
            (0, 1),   # Derecha
            (-1, -1), # Arriba-Izquierda
            (1, -1)   # Abajo-Izquierda
        ]
        
        while heap:
            distance, r, c = heapq.heappop(heap)
            if visited[r][c]:
                continue
            visited[r][c] = True
            
            if player_id == 1 and c == size - 1 or player_id == 2 and r == size - 1:
                return -distance
            
            directions = directions_fila_par if r % 2 == 0 else directions_fila_impar
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size and distances[nr][nc] != -1:
                    cost = 0 if board.board[nr][nc] == player_id else 1
                    new_dist = distance + cost
                    if new_dist < distances[nr][nc]:
                        distances[nr][nc] = new_dist
                        heapq.heappush(heap, (new_dist, nr, nc))
        return -float('inf')
    
    # def heuristic(self, board, player_id):
    #     initials = []
    #     finals = []
    #     if player_id == 1:
    #         for row in range(board.size):
    #             initials.append((row, 0))
    #             finals.append((row, board.size - 1))
    #     else:
    #         for col in range(board.size):
    #             initials.append((0, col))
    #             finals.append((board.size - 1, col))
    #     return self.bfs(board, player_id, initials, finals)
            
    # def bfs(self, board, player_id, initials: list[tuple], finals: list[tuple]):
    #     stack = []
    #     # mask = [[-float('inf') for _ in range(board.size)] for _ in range(board.size)]
    #     for element in initials:
    #         # mask[element[0]][element[1]] = 0
    #         stack.append((element, 0))
    #     visited = set()
    #     visited.update(initials)
    #     max_distance = 0
    #     end = False
    #     while stack:
    #         ((r, c), distance) = stack.pop(0)
    #         if r % 2 == 0:
    #             directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1)]
    #         else:
    #             directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1)]
    #         for dr, dc in directions:
    #             nr, nc = r + dr, c + dc
    #             if self.is_in_bounds(board, nr, nc) and not (nr, nc) in visited:
    #                 if board.board[nr][nc] == 0:
    #                     # if mask[nr][nc] != -float('inf'): 
    #                     #     mask[nr][nc] = min(mask[nr][nc], distance + 1)
    #                     #     continue
    #                     # mask[nr][nc] = distance
    #                     stack.append(((nr, nc), distance + 1))
    #                     visited.add((nr, nc))
    #                     if (nr, nc) in finals:
    #                         max_distance = max(max_distance, distance + 1)
    #                         end = True
    #                         break
    #                 if board.board[nr][nc] == player_id:
    #                     stack.append(((nr, nc), distance + 1))
    #                     visited.add((nr, nc))
    #                     if (nr, nc) in finals:
    #                         max_distance = max(max_distance, distance + 1)
    #                         end = True
    #                         break
    #                     #tirar dfs por las casillas de mi color, visitarlas y agragarlas al stack
    #                     self.dfs(board, player_id, (nr, nc), stack, visited, distance + 1)
    #                     for element in visited:
    #                         if element in finals:
    #                             max_distance = max(max_distance, distance + 1)
    #                             end = True
    #                             break
    #         if end:
    #             break
    #     return max_distance   
    #     #return max distance in stack

    # def dfs(self, board, player_id, move, bfs_stack, visited, distance):
    #     stack = []
    #     stack.append(move)
    #     visited.add(move)
    #     while stack:
    #         r, c = stack.pop()
    #         if r % 2 == 0:
    #             directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1)]
    #         else:
    #             directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1)]
    #         for dr, dc in directions:
    #             nr, nc = r + dr, c + dc
    #             if self.is_in_bounds(board, nr, nc) and not (nr, nc) in visited:
    #                 if board.board[nr][nc] == player_id:
    #                     stack.append((nr, nc))
    #                     bfs_stack.append(((nr, nc), distance))
    #                     visited.add((nr, nc))
                        
    # def is_in_bounds(self, board, r, c):
    #     return 0 <= r < board.size and 0 <= c < board.size