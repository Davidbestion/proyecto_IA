
adj = [
            (0, -1),   # Izquierda
            (0, 1),    # Derecha
            (-1, 0),   # Arriba
            (1, 0),    # Abajo
            (-1, 1),   # Arriba derecha
            (1, -1)    # Abajo izquierda
        ]

def dfs(g,player_id,size):
    visited = set()
    p = {}
    for u in g:
        if u[2 - player_id] != 0:  # player1 usa columna (izq->der), player2 usa fila (arr->abajo)
            continue
        if u not in visited:
            p[(u[0],u[1])] = None
            if dfs_visit(g,u,visited,p,size,player_id):
                return True
    return False

# Eda xd
def dfs_visit(g,u,visited,p,size,player_id):
    visited.add((u))
    for dir in adj:
        v = (u[0]+dir[0],u[1]+dir[1])
        if v not in g:
            continue
        if v[2 - player_id] == size - 1:  # player1: col N-1; player2: fila N-1
            p[v] = u
            return True
        if v not in visited:
            p[v] = u
            if dfs_visit(g,v,visited,p,size,player_id):
                return True
    return False