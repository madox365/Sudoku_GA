import matplotlib.pyplot as plt
import numpy as np

def plot_sudoku(board, title="Sudoku", fixed_positions=None):
    """Dibuja un tablero de sudoku"""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 9)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Dibujar cuadrícula
    for i in range(10):
        lw = 3 if i % 3 == 0 else 1
        ax.plot([0, 9], [i, i], 'k-', linewidth=lw)
        ax.plot([i, i], [0, 9], 'k-', linewidth=lw)
    
    # Dibujar números
    for i in range(9):
        for j in range(9):
            num = board[i, j]
            if num != 0:
                color = 'black' if fixed_positions is None or fixed_positions[i, j] else 'blue'
                weight = 'bold' if fixed_positions is None or fixed_positions[i, j] else 'normal'
                ax.text(j + 0.5, 8.5 - i, str(num), 
                       ha='center', va='center', 
                       fontsize=20, color=color, weight=weight)
    
    ax.set_title(title, fontsize=16, weight='bold')
    plt.tight_layout()
    return fig

def plot_evolution(history):
    """Grafica la evolución del fitness"""
    generations = [h['generation'] for h in history]
    fitness = [h['best_fitness'] for h in history]
    conflicts = [h['conflicts'] for h in history]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Fitness
    ax1.plot(generations, fitness, 'b-', linewidth=2)
    ax1.set_xlabel('Generación')
    ax1.set_ylabel('Fitness')
    ax1.set_title('Evolución del Fitness')
    ax1.grid(True, alpha=0.3)
    
    # Conflictos
    ax2.plot(generations, conflicts, 'r-', linewidth=2)
    ax2.set_xlabel('Generación')
    ax2.set_ylabel('Conflictos')
    ax2.set_title('Evolución de Conflictos')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig