import HexBoard as Game
import Player as AI

def main():
    size = 5
    game = Game.HexBoard(size)
    
    # Configurar jugadores
    player1 = AI.MiniMaxPlayer(1)
    player2 = AI.MonteCarloPlayer(2)
    
    current_player = 1
    moves_history = []
    
    while True:
        print("\033c", end="")  # Limpiar pantalla
        print(f"=== Turno {len(moves_history)+1} ===")
        print_hex_board(game, moves_history)
        
        # Mostrar últimos 3 movimientos
        if moves_history:
            print("\nÚltimos movimientos:")
            for move in moves_history[-3:]:
                print(f"Jugador {move[2]}: ({move[0]}, {move[1]})")
        
        # Obtener movimiento
        player = player1 if current_player == 1 else player2
        row, col = player.play(game)
        
        # Registrar movimiento
        moves_history.append((row, col, current_player))
        game.place_piece(row, col, current_player)
        
        # Verificar ganador
        if game.check_connection(current_player):
            print("\033c", end="")
            print_hex_board(game, moves_history)
            print(f"\n¡Jugador {current_player} gana!")
            print(f"Total de movimientos: {len(moves_history)}")
            break
        
        # Cambiar jugador
        current_player = 2 if current_player == 1 else 1
# def main():
#     game = Game.HexBoard(6)
#     player2 = AI.MiniMaxPlayer(2)
#     player1 = AI.MonteCarloPlayer(1)
#     player = True #True - Player 1, False - Player 2
#     print_hex_board(game)
#     while True:
        
#         if player:
#             print("Player 1's turn")
#             row, col = player1.play(game)
#             game.place_piece(row, col, 1)
#             print_hex_board(game)
#             if game.check_connection(1):
#                 print("Player 1 wins!")
#                 break
#         else:
#             print("Player 2's turn")
#             row, col = player2.play(game)
#             game.place_piece(row, col, 2)
#             print_hex_board(game)
#             if game.check_connection(2):
#                 print("Player 2 wins!")
#                 break
#         player = not player

def print_hex_board(game: Game.HexBoard, moves_history):
    """Imprime el tablero Hex con alineación correcta, conexiones visuales y movimientos realizados."""
    size = game.size
    cell_width = 3

    # Encabezado de columnas
    print(" " * (cell_width + 1), end="")
    for col in range(size):
        print(f"{col:2} ", end="")
    print("\n")

    for row in range(size):
        # Indentación progresiva para efecto hexagonal
        indent = (size - row - 1) * cell_width // 2
        print(" " * indent, end="")
        
        # Número de fila
        print(f"{row:2} ", end="")
        
        # Contenido de la fila
        for col in range(size):
            cell = game.board[row][col]
            if cell == 0:
                symbol = "·"
                color = "\033[90m"  # Gray for empty cells
            elif cell == 1:
                symbol = "X"
                color = "\033[91m"  # Red for Player 1
            else:
                symbol = "O"
                color = "\033[94m"  # Blue for Player 2
            print(f"{color}{symbol}\033[0m", end="")
            if col < size - 1:
                # Check if there's a horizontal connection
                if (row, col, 1) in moves_history and (row, col + 1, 1) in moves_history:
                    print("\033[91m───\033[0m", end="")  # Red connection
                elif (row, col, 2) in moves_history and (row, col + 1, 2) in moves_history:
                    print("\033[94m───\033[0m", end="")  # Blue connection
                else:
                    print("───", end="")
        print()

        # Conexiones inter-filas
        if row < size - 1:
            print(" " * (indent + cell_width // 2 + 1), end="")
            for col in range(size):
                if col < size - 1:
                    # Check diagonal connections
                    if (row, col, 1) in moves_history and (row + 1, col + 1, 1) in moves_history:
                        print("\033[91m╲   ╱\033[0m", end="")  # Red diagonal connection
                    elif (row, col, 2) in moves_history and (row + 1, col + 1, 2) in moves_history:
                        print("\033[94m╲   ╱\033[0m", end="")  # Blue diagonal connection
                    else:
                        print("╲   ╱", end="")
                else:
                    if (row, col, 1) in moves_history and (row + 1, col, 1) in moves_history:
                        print("\033[91m╲\033[0m", end="")  # Red vertical connection
                    elif (row, col, 2) in moves_history and (row + 1, col, 2) in moves_history:
                        print("\033[94m╲\033[0m", end="")  # Blue vertical connection
                    else:
                        print("╲", end="")
            print()
# def print_hex_board(game: Game.HexBoard):
#     """Imprime el tablero Hex con alineación correcta y conexiones visuales."""
#     size = game.size
#     cell_width = 3
#     line_width = size * cell_width + (size - 1)
    
#     # Encabezado de columnas
#     print(" " * (cell_width + 1), end="")
#     for col in range(size):
#         print(f"{col:2} ", end="")
#     print("\n")

#     for row in range(size):
#         # Indentación progresiva para efecto hexagonal
#         indent = (size - row - 1) * cell_width // 2
#         print(" " * indent, end="")
        
#         # Número de fila
#         print(f"{row:2} ", end="")
        
#         # Contenido de la fila
#         for col in range(size):
#             cell = game.board[row][col]
#             if cell == 0:
#                 symbol = "·"
#                 color = "\033[90m"
#             elif cell == 1:
#                 symbol = "X"
#                 color = "\033[91m"
#             else:
#                 symbol = "O"
#                 color = "\033[94m"
#             print(f"{color}{symbol}\033[0m", end="")
#             if col < size - 1:
#                 print("───", end="")
#         print()

#         # Conexiones inter-filas
#         if row < size - 1:
#             print(" " * (indent + cell_width // 2 + 1), end="")
#             for _ in range(size):
#                 if row % 2 == 0:
#                     print("╲   ╱", end="") if _ < size - 1 else print("╲")
#                 else:
#                     print("╱   ╲", end="") if _ < size - 1 else print("╱")
#             print()


# def print_hex_board(game:Game):
#     """Imprime el tablero de hexágonos."""
#     for i in range(game.size): 
#         # Q no se printe en diagonal
#         if i % 2 == 0:
#             print(" " , end="")
#         else:
#             print(" " * 3, end="")
#         for j in range(game.size):
#             if game.board[i][j] == 0:
#                 print(" . ", end="")
#             elif game.board[i][j] == 1:
#                 #SI es jugador 1, imprimir circulo rojo
#                 # print(" X ", end="")
#                 print(" \033[31mX\033[0m ", end="")
#             else:
#                 # print(" O ", end="")
#                 print(" \033[34mO\033[0m ", end="")
#         print()

    
if __name__ == "__main__":
    main()