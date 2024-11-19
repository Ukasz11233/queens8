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
        self.initialize_population()
        best_outputs = []
        best_outputs_fitness = []
        if not self.pop_created:
            return

        num_generations = numpy.uint16(self.num_generations_TextInput.text)
        num_parents = numpy.uint8(self.num_solutions / 2)

        for generation in range(num_generations):
            print("\n##  Generation = ", generation, "  ##\n")

            population_fitness, total_num_attacks = self.fitness(self.population)

            max_fitness = numpy.max(population_fitness)
            max_fitness_idx = numpy.where(population_fitness == max_fitness)[0][0]

            best_outputs_fitness.append(max_fitness)
            best_outputs.append(self.population[max_fitness_idx])
            if max_fitness == float("inf"):
                print("Best solution found")
                self.num_attacks_Label.text = "Best Solution Found"
                print("\nPopulation : \n", self.population)
                print("\n**  Best solution IDX = ", max_fitness_idx, "  **\n")

                numpy.save("best_outputs_fitness.npy", best_outputs_fitness)
                numpy.save("best_outputs.npy", best_outputs)
                print("\n**  Data Saved Successfully  **\n")

                break

            parents = genAlg.select_parents(self.population, population_fitness, num_parents)
            offspring_crossover = genAlg.crossover(parents, offspring_size=(self.num_solutions - parents.shape[0], 8, 2))
            offspring_mutation = genAlg.mutation(offspring_crossover, num_mutations=numpy.uint8(self.num_mutations_TextInput.text))

            self.population[0:parents.shape[0]] = parents
            self.population[parents.shape[0]:] = offspring_mutation

        self.update_board_UI()

    def call_force_stop(self):
        self.force_stop = True

    def initialize_population(self, *args):
        self.num_solutions = numpy.uint8(self.num_solutions_TextInput.text)

        self.reset_board_text()

        # Losowa inicjalizacja współrzędnych hetmanów
        self.population = numpy.random.randint(0, 8, size=(self.num_solutions, 8, 2))

        self.pop_created = True
        self.num_attacks_Label.text = "Initial population Created."

    def reset_board_text(self):
        for row_idx in range(self.all_widgets.shape[0]):
            for col_idx in range(self.all_widgets.shape[1]):
                self.all_widgets[row_idx, col_idx].text = "[color=262626]" + str(row_idx) + ", " + str(col_idx) + "[/color]"
                with self.all_widgets[row_idx, col_idx].canvas.before:
                    kivy.graphics.Color(0, 0, 0, 1)
                    self.rect = kivy.graphics.Rectangle(size=self.all_widgets[row_idx, col_idx].size, pos=self.all_widgets[row_idx, col_idx].pos)

    def update_board_UI(self, *args):
        if not self.pop_created:
            return

        self.reset_board_text()

        population_fitness, total_num_attacks = self.fitness(self.population)

        max_fitness = numpy.max(population_fitness)
        max_fitness_idx = numpy.where(population_fitness == max_fitness)[0][0]
        best_solution = self.population[max_fitness_idx]

        self.num_attacks_Label.text = "Max Fitness = " + str(numpy.round(max_fitness, 4)) + "\n# Attacks = " + str(total_num_attacks[max_fitness_idx])

        for (x, y) in best_solution:
            self.all_widgets[x, y].text = "[color=ffcc00]Queen[/color]"
            with self.all_widgets[x, y].canvas.before:
                kivy.graphics.Color(0, 1, 0, 1)
                self.rect = kivy.graphics.Rectangle(size=self.all_widgets[x, y].size, pos=self.all_widgets[x, y].pos)

    def fitness(self, population):
        total_num_attacks_column = self.attacks_column(population)
        total_num_attacks_diagonal = self.attacks_diagonal(population)
        total_num_attacks_horizontal = self.attacks_horizontal(population)

        total_num_attacks = total_num_attacks_column + total_num_attacks_diagonal + total_num_attacks_horizontal

        population_fitness = numpy.copy(total_num_attacks)

        for solution_idx in range(population.shape[0]):
            if population_fitness[solution_idx] == 0:
                population_fitness[solution_idx] = float("inf")
            else:
                population_fitness[solution_idx] = 1.0 / population_fitness[solution_idx]

        return population_fitness, total_num_attacks

    def attacks_diagonal(self, population):
        total_num_attacks = numpy.zeros(population.shape[0])

        for solution_idx in range(population.shape[0]):
            ga_solution = population[solution_idx]

            temp = numpy.zeros(shape=(10, 10))
            for (x, y) in ga_solution:
                temp[x + 1, y + 1] = 1

            total = 0
            for (x, y) in ga_solution:
                total += self.diagonal_attacks(temp[x + 1:, y + 1:])
                total += self.diagonal_attacks(temp[x + 1:, y + 1:0:-1])
                total += self.diagonal_attacks(temp[x + 1:0:-1, y + 1:])
                total += self.diagonal_attacks(temp[x + 1:0:-1, y + 1:0:-1])

            total_num_attacks[solution_idx] += total / 2

        return total_num_attacks

    def diagonal_attacks(self, mat):
        if mat.shape[0] < 2 or mat.shape[1] < 2:
            return 0
        return mat.diagonal().sum() - 1

    def attacks_column(self, population):
        total_num_attacks = numpy.zeros(population.shape[0])

        for solution_idx in range(population.shape[0]):
            ga_solution = population[solution_idx]

            for queen_y_pos in range(8):
                col_sum = numpy.sum([1 for (x, y) in ga_solution if y == queen_y_pos])
                if col_sum > 1:
                    total_num_attacks[solution_idx] += col_sum - 1

        return total_num_attacks

    def attacks_horizontal(self, population):
        total_num_attacks = numpy.zeros(population.shape[0])

        for solution_idx in range(population.shape[0]):
            ga_solution = population[solution_idx]

            for queen_x_pos in range(8):
                row_sum = numpy.sum([1 for (x, y) in ga_solution if x == queen_x_pos])
                if row_sum > 1:
                    total_num_attacks[solution_idx] += row_sum - 1

        return total_num_attacks


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
        self.num_solutions_TextInput = kivy.uix.textinput.TextInput(text="150", font_size=20, size_hint_x=1)
        self.num_generations_TextInput = kivy.uix.textinput.TextInput(text="500", font_size=20, size_hint_x=1)
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
