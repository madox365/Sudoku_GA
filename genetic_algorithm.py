import numpy as np
import random
from config import Config

class Individual:
    def __init__(self, board, sudoku):
        self.board = board
        self.sudoku = sudoku
        self.fitness = sudoku.fitness(board)
    
    def __lt__(self, other):
        return self.fitness > other.fitness

class GeneticAlgorithm:
    def __init__(self, sudoku, config=Config(), callback=None):
        self.sudoku = sudoku
        self.config = config
        self.population = []
        self.best_individual = None
        self.generation = 0
        self.history = []
        self.callback = callback
        self.stagnation_counter = 0
        self.best_fitness_ever = 0
        
    def initialize_population(self):
        """Inicialización mejorada con diversidad"""
        self.population = []
        
        for _ in range(self.config.POPULATION_SIZE):
            board = np.copy(self.sudoku.initial_board)
            
            for row in range(9):
                fixed_nums = board[row][board[row] != 0].tolist()
                missing = [n for n in range(1, 10) if n not in fixed_nums]
                random.shuffle(missing)
                
                idx = 0
                for col in range(9):
                    if board[row, col] == 0:
                        board[row, col] = missing[idx]
                        idx += 1
            
            individual = Individual(board, self.sudoku)
            self.population.append(individual)
        
        self.population.sort()
        self.best_individual = self.population[0]
        self.best_fitness_ever = self.best_individual.fitness
    
    def tournament_selection(self):
        """Selección por torneo"""
        tournament = random.sample(self.population, self.config.TOURNAMENT_SIZE)
        return min(tournament)
    
    def crossover(self, parent1, parent2):
        """Cruce mejorado - intercambio de filas"""
        child_board = np.copy(parent1.board)
        rows_to_swap = random.sample(range(9), random.randint(2, 5))
        
        for row in rows_to_swap:
            child_board[row] = parent2.board[row]
        
        return Individual(child_board, self.sudoku)
    
    def mutate(self, individual):
        """Mutación mejorada - múltiples estrategias"""
        if random.random() > self.config.MUTATION_RATE:
            return individual
        
        board = np.copy(individual.board)
        
        # Estrategia 1: Swap en fila aleatoria (70%)
        if random.random() < 0.7:
            row = random.randint(0, 8)
            non_fixed = [col for col in range(9) if not self.sudoku.fixed_positions[row, col]]
            
            if len(non_fixed) >= 2:
                col1, col2 = random.sample(non_fixed, 2)
                board[row, col1], board[row, col2] = board[row, col2], board[row, col1]
        
        # Estrategia 2: Swap entre dos filas (20%)
        elif random.random() < 0.9:
            row1, row2 = random.sample(range(9), 2)
            # Solo swap en columnas no fijas de ambas filas
            for col in range(9):
                if not self.sudoku.fixed_positions[row1, col] and not self.sudoku.fixed_positions[row2, col]:
                    if random.random() < 0.3:
                        board[row1, col], board[row2, col] = board[row2, col], board[row1, col]
        
        # Estrategia 3: Reordenar fila completa (10%)
        else:
            row = random.randint(0, 8)
            non_fixed_cols = [col for col in range(9) if not self.sudoku.fixed_positions[row, col]]
            if len(non_fixed_cols) > 1:
                values = [board[row, col] for col in non_fixed_cols]
                random.shuffle(values)
                for i, col in enumerate(non_fixed_cols):
                    board[row, col] = values[i]
        
        return Individual(board, self.sudoku)
    
    def adaptive_mutation(self):
        """Ajusta la tasa de mutación basado en estancamiento"""
        if self.stagnation_counter > 50:
            # Aumentar mutación para escapar de óptimo local
            return min(0.8, self.config.MUTATION_RATE * 1.5)
        elif self.stagnation_counter > 100:
            # Mutación muy alta para resetear búsqueda
            return 0.9
        return self.config.MUTATION_RATE
    
    def evolve(self):
        """Evolución con mutación adaptativa"""
        new_population = []
        elite = self.population[:self.config.ELITE_SIZE]
        new_population.extend(elite)
        
        # Mutación adaptativa
        original_mutation = self.config.MUTATION_RATE
        self.config.MUTATION_RATE = self.adaptive_mutation()
        
        while len(new_population) < self.config.POPULATION_SIZE:
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)
        
        # Restaurar tasa de mutación original
        self.config.MUTATION_RATE = original_mutation
        
        self.population = new_population
        self.population.sort()
        self.best_individual = self.population[0]
        self.generation += 1
        
        # Detectar estancamiento
        if self.best_individual.fitness > self.best_fitness_ever:
            self.best_fitness_ever = self.best_individual.fitness
            self.stagnation_counter = 0
        else:
            self.stagnation_counter += 1
        
        # Si hay mucho estancamiento, inyectar diversidad
        if self.stagnation_counter > 150:
            self.inject_diversity()
            self.stagnation_counter = 0
        
        self.history.append({
            'generation': self.generation,
            'best_fitness': self.best_individual.fitness,
            'conflicts': self.sudoku.count_conflicts(self.best_individual.board)
        })
        
        return self.best_individual
    
    def inject_diversity(self):
        """Inyecta nuevos individuos aleatorios para escapar de óptimo local"""
        # Mantener la élite
        elite_size = self.config.ELITE_SIZE * 2
        elite = self.population[:elite_size]
        
        # Generar nuevos individuos aleatorios
        new_individuals = []
        for _ in range(self.config.POPULATION_SIZE - elite_size):
            board = np.copy(self.sudoku.initial_board)
            
            for row in range(9):
                fixed_nums = board[row][board[row] != 0].tolist()
                missing = [n for n in range(1, 10) if n not in fixed_nums]
                random.shuffle(missing)
                
                idx = 0
                for col in range(9):
                    if board[row, col] == 0:
                        board[row, col] = missing[idx]
                        idx += 1
            
            individual = Individual(board, self.sudoku)
            new_individuals.append(individual)
        
        self.population = elite + new_individuals
        self.population.sort()
    
    def solve(self):
        """Ejecuta el algoritmo genético hasta encontrar solución"""
        self.initialize_population()
        
        if self.config.VERBOSE:
            print(f"Generación 0: Fitness = {self.best_individual.fitness}, Conflictos = {self.sudoku.count_conflicts(self.best_individual.board)}")
        
        for gen in range(self.config.GENERATIONS):
            best = self.evolve()
            
            # Callback para visualización en tiempo real
            if self.callback and gen % self.config.SHOW_EVERY == 0:
                should_continue = self.callback(self)
                if not should_continue:
                    break
            
            if self.config.VERBOSE and gen % self.config.SHOW_EVERY == 0:
                conflicts = self.sudoku.count_conflicts(best.board)
                print(f"Generación {self.generation}: Fitness = {best.fitness}, Conflictos = {conflicts}, Estancamiento = {self.stagnation_counter}")
            
            if self.sudoku.is_solved(best.board):
                if self.config.VERBOSE:
                    print(f"\n¡Sudoku resuelto en la generación {self.generation}!")
                if self.callback:
                    self.callback(self)
                return best.board
        
        if self.config.VERBOSE:
            print(f"\nNo se encontró solución completa. Mejor fitness: {self.best_individual.fitness}")
        
        return self.best_individual.board