import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

class RealtimeVisualizer:
    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.fig = plt.figure(figsize=(14, 6))
        
        # Subplot para el tablero
        self.ax_board = self.fig.add_subplot(121)
        self.ax_board.set_xlim(0, 9)
        self.ax_board.set_ylim(0, 9)
        self.ax_board.set_aspect('equal')
        self.ax_board.axis('off')
        
        # Subplot para las gráficas
        self.ax_stats = self.fig.add_subplot(122)
        
        self.generations = []
        self.fitness_vals = []
        self.conflicts_vals = []
        
        self.draw_grid()
        self.text_objects = []
        self.init_text_objects()
        
        plt.ion()
        plt.show()
    
    def draw_grid(self):
        for i in range(10):
            lw = 3 if i % 3 == 0 else 1
            self.ax_board.plot([0, 9], [i, i], 'k-', linewidth=lw)
            self.ax_board.plot([i, i], [0, 9], 'k-', linewidth=lw)
    
    def init_text_objects(self):
        self.text_objects = []
        for i in range(9):
            row_texts = []
            for j in range(9):
                text = self.ax_board.text(j + 0.5, 8.5 - i, '', 
                                         ha='center', va='center', 
                                         fontsize=18)
                row_texts.append(text)
            self.text_objects.append(row_texts)
    
    def update(self, ga):
        board = ga.best_individual.board
        
        # Actualizar tablero
        for i in range(9):
            for j in range(9):
                num = board[i, j]
                if num != 0:
                    is_fixed = self.sudoku.fixed_positions[i, j]
                    color = 'black' if is_fixed else 'blue'
                    weight = 'bold' if is_fixed else 'normal'
                    self.text_objects[i][j].set_text(str(num))
                    self.text_objects[i][j].set_color(color)
                    self.text_objects[i][j].set_weight(weight)
        
        # Actualizar gráficas
        self.generations.append(ga.generation)
        self.fitness_vals.append(ga.best_individual.fitness)
        self.conflicts_vals.append(self.sudoku.count_conflicts(board))
        
        self.ax_stats.clear()
        self.ax_stats.plot(self.generations, self.conflicts_vals, 'r-', linewidth=2, label='Conflictos')
        self.ax_stats.set_xlabel('Generación', fontsize=12)
        self.ax_stats.set_ylabel('Conflictos', fontsize=12)
        self.ax_stats.set_title(f'Gen: {ga.generation} | Fitness: {ga.best_individual.fitness} | Conflictos: {self.conflicts_vals[-1]}', 
                               fontsize=12, weight='bold')
        self.ax_stats.grid(True, alpha=0.3)
        self.ax_stats.legend()
        
        plt.pause(0.001)
        
        return True  # Continuar ejecución

def plot_final_results(sudoku, solution, history):
    """Grafica resultados finales"""
    fig = plt.figure(figsize=(15, 5))
    
    # Sudoku inicial
    ax1 = fig.add_subplot(131)
    plot_static_sudoku(ax1, sudoku.initial_board, "Sudoku Inicial", sudoku.fixed_positions)
    
    # Solución
    ax2 = fig.add_subplot(132)
    plot_static_sudoku(ax2, solution, "Solución", sudoku.fixed_positions)
    
    # Evolución
    ax3 = fig.add_subplot(133)
    generations = [h['generation'] for h in history]
    conflicts = [h['conflicts'] for h in history]
    ax3.plot(generations, conflicts, 'r-', linewidth=2)
    ax3.set_xlabel('Generación')
    ax3.set_ylabel('Conflictos')
    ax3.set_title('Evolución de Conflictos')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_static_sudoku(ax, board, title, fixed_positions=None):
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 9)
    ax.set_aspect('equal')
    ax.axis('off')
    
    for i in range(10):
        lw = 3 if i % 3 == 0 else 1
        ax.plot([0, 9], [i, i], 'k-', linewidth=lw)
        ax.plot([i, i], [0, 9], 'k-', linewidth=lw)
    
    for i in range(9):
        for j in range(9):
            num = board[i, j]
            if num != 0:
                color = 'black' if fixed_positions is None or fixed_positions[i, j] else 'blue'
                weight = 'bold' if fixed_positions is None or fixed_positions[i, j] else 'normal'
                ax.text(j + 0.5, 8.5 - i, str(num), 
                       ha='center', va='center', 
                       fontsize=16, color=color, weight=weight)
    
    ax.set_title(title, fontsize=14, weight='bold')