import copy
class HexBoard:
    def __init__(self, size: int):
        self.size = size  # Tamaño N del tablero (NxN)
        self.board = [[0 for _ in range(size)] for _ in range(size)]  # Matriz NxN (0=vacío, 1=Jugador1, 2=Jugador2)

    def clone(self) -> "HexBoard":
        """Devuelve una copia del tablero actual"""
        return copy.deepcopy(self)
        # return HexBoard(self.size, [row[:] for row in self.board])

    def place_piece(self, row: int, col: int, player_id: int) -> bool:#0 - vacias, 1 - jugador 1, 2 - jugador 2
        """Coloca una ficha si la casilla está vacía."""
        if self.board[row][col] == 0:
            self.board[row][col] = player_id
            return True
        return False

    def get_possible_moves(self) -> list:
        """Devuelve todas las casillas vacías como tuplas (fila, columna)."""
        return [(row, col) for row in range(self.size) for col in range(self.size) if self.board[row][col] == 0]
    
    def check_connection(self, player_id: int) -> bool:
        """Verifica si el jugador ha conectado sus dos lados usando BFS."""
        from collections import deque

        visited = set()
        queue = deque()
        size = self.size

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

        # Inicialización según jugador
        if player_id == 1:
            # Jugador 1: busca conectar izquierda (col 0) a derecha (col size-1)
            start_nodes = [(row, 0) for row in range(size) if self.board[row][0] == 1]
            target = lambda r, c: c == size - 1
        else:
            # Jugador 2: busca conectar arriba (fila 0) a abajo (fila size-1)
            start_nodes = [(0, col) for col in range(size) if self.board[0][col] == 2]
            target = lambda r, c: r == size - 1

        # BFS desde todos los nodos iniciales
        for node in start_nodes:
            if node in visited:
                continue
            queue.clear()
            queue.append(node)
            visited.add(node)
            
            while queue:
                r, c = queue.popleft()
                
                # Verificar si llegamos al lado objetivo
                if target(r, c):
                    return True
                
                if r % 2 == 0:
                    directions = directions_fila_par
                else:
                    directions = directions_fila_impar
                    
                # Explorar vecinos
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size:
                        if (nr, nc) not in visited and self.board[nr][nc] == player_id:
                            visited.add((nr, nc))
                            queue.append((nr, nc))
        
        return False
    # def check_connection(self, player_id: int) -> bool:
    #     """Verifica si el jugador ha conectado sus dos lados."""
    #     directions_fila_par = [
    #         (-1, 0),  # Arriba
    #         (1, 0),   # Abajo
    #         (0, -1),  # Izquierda
    #         (0, 1),   # Derecha
    #         (-1, 1),  # Arriba-Derecha
    #         (1, 1)    # Abajo-Derecha
    #     ]
    #     directions_fila_impar = [
    #         (-1, 0),  # Arriba
    #         (1, 0),   # Abajo
    #         (0, -1),  # Izquierda
    #         (0, 1),   # Derecha
    #         (-1, -1), # Arriba-Izquierda
    #         (1, -1)   # Abajo-Izquierda
    #     ]
    #     visited = set()
    #     stack = []
        
    #     if player_id == 1:
    #         #Buscar en col 0
    #         for row in range(self.size):
    #             if self.board[row][0] == player_id and (row, 0) not in visited:
    #                 stack.append((row, 0))
    #                 visited.add((row, 0))
    #     if player_id == 2:
    #         #Buscar en fila 0
    #         for col in range(self.size):
    #             if self.board[0][col] == player_id and (0, col) not in visited:
    #                 stack.append((0, col))
    #                 visited.add((0, col))
    #     #DFS para verificar si hay conexión
        
            
    #     def dfs(board, r, c):
    #         #DFS para verificar si hay conexión
    #         if player_id == 1 and c == self.size - 1:
    #             return True
    #         if player_id == 2 and r == self.size - 1:
    #             return True
            
    #         # Verifica los vecinos
    #         if r % 2 == 0:
    #             directions = directions_fila_par
    #         else:
    #             directions = directions_fila_impar
    #         stack = [(r, c)]
    #         visited.add((r, c))
    #         while stack:
    #             r, c = stack.pop()
                
    #             if r % 2 == 0:
    #                 directions = directions_fila_par
    #             else:
    #                 directions = directions_fila_impar
                    
    #             for dr, dc in directions:
    #                 nr, nc = r + dr, c + dc
    #                 if is_in_bounds(nr, nc) and (nr, nc) not in visited and self.board[nr][nc] == player_id:
    #                     if board[nr][nc] == player_id:
    #                         stack.append((nr, nc))
    #                         visited.add((nr, nc))
    #                         if player_id == 1 and nc == self.size - 1:
    #                             return True
    #                         if player_id == 2 and nr == self.size - 1:
    #                             return True
    #                     # if player_id == 1 and nc == self.size - 1:
    #                     #     return True
    #                     # if player_id == 2 and nr == self.size - 1:
    #                     #     return True
    #                     # stack.append((nr, nc))
    #                     # visited.add((nr, nc))
    #         return False
                        
    #     def is_in_bounds(r, c):
    #         return 0 <= r < self.size and 0 <= c < self.size
        
    #     while stack:
    #         r, c = stack.pop()
    #         if dfs(self.board, r, c):
    #             return True
    #     return False

        
