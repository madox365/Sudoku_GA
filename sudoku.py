import numpy as np

class Sudoku:
    def __init__(self, board):
        self.initial_board = np.array(board)
        self.fixed_positions = self.initial_board != 0
        
    def count_conflicts(self, board):
        conflicts = 0
        
        # Conflictos en filas
        for row in board:
            conflicts += (9 - len(set(row)))
        
        # Conflictos en columnas
        for col in range(9):
            conflicts += (9 - len(set(board[:, col])))
        
        # Conflictos en subcuadrículas 3x3
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box = board[box_row:box_row+3, box_col:box_col+3].flatten()
                conflicts += (9 - len(set(box)))
        
        return conflicts
    
    def fitness(self, board):
        conflicts = self.count_conflicts(board)
        return 243 - conflicts
    
    def is_solved(self, board):
        return self.count_conflicts(board) == 0