from HexBoard import HexBoard
import random
# from copy import deepcopy
class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id  # Tu identificador (1 o 2)

    def play(self, board: HexBoard) -> tuple:
        raise NotImplementedError("¡Implementa este método!")
    
class MyPlayer(Player):
    def __init__(self, player_id, heuristic):
        super().__init__(player_id)
        self.heuristic = heuristic
        
    # def play(self, board: HexBoard) -> tuple:
    #     return self.monte_carlo_heuristic(board, self.player_id)
        
        
    # def play(self, board: HexBoard) -> tuple:
    #     _, best_move = self.minimax(board, self.depth, -float('inf'), float('inf'), self.player_id, True)
    #     if best_move is None and board.get_possible_moves(): #SI best_move es None, significa que siempre pierdo. Solucion: jugar random...
    #         best_move = random.choice(board.get_possible_moves())
    #     if best_move is None:
    #         raise ValueError("No valid moves available.")
    #     return best_move                                                         #'True' porque yo siempre maximizo.
    
    # def minimax(self, board, depth, alpha, beta, player, maximizing_player):
    #     # Casos base: profundidad 0 o juego terminado
    #     winner = self.check_winner()
    #     if depth == 0 or winner is not None:
    #         if winner == self.player_id:# minimax siempre se llama con maximizing_player = True
    #             return float('inf'), None   # Yo siempre maximizo
    #         elif winner == 3 - self.player_id:  # El otro jugador siempre minimiza
    #             return -float('inf'), None
    #         else:
    #             return self.heuristic(board.board, self.player_id), None
        
    #     valid_moves = board.get_possible_moves()
    #     if not valid_moves:
    #         return self.heuristic(board.board, self.player_id), None
        
    #     best_move = None
    #     if maximizing_player:
    #         max_eval = -float('inf')
    #         for move in valid_moves:
    #             row, col = move
    #             game_copy = board.clone()
    #             game_copy.place_piece(row, col, player)
    #             # game_copy.check_connection(player)
                
    #             evaluation, _ = self.minimax(game_copy, depth-1, alpha, beta, (3-player), False)
    #             if evaluation > max_eval:
    #                 max_eval = evaluation
    #                 best_move = move
                
    #             #Yo maximizo, mi padre minimiza
    #             #Si mi alpha es mayor que el beta de mi padre, dejo de buscar
    #             alpha = max(alpha, evaluation)
    #             if beta <= alpha:
    #                 break
    #         return max_eval, best_move
    #     else:
    #         min_eval = float('inf')
    #         for move in valid_moves:
    #             row, col = move
    #             game_copy = board.clone()
    #             game_copy.place_piece(row, col, player)
    #             # game_copy.check_connection(player)
                
    #             evaluation, _ = self.minimax(game_copy, depth-1, alpha, beta, (3-player), True)
    #             if evaluation < min_eval:
    #                 min_eval = evaluation
    #                 best_move = move
                
    #             beta = min(beta, evaluation)
    #             #Yo minimizo, mi padre maximiza
    #             #Si mi beta es menor que el alpha de mi padre, dejo de buscar
    #             if beta <= alpha:
    #                 break
    #         return min_eval, best_move     
        
    def check_winner(board:HexBoard):
        if board.check_connection(1): return 1
        if board.check_connection(2): return 2
        return None
    
    # def monte_carlo_heuristic(board, player_id):
    #     num_simulations = 1000
    #     wins = 0
    #     loses = 0
    #     for _ in range(num_simulations):
    #         board_copy = board.clone()
    #         current_player = player_id
    #         while True:
    #             possible_moves = board_copy.get_possible_moves()
    #             if not possible_moves:
    #                 break
    #             move = random.choice(possible_moves)
    #             row, col = move
    #             board_copy.place_piece(row, col, current_player)
                
    #             if board_copy.check_connection(current_player):
    #                 if current_player == player_id:
    #                     wins += 1
    #                 else:
    #                     loses += 1
    #                 break
    #             current_player = 3 - current_player
    #     return wins - loses
           
    def monte_carlo_heuristic(board, player_id):
        num_simulations = 1000
        best_move = None
        best_score = float('-inf')
        for move in board.get_possible_moves():
            row, col = move
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

    
        