import kivy.app
import kivy.uix.gridlayout
import kivy.uix.boxlayout
import kivy.uix.button
import kivy.uix.textinput
import kivy.uix.label
import kivy.graphics
import numpy
import genAlg

class Queens8App(kivy.app.App):
    pop_created = False

    def start_ga(self, *args):
        """
        Initializes the genetic algorithm process, iterating through generations to optimize the 
        population_board. Stops when the best solution is found or the maximum number of generations is reached.
        Saves the best solutions to files and updates the UI with the best solution.
        """
        self.initialize_population()
        best_outputs = []
        best_outputs_fitness = []
        if self.pop_created == False:
            return

        num_generations = numpy.uint16(self.num_generations_TextInput.text)
        num_parents = numpy.uint8(self.num_solutions / 2)

        for generation in range(num_generations):
            print("\n##  Generation = ", generation, "  ##\n")

            population_fitness, total_num_attacks = self.fitness(self.population_board)
            # print("\nFitness : \n", population_fitness)

            max_fitness = numpy.max(population_fitness)
            max_fitness_idx = numpy.where(population_fitness == max_fitness)[0][0]
            # print("\nMax Fitness = ", max_fitness)

            best_outputs_fitness.append(max_fitness)
            best_outputs.append(self.population_1D_vector[max_fitness_idx, :])

            if max_fitness == float("inf"):
                print("Best solution found")
                self.num_attacks_Label.text = "Best Solution Found"
                print("\n1D population_board : \n", self.population_1D_vector)
                print("\n**  Best solution IDX = ", max_fitness_idx, "  **\n")

                best_outputs_fitness_array = numpy.array(best_outputs_fitness)
                best_outputs_array = numpy.array(best_outputs)

                numpy.save("best_outputs_fitness.npy", best_outputs_fitness)
                numpy.save("best_outputs.npy", best_outputs)
                print("\n**  Data Saved Successfully  **\n")

                break

            parents = genAlg.select_parents(self.population_1D_vector, population_fitness, num_parents)
            offspring_crossover = genAlg.crossover(parents, offspring_size=(self.num_solutions - parents.shape[0], 8))
            offspring_mutation = genAlg.mutation(offspring_crossover, num_mutations=numpy.uint8(self.num_mutations_TextInput.text))

            self.population_1D_vector[0:parents.shape[0], :] = parents
            self.population_1D_vector[parents.shape[0]:, :] = offspring_mutation

            self.vector_to_matrix()

    # Initialize the population_board for the Genetic Algorithm
    def initialize_population(self, *args):
        """
        Initializes the population_board matrix with random queen positions for the 8-queens problem.
        Converts the vector representation of solutions into matrix form for further processing.
        """
        self.num_solutions = numpy.uint8(self.num_solutions_TextInput.text)

        self.reset_board_text()

        self.population_1D_vector = numpy.zeros(shape=(self.num_solutions, 8))  # Rows represent solutions.

        for solution_idx in range(self.num_solutions):
            initial_queens_y_indices = numpy.random.rand(8) * 8
            initial_queens_y_indices = initial_queens_y_indices.astype(numpy.uint8)
            self.population_1D_vector[solution_idx, :] = initial_queens_y_indices

        self.vector_to_matrix()

        self.pop_created = True  # Indicates population_board is ready.
        self.num_attacks_Label.text = "Initial population_board Created."

    # Convert 1D vector representation to 2D matrix form
    def vector_to_matrix(self):
        """
        Converts the 1D vector representation of queen positions into a 2D matrix form for the board.
        Each solution (vector) is transformed into an 8x8 grid representation.
        """
        self.population_board = numpy.zeros(shape=(self.num_solutions, 8, 8))

        for solution_idx, current_solution in enumerate(self.population_1D_vector):
            current_solution = numpy.uint8(current_solution)
            for row_idx, col_idx in enumerate(current_solution):
                self.population_board[solution_idx, row_idx, col_idx] = 1

    # Reset the chessboard UI
    def reset_board_text(self):
        """
        Resets the chessboard UI, clearing all labels and resetting cell colors.
        """
        for row_idx in range(self.all_widgets.shape[0]):
            for col_idx in range(self.all_widgets.shape[1]):
                self.all_widgets[row_idx, col_idx].text = "[color=262626]" + str(row_idx) + ", " + str(col_idx) + "[/color]"
                with self.all_widgets[row_idx, col_idx].canvas.before:
                    kivy.graphics.Color(0, 0, 0, 1)  # Black background
                    self.rect = kivy.graphics.Rectangle(size=self.all_widgets[row_idx, col_idx].size, pos=self.all_widgets[row_idx, col_idx].pos)

    # Update the board to display the best solution
    def update_board_UI(self, *args):
        """
        Updates the chessboard UI with the best solution from the current population_board.
        Displays queen positions and updates fitness information.
        """
        if self.pop_created == False:
            return

        self.reset_board_text()

        population_fitness, total_num_attacks = self.fitness(self.population_board)

        max_fitness = numpy.max(population_fitness)
        max_fitness_idx = numpy.where(population_fitness == max_fitness)[0][0]
        best_solution = self.population_board[max_fitness_idx, :]

        self.num_attacks_Label.text = "Max Fitness = " + str(numpy.round(max_fitness, 4)) + "\n# Attacks = " + str(total_num_attacks[max_fitness_idx])

        for row_idx in range(8):
            for col_idx in range(8):
                if best_solution[row_idx, col_idx] == 1:
                    self.all_widgets[row_idx, col_idx].text = "[color=ffcc00]Queen[/color]"
                    with self.all_widgets[row_idx, col_idx].canvas.before:
                        kivy.graphics.Color(0, 1, 0, 1)  # Green for queens
                        self.rect = kivy.graphics.Rectangle(size=self.all_widgets[row_idx, col_idx].size, pos=self.all_widgets[row_idx, col_idx].pos)

    # Calculate the fitness of each solution
    def fitness(self, population_board):
        """
        Calculates the fitness of each solution in the population_board based on the number of attacks.
        Higher fitness is assigned to solutions with fewer attacks.
        """
        total_num_attacks_column = self.attacks_column(self.population_board)
        print("Number of Attacks (Column) : ", total_num_attacks_column)

        total_num_attacks_diagonal = self.attacks_diagonal(self.population_board)
        print("Number of Attacks (Diagonal) : ", total_num_attacks_diagonal)

        total_num_attacks = total_num_attacks_column + total_num_attacks_diagonal

        population_fitness = numpy.copy(total_num_attacks)

        print("Number of Attacks (Column + Diagonal) : ", total_num_attacks)

        for solution_idx in range(population_board.shape[0]):
            if population_fitness[solution_idx] == 0:
                population_fitness[solution_idx] = float("inf")  # Perfect solution
            else:
                population_fitness[solution_idx] = 1.0 / population_fitness[solution_idx]  # Lower attacks = higher fitness

        print("population_board Fitness (Column + Diagonal) : ", population_fitness)

        return population_fitness, total_num_attacks

    # Calculate diagonal attacks for each solution
    def attacks_diagonal(self, population_board):
        """
        Counts the number of diagonal attacks (both major and minor diagonals) for each solution.
        """
        total_num_attacks = numpy.zeros(population_board.shape[0])

        for solution_idx in range(population_board.shape[0]):
            ga_solution = population_board[solution_idx, :]

            temp = numpy.zeros(shape=(10, 10))
            temp[1:9, 1:9] = ga_solution

            row_indices, col_indices = numpy.where(ga_solution == 1)
            row_indices += 1
            col_indices += 1

            total = 0
            for element_idx in range(8):
                x = row_indices[element_idx]
                y = col_indices[element_idx]

                total += self.diagonal_attacks(temp[x:, y:])  # Bottom-right
                total += self.diagonal_attacks(temp[x:, y:0:-1])  # Bottom-left
                total += self.diagonal_attacks(temp[x:0:-1, y:])  # Top-right
                total += self.diagonal_attacks(temp[x:0:-1, y:0:-1])  # Top-left

            total_num_attacks[solution_idx] += total / 2

        return total_num_attacks

    # Helper for diagonal attacks
    def diagonal_attacks(self, mat):
        """
        Returns the number of queen attacks along the diagonal of a sub-matrix.
        """
        if mat.shape[0] < 2 or mat.shape[1] < 2:
            return 0
        return mat.diagonal().sum() - 1

    # Calculate column attacks for each solution
    def attacks_column(self, population_board):
        """
        Counts the number of column-wise attacks for each solution in the population_board.
        """
        total_num_attacks = numpy.zeros(population_board.shape[0])

        for solution_idx in range(population_board.shape[0]):
            ga_solution = population_board[solution_idx, :]

            for queen_y_pos in range(8):
                col_sum = numpy.sum(ga_solution[:, queen_y_pos])
                if col_sum > 1:
                    total_num_attacks[solution_idx] += col_sum - 1

        return total_num_attacks

    # Build the GUI
    def build(self):
        """
        Builds the graphical user interface (GUI) for the application, 
        including the chessboard and control buttons for GA operations.
        """
        boxLayout = kivy.uix.boxlayout.BoxLayout(orientation="vertical")

        gridLayout = kivy.uix.gridlayout.GridLayout(rows=8, size_hint_y=9)
        boxLayout_buttons = kivy.uix.boxlayout.BoxLayout(orientation="horizontal")

        boxLayout.add_widget(gridLayout)
        boxLayout.add_widget(boxLayout_buttons)

        self.all_widgets = numpy.zeros(shape=(8, 8), dtype="O")

        for row_idx in range(self.all_widgets.shape[0]):
            for col_idx in range(self.all_widgets.shape[1]):
                self.all_widgets[row_idx, col_idx] = kivy.uix.button.Button(text=str(row_idx) + ", " + str(col_idx), font_size=25)
                self.all_widgets[row_idx, col_idx].markup = True
                gridLayout.add_widget(self.all_widgets[row_idx, col_idx])

        ga_solution_button = kivy.uix.button.Button(text="Show Best Solution", font_size=15, size_hint_x=2)
        ga_solution_button.bind(on_press=self.update_board_UI)

        start_ga_button = kivy.uix.button.Button(text="Start GA", font_size=15, size_hint_x=2)
        start_ga_button.bind(on_press=self.start_ga)

        # Inputs for GA parameters
        self.num_solutions_TextInput = kivy.uix.textinput.TextInput(text="8", font_size=20, size_hint_x=1)
        self.num_generations_TextInput = kivy.uix.textinput.TextInput(text="10000", font_size=20, size_hint_x=1)
        self.num_mutations_TextInput = kivy.uix.textinput.TextInput(text="5", font_size=20, size_hint_x=1)

        # Display for fitness/attack stats
        self.num_attacks_Label = kivy.uix.label.Label(text="# Attacks/Best Solution", font_size=15, size_hint_x=2)

        # Add buttons and inputs to the layout
        boxLayout_buttons.add_widget(ga_solution_button)
        boxLayout_buttons.add_widget(start_ga_button)
        boxLayout_buttons.add_widget(self.num_solutions_TextInput)
        boxLayout_buttons.add_widget(self.num_generations_TextInput)
        boxLayout_buttons.add_widget(self.num_mutations_TextInput)
        boxLayout_buttons.add_widget(self.num_attacks_Label)

        return boxLayout

from kivy.config import Config
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '600')

queens = Queens8App()
queens.run()
