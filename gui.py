import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from sudoku import Sudoku
from genetic_algorithm import GeneticAlgorithm
from config import Config
import threading

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Solucionador de Sudoku - Algoritmos Genéticos")
        self.root.geometry("1400x750")
        
        # Variables
        self.cells = []
        self.sudoku = None
        self.ga = None
        self.is_running = False
        self.is_paused = False
        
        # Colores
        self.color_fixed = "#000000"
        self.color_generated = "#0066CC"
        self.color_bg_fixed = "#E8E8E8"
        self.color_bg_empty = "#FFFFFF"
        
        self.setup_ui()
        self.load_example_sudoku('facil')
        
    def setup_ui(self):
        # Frame principal con grid
        main_frame = tk.Frame(self.root, bg='#F0F0F0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configurar grid weights
        main_frame.grid_columnconfigure(0, weight=0)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # ==================== PANEL IZQUIERDO ====================
        left_frame = tk.Frame(main_frame, bg='#F0F0F0')
        left_frame.grid(row=0, column=0, sticky='n', padx=20)
        
        # Título
        title = tk.Label(left_frame, text="Tablero de Sudoku", 
                        font=('Arial', 16, 'bold'), bg='#F0F0F0')
        title.pack(pady=(0, 15))
        
        # Tablero de Sudoku
        self.board_canvas = tk.Canvas(left_frame, width=460, height=460, 
                                     bg='#000000', highlightthickness=0)
        self.board_canvas.pack()
        
        self.create_board()
        
        # Botones de ejemplos
        examples_frame = tk.LabelFrame(left_frame, text="Sudokus de Ejemplo", 
                                      font=('Arial', 11, 'bold'), bg='#F0F0F0', 
                                      padx=10, pady=10)
        examples_frame.pack(pady=15, fill=tk.X)
        
        btn_frame = tk.Frame(examples_frame, bg='#F0F0F0')
        btn_frame.pack()
        
        tk.Button(btn_frame, text="Fácil", command=lambda: self.load_example_sudoku('facil'),
                 width=10, height=2, bg='#4CAF50', fg='white', 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Medio", command=lambda: self.load_example_sudoku('medio'),
                 width=10, height=2, bg='#FF9800', fg='white', 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Difícil", command=lambda: self.load_example_sudoku('dificil'),
                 width=10, height=2, bg='#F44336', fg='white', 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Button(examples_frame, text="Limpiar Tablero", command=self.clear_board,
                 width=32, height=2, bg='#607D8B', fg='white', 
                 font=('Arial', 10, 'bold')).pack(pady=(10, 0))
        
        # ==================== PANEL DERECHO ====================
        right_frame = tk.Frame(main_frame, bg='#F0F0F0')
        right_frame.grid(row=0, column=1, sticky='nsew', padx=20)
        
        # Parámetros
        params_frame = tk.LabelFrame(right_frame, text="Parámetros del Algoritmo Genético", 
                                     font=('Arial', 12, 'bold'), bg='#F0F0F0', 
                                     padx=20, pady=15)
        params_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Sliders de parámetros
        self.create_param_slider(params_frame, "Tamaño de Población:", 500, 5000, 1500, 'population')
        self.create_param_slider(params_frame, "Tasa de Mutación:", 0.1, 1.0, 0.4, 'mutation', is_float=True)
        self.create_param_slider(params_frame, "Tamaño de Élite:", 5, 50, 15, 'elite')
        
        # Botones de control
        control_frame = tk.LabelFrame(right_frame, text="Control de Ejecución", 
                                      font=('Arial', 12, 'bold'), bg='#F0F0F0', 
                                      padx=20, pady=15)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        buttons_container = tk.Frame(control_frame, bg='#F0F0F0')
        buttons_container.pack()
        
        self.btn_start = tk.Button(buttons_container, text="▶ Iniciar", 
                                   command=self.start_solving,
                                   width=15, height=2, bg='#4CAF50', fg='white', 
                                   font=('Arial', 12, 'bold'))
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        self.btn_pause = tk.Button(buttons_container, text="⏸ Pausar", 
                                   command=self.pause_solving,
                                   width=15, height=2, bg='#FF9800', fg='white', 
                                   font=('Arial', 12, 'bold'), state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = tk.Button(buttons_container, text="⏹ Detener", 
                                  command=self.stop_solving,
                                  width=15, height=2, bg='#F44336', fg='white', 
                                  font=('Arial', 12, 'bold'), state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        # Estadísticas
        stats_frame = tk.LabelFrame(right_frame, text="Estadísticas en Tiempo Real", 
                                    font=('Arial', 12, 'bold'), bg='#F0F0F0', 
                                    padx=20, pady=15)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.generation_var = tk.StringVar(value="Generación: 0")
        self.fitness_var = tk.StringVar(value="Fitness: 0 / 243")
        self.conflicts_var = tk.StringVar(value="Conflictos: 0")
        self.status_var = tk.StringVar(value="Estado: Esperando...")
        
        stats_labels_frame = tk.Frame(stats_frame, bg='#F0F0F0')
        stats_labels_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(stats_labels_frame, textvariable=self.generation_var, 
                font=('Arial', 16, 'bold'), bg='#F0F0F0', fg='#333', 
                anchor='w').pack(fill=tk.X, pady=8)
        tk.Label(stats_labels_frame, textvariable=self.fitness_var, 
                font=('Arial', 16, 'bold'), bg='#F0F0F0', fg='#333', 
                anchor='w').pack(fill=tk.X, pady=8)
        tk.Label(stats_labels_frame, textvariable=self.conflicts_var, 
                font=('Arial', 16, 'bold'), bg='#F0F0F0', fg='#333', 
                anchor='w').pack(fill=tk.X, pady=8)
        
        # Separador
        separator = tk.Frame(stats_labels_frame, height=2, bg='#CCCCCC')
        separator.pack(fill=tk.X, pady=15)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(stats_labels_frame, mode='indeterminate', length=400)
        self.progress.pack(pady=10)
        
        # Estado
        tk.Label(stats_labels_frame, textvariable=self.status_var, 
                font=('Arial', 14, 'bold'), bg='#F0F0F0', fg='#2196F3', 
                anchor='center').pack(fill=tk.X, pady=10)
        
    def create_board(self):
        """Crea el tablero de sudoku con Entry widgets"""
        cell_size = 50
        
        for i in range(9):
            row = []
            for j in range(9):
                # Calcular posición
                x = j * cell_size + (j // 3) * 2
                y = i * cell_size + (i // 3) * 2
                
                # Crear Entry
                entry = tk.Entry(self.board_canvas, font=('Arial', 20, 'bold'), 
                               justify='center', relief=tk.SOLID, bd=1,
                               bg=self.color_bg_empty, width=3)
                
                # Colocar en canvas
                self.board_canvas.create_window(x + cell_size//2, y + cell_size//2, 
                                               window=entry, width=cell_size-2, 
                                               height=cell_size-2)
                
                # Validación de entrada
                entry.bind('<KeyPress>', self.validate_input)
                row.append(entry)
            
            self.cells.append(row)
        
        # Dibujar líneas gruesas para las cajas 3x3
        for i in range(4):
            x = i * 3 * cell_size + i * 2
            self.board_canvas.create_line(x, 0, x, 460, width=3, fill='#000000')
            self.board_canvas.create_line(0, x, 460, x, width=3, fill='#000000')
        
    def create_param_slider(self, parent, label, min_val, max_val, default, var_name, is_float=False):
        frame = tk.Frame(parent, bg='#F0F0F0')
        frame.pack(fill=tk.X, pady=8)
        
        label_widget = tk.Label(frame, text=label, font=('Arial', 11), 
                               bg='#F0F0F0', width=20, anchor='w')
        label_widget.pack(side=tk.LEFT, padx=(0, 10))
        
        if is_float:
            var = tk.DoubleVar(value=default)
            scale = tk.Scale(frame, from_=min_val, to=max_val, resolution=0.1, 
                           orient=tk.HORIZONTAL, variable=var, bg='#F0F0F0', 
                           length=300, font=('Arial', 10))
        else:
            var = tk.IntVar(value=default)
            scale = tk.Scale(frame, from_=min_val, to=max_val, 
                           orient=tk.HORIZONTAL, variable=var, bg='#F0F0F0', 
                           length=300, font=('Arial', 10))
        
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setattr(self, f'{var_name}_var', var)
        
    def validate_input(self, event):
        """Valida la entrada del usuario"""
        if event.char and not event.char.isdigit():
            return 'break'
        if event.char == '0':
            return 'break'
    
    def get_board(self):
        """Obtiene el tablero actual"""
        board = []
        for i in range(9):
            row = []
            for j in range(9):
                val = self.cells[i][j].get().strip()
                row.append(int(val) if val else 0)
            board.append(row)
        return board
    
    def set_board(self, board, fixed_positions=None):
        """Actualiza el tablero visual"""
        for i in range(9):
            for j in range(9):
                self.cells[i][j].config(state='normal')
                self.cells[i][j].delete(0, tk.END)
                
                if board[i][j] != 0:
                    self.cells[i][j].insert(0, str(board[i][j]))
                    
                    if fixed_positions is not None and fixed_positions[i][j]:
                        self.cells[i][j].config(fg=self.color_fixed, 
                                               bg=self.color_bg_fixed,
                                               state='readonly')
                    else:
                        self.cells[i][j].config(fg=self.color_generated, 
                                               bg=self.color_bg_empty)
                else:
                    self.cells[i][j].config(fg='#000000', bg=self.color_bg_empty)
    
    def clear_board(self):
        """Limpia el tablero"""
        if self.is_running:
            messagebox.showwarning("Advertencia", "Detén la ejecución antes de limpiar")
            return
        
        for i in range(9):
            for j in range(9):
                self.cells[i][j].config(state='normal')
                self.cells[i][j].delete(0, tk.END)
                self.cells[i][j].config(bg=self.color_bg_empty, fg='#000000')
        
        self.generation_var.set("Generación: 0")
        self.fitness_var.set("Fitness: 0 / 243")
        self.conflicts_var.set("Conflictos: 0")
        self.status_var.set("Estado: Esperando...")
    
    def load_example_sudoku(self, difficulty):
        """Carga un sudoku de ejemplo"""
        if self.is_running:
            messagebox.showwarning("Advertencia", "Detén la ejecución antes de cargar un ejemplo")
            return
        
        sudokus = {
            'facil': [
                [5,3,0,0,7,0,0,0,0],
                [6,0,0,1,9,5,0,0,0],
                [0,9,8,0,0,0,0,6,0],
                [8,0,0,0,6,0,0,0,3],
                [4,0,0,8,0,3,0,0,1],
                [7,0,0,0,2,0,0,0,6],
                [0,6,0,0,0,0,2,8,0],
                [0,0,0,4,1,9,0,0,5],
                [0,0,0,0,8,0,0,7,9]
            ],
            'medio': [
                [0,0,0,6,0,0,4,0,0],
                [7,0,0,0,0,3,6,0,0],
                [0,0,0,0,9,1,0,8,0],
                [0,0,0,0,0,0,0,0,0],
                [0,5,0,1,8,0,0,0,3],
                [0,0,0,3,0,6,0,4,5],
                [0,4,0,2,0,0,0,6,0],
                [9,0,3,0,0,0,0,0,0],
                [0,2,0,0,0,0,1,0,0]
            ],
            'dificil': [
                [0,0,0,0,0,0,0,1,2],
                [0,0,0,0,3,5,0,0,0],
                [0,0,0,6,0,0,0,7,0],
                [7,0,0,0,0,0,3,0,0],
                [0,0,0,4,0,0,8,0,0],
                [1,0,0,0,0,0,0,0,0],
                [0,0,0,1,2,0,0,0,0],
                [0,8,0,0,0,0,0,4,0],
                [0,5,0,0,0,0,6,0,0]
            ]
        }
        
        board = sudokus[difficulty]
        self.sudoku = Sudoku(board)
        self.set_board(board, self.sudoku.fixed_positions)
        
        self.generation_var.set("Generación: 0")
        self.fitness_var.set("Fitness: 0 / 243")
        self.conflicts_var.set("Conflictos: 0")
        self.status_var.set("Estado: Sudoku cargado")
    
    def start_solving(self):
        """Inicia el proceso de resolución"""
        board = self.get_board()
        
        # Validar que hay números en el tablero
        if all(cell == 0 for row in board for cell in row):
            messagebox.showwarning("Advertencia", "Por favor, ingresa un sudoku válido")
            return
        
        self.sudoku = Sudoku(board)
        self.is_running = True
        self.is_paused = False
        
        # Configurar botones
        self.btn_start.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.NORMAL)
        
        # Iniciar barra de progreso
        self.progress.start(10)
        self.status_var.set("Estado: Buscando solución...")
        
        # Crear configuración con parámetros de la GUI
        config = Config()
        config.POPULATION_SIZE = self.population_var.get()
        config.MUTATION_RATE = self.mutation_var.get()
        config.ELITE_SIZE = self.elite_var.get()
        config.VERBOSE = False
        config.SHOW_EVERY = 10
        
        # Crear AG con callback
        self.ga = GeneticAlgorithm(self.sudoku, config, callback=self.update_callback)
        
        # Ejecutar en thread separado
        thread = threading.Thread(target=self.solve_thread, daemon=True)
        thread.start()
    
    def solve_thread(self):
        """Thread para ejecutar el AG"""
        try:
            solution = self.ga.solve()
            self.root.after(0, self.on_solution_found, solution)
        except Exception as e:
            self.root.after(0, self.on_error, str(e))
    
    def update_callback(self, ga):
        """Callback para actualizar la GUI durante la ejecución"""
        if self.is_paused:
            while self.is_paused and self.is_running:
                import time
                time.sleep(0.1)
        
        if not self.is_running:
            return False
        
        # Actualizar GUI desde el thread principal
        self.root.after(0, self.update_display, ga)
        return True
    
    def update_display(self, ga):
        """Actualiza la visualización del tablero y estadísticas"""
        board = ga.best_individual.board
        conflicts = self.sudoku.count_conflicts(board)
        
        # Actualizar estadísticas
        self.generation_var.set(f"Generación: {ga.generation}")
        self.fitness_var.set(f"Fitness: {ga.best_individual.fitness} / 243")
        self.conflicts_var.set(f"Conflictos: {conflicts}")
        
        # Actualizar tablero
        self.set_board(board, self.sudoku.fixed_positions)
        
        # Forzar actualización
        self.root.update_idletasks()
    
    def pause_solving(self):
        """Pausa/reanuda la ejecución"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.config(text="▶ Continuar", bg='#4CAF50')
            self.status_var.set("Estado: Pausado")
            self.progress.stop()
        else:
            self.btn_pause.config(text="⏸ Pausar", bg='#FF9800')
            self.status_var.set("Estado: Buscando solución...")
            self.progress.start(10)
    
    def stop_solving(self):
        """Detiene la ejecución"""
        self.is_running = False
        self.is_paused = False
        self.progress.stop()
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED, text="⏸ Pausar", bg='#FF9800')
        self.btn_stop.config(state=tk.DISABLED)
        
        self.status_var.set("Estado: Detenido por el usuario")
    
    def on_solution_found(self, solution):
        """Maneja el evento cuando se encuentra una solución"""
        self.is_running = False
        self.progress.stop()
        
        conflicts = self.sudoku.count_conflicts(solution)
        
        if conflicts == 0:
            self.status_var.set("Estado: ¡RESUELTO EXITOSAMENTE! ✓")
            messagebox.showinfo("¡Éxito!", 
                              f"¡Sudoku resuelto exitosamente!\n\n"
                              f"Generaciones: {self.ga.generation}\n"
                              f"Fitness final: {self.ga.best_individual.fitness}/243")
        else:
            self.status_var.set(f"Estado: Solución parcial ({conflicts} conflictos)")
            messagebox.showwarning("Solución parcial", 
                                 f"No se encontró solución completa.\n\n"
                                 f"Conflictos restantes: {conflicts}\n"
                                 f"Generaciones utilizadas: {self.ga.generation}\n"
                                 f"Fitness: {self.ga.best_individual.fitness}/243\n\n"
                                 f"Intenta ajustar los parámetros y volver a ejecutar.")
        
        self.set_board(solution, self.sudoku.fixed_positions)
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)
    
    def on_error(self, error_msg):
        """Maneja errores durante la ejecución"""
        self.is_running = False
        self.progress.stop()
        self.status_var.set("Estado: Error en la ejecución")
        messagebox.showerror("Error", f"Ocurrió un error:\n\n{error_msg}")
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)

def run_gui():
    """Función principal para ejecutar la GUI"""
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()