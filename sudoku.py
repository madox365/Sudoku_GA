<<<<<<< HEAD
import numpy as np
import copy

class Sudoku:
    def __init__(self, board):
        """
        board: matriz 9x9 con el sudoku inicial (0 = celda vacía)
        """
        self.initial_board = np.array(board)
        self.fixed_positions = self.initial_board != 0
        
    def is_valid_number(self, board, row, col, num):
        """Verifica si un número es válido en una posición"""
        # Verificar fila
        if num in board[row]:
            return False
        
        # Verificar columna
        if num in board[:, col]:
            return False
        
        # Verificar subcuadrícula 3x3
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        if num in board[box_row:box_row+3, box_col:box_col+3]:
            return False
        
        return True
    
    def get_possible_values(self, row, col):
        """Retorna valores posibles para una celda"""
        if self.fixed_positions[row, col]:
            return [self.initial_board[row, col]]
        return list(range(1, 10))
    
    def count_conflicts(self, board):
        """
        Función de aptitud: cuenta el número de conflictos
        Menor conflicto = mejor aptitud
        """
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
        """
        Fitness: inverso de los conflictos
        Mayor fitness = mejor solución
        """
        conflicts = self.count_conflicts(board)
        # Fitness máximo es 243 (sin conflictos)
        return 243 - conflicts
    
    def is_solved(self, board):
        """Verifica si el sudoku está resuelto"""
=======
import numpy as np
import copy

class Sudoku:
    def __init__(self, board):
        """
        board: matriz 9x9 con el sudoku inicial (0 = celda vacía)
        """
        self.initial_board = np.array(board)
        self.fixed_positions = self.initial_board != 0
        
    def is_valid_number(self, board, row, col, num):
        """Verifica si un número es válido en una posición"""
        # Verificar fila
        if num in board[row]:
            return False
        
        # Verificar columna
        if num in board[:, col]:
            return False
        
        # Verificar subcuadrícula 3x3
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        if num in board[box_row:box_row+3, box_col:box_col+3]:
            return False
        
        return True
    
    def get_possible_values(self, row, col):
        """Retorna valores posibles para una celda"""
        if self.fixed_positions[row, col]:
            return [self.initial_board[row, col]]
        return list(range(1, 10))
    
    def count_conflicts(self, board):
        """
        Función de aptitud: cuenta el número de conflictos
        Menor conflicto = mejor aptitud
        """
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
        """
        Fitness: inverso de los conflictos
        Mayor fitness = mejor solución
        """
        conflicts = self.count_conflicts(board)
        # Fitness máximo es 243 (sin conflictos)
        return 243 - conflicts
    
    def is_solved(self, board):
        """Verifica si el sudoku está resuelto"""
>>>>>>> 3b62edf0b3027395e8fba07b1daeafff876a00c1
        return self.count_conflicts(board) == 0