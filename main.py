from sudoku import Sudoku
from genetic_algorithm import GeneticAlgorithm
from visualization import plot_sudoku, plot_evolution
from config import Config
import matplotlib.pyplot as plt

def main():
    # Sudoku de ejemplo (dificultad media)
    initial_board = [
        [5,3,0,0,7,0,0,0,0],
        [6,0,0,1,9,5,0,0,0],
        [0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],
        [4,0,0,8,0,3,0,0,1],
        [7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],
        [0,0,0,4,1,9,0,0,5],
        [0,0,0,0,8,0,0,7,9]
    ]
    
    print("=" * 50)
    print("SOLUCIONADOR DE SUDOKU CON ALGORITMOS GENÉTICOS")
    print("=" * 50)
    print()
    
    # Crear instancia de Sudoku
    sudoku = Sudoku(initial_board)
    
    # Visualizar sudoku inicial
    print("Sudoku inicial:")
    fig1 = plot_sudoku(sudoku.initial_board, "Sudoku Inicial", sudoku.fixed_positions)
    plt.show()
    
    # Configuración del AG
    config = Config()
    print(f"\nParámetros del Algoritmo Genético:")
    print(f"  - Tamaño de población: {config.POPULATION_SIZE}")
    print(f"  - Generaciones máximas: {config.GENERATIONS}")
    print(f"  - Tasa de mutación: {config.MUTATION_RATE}")
    print(f"  - Tamaño de élite: {config.ELITE_SIZE}")
    print(f"  - Tamaño de torneo: {config.TOURNAMENT_SIZE}")
    print()
    
    # Crear y ejecutar AG
    ga = GeneticAlgorithm(sudoku, config)
    solution = ga.solve()
    
    # Visualizar solución
    print("\nSolución encontrada:")
    fig2 = plot_sudoku(solution, "Solución", sudoku.fixed_positions)
    plt.show()
    
    # Visualizar evolución
    if ga.history:
        fig3 = plot_evolution(ga.history)
        plt.show()
    
    # Verificar solución
    conflicts = sudoku.count_conflicts(solution)
    if conflicts == 0:
        print("\n✓ ¡Solución válida encontrada!")
    else:
        print(f"\n✗ Solución con {conflicts} conflictos")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()