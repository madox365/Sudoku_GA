import numpy as np
import random
from config import Config

class Individual:
    def __init__(self, board, sudoku):
        self.board = board
        self.sudoku = sudoku
        self.fitness = sudoku.fitness(board)
    
    def __lt__(self, other):
        return self.fitness > other.fitness  # Mayor fitness es mejor

class GeneticAlgorithm:
    def __init__(self, sudoku, config=Config()):
        self.sudoku = sudoku
        self.config = config
        self.population = []
        self.best_individual = None
        self.generation = 0
        self.history = []
        
    def initialize_population(self):
        """Inicializa la población con individuos aleatorios válidos por fila"""
        self.population = []
        
        for _ in range(self.config.POPULATION_SIZE):
            board = np.copy(self.sudoku.initial_board)
            
            # Para cada fila, llenar con números faltantes
            for row in range(9):
                # Obtener números ya presentes en la fila
                fixed_nums = board[row][board[row] != 0].tolist()
                # Números faltantes
                missing = [n for n in range(1, 10) if n not in fixed_nums]
                random.shuffle(missing)
                
                # Llenar celdas vacías
                idx = 0
                for col in range(9):
                    if board[row, col] == 0:
                        board[row, col] = missing[idx]
                        idx += 1
            
            individual = Individual(board, self.sudoku)
            self.population.append(individual)
        
        self.population.sort()
        self.best_individual = self.population[0]
    
    def tournament_selection(self):
        """Selección por torneo"""
        tournament = random.sample(self.population, self.config.TOURNAMENT_SIZE)
        return min(tournament)  # El de mayor fitness (menor en __lt__)
    
    def crossover(self, parent1, parent2):
        """
        Cruce: intercambia filas completas entre padres
        preservando la validez de cada fila
        """
        child_board = np.copy(parent1.board)
        
        # Seleccionar filas aleatorias del padre 2
        rows_to_swap = random.sample(range(9), random.randint(2, 5))
        
        for row in rows_to_swap:
            child_board[row] = parent2.board[row]
        
        return Individual(child_board, self.sudoku)
    
    def mutate(self, individual):
        """
        Mutación: intercambia dos valores no fijos en una fila aleatoria
        """
        if random.random() > self.config.MUTATION_RATE:
            return individual
        
        board = np.copy(individual.board)
        
        # Seleccionar una fila aleatoria
        row = random.randint(0, 8)
        
        # Encontrar posiciones no fijas en esa fila
        non_fixed = [col for col in range(9) if not self.sudoku.fixed_positions[row, col]]
        
        if len(non_fixed) >= 2:
            # Intercambiar dos valores
            col1, col2 = random.sample(non_fixed, 2)
            board[row, col1], board[row, col2] = board[row, col2], board[row, col1]
        
        return Individual(board, self.sudoku)
    
    def evolve(self):
        """Ejecuta una generación del algoritmo genético"""
        new_population = []
        
        # Elitismo: mantener los mejores individuos
        elite = self.population[:self.config.ELITE_SIZE]
        new_population.extend(elite)
        
        # Generar nueva población
        while len(new_population) < self.config.POPULATION_SIZE:
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            
            new_population.append(child)
        
        self.population = new_population
        self.population.sort()
        self.best_individual = self.population[0]
        self.generation += 1
        
        # Guardar histórico
        self.history.append({
            'generation': self.generation,
            'best_fitness': self.best_individual.fitness,
            'conflicts': self.sudoku.count_conflicts(self.best_individual.board)
        })
        
        return self.best_individual
    
    def solve(self):
        """Ejecuta el algoritmo genético hasta encontrar solución"""
        self.initialize_population()
        
        if self.config.VERBOSE:
            print(f"Generación 0: Fitness = {self.best_individual.fitness}, Conflictos = {self.sudoku.count_conflicts(self.best_individual.board)}")
        
        for gen in range(self.config.GENERATIONS):
            best = self.evolve()
            
            if self.config.VERBOSE and gen % self.config.SHOW_EVERY == 0:
                conflicts = self.sudoku.count_conflicts(best.board)
                print(f"Generación {self.generation}: Fitness = {best.fitness}, Conflictos = {conflicts}")
            
            # Si encontramos la solución, terminar
            if self.sudoku.is_solved(best.board):
                if self.config.VERBOSE:
                    print(f"\n¡Sudoku resuelto en la generación {self.generation}!")
                return best.board
        
        if self.config.VERBOSE:
            print(f"\nNo se encontró solución completa. Mejor fitness: {self.best_individual.fitness}")
        
        return self.best_individual.board
