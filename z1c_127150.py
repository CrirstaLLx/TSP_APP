import random
import math
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# constants for genetic algorithm
POPULATION_SIZE = 100
GENERATIONS = 500
MUTATION_RATE = 0.05
CROSSOVER_RATE = 0.8

# constants for simulated annealing
INITIAL_TEMPERATURE = 10000
FINAL_TEMPERATURE = 1e-8
COOLING_RATE = 0.995

# settings for cities
NUM_CITIES = random.randint(20, 40)
cities = []

# store progress for each algorithm
genetic_progress = []
sa_progress = []

# Create the main window
root = tk.Tk()
root.title("Travelling Salesman Problem App")
root.geometry("1400x600")

main_frame = tk.Frame(root)
main_frame.pack(pady=10)

# Canvas to display cities and paths
canvas_width, canvas_height = 600, 400
canvas = tk.Canvas(main_frame, width=canvas_width, height=canvas_height, bg="white")
canvas.grid(row=0, column=0, padx=20)

canvas_center_x = canvas_width // 2
canvas_center_y = canvas_height // 2

# Create a figure for the matplotlib plot
fig, ax = plt.subplots()
ax.set_title("Algorithm Progress")
ax.set_xlabel("Iteration")
ax.set_ylabel("Distance")
ax.grid(True)

canvas_plot = FigureCanvasTkAgg(fig, master=main_frame)
canvas_plot.get_tk_widget().grid(row=0, column=1, padx=20)

# Calculate the distance between two cities
def calculate_distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

# Generate random cities and draw them on the canvas
def generate_cities():
    global cities, NUM_CITIES

    NUM_CITIES = random.randint(20, 40)
    cities = [(random.randint(0, 200), random.randint(0, 200)) for _ in range(NUM_CITIES)]

    canvas.delete("all")
    for x, y in cities:
        # Center the cities by adding offset (shift them by canvas_center_x and canvas_center_y)
        centered_x = x + canvas_center_x - 100
        centered_y = y + canvas_center_y - 100

        canvas.create_oval(centered_x - 5, centered_y - 5, centered_x + 5, centered_y + 5, fill="blue")
        canvas.create_text(centered_x, centered_y - 10, text=f"({x}, {y})", font=("Arial", 8), fill="black")

    print(f"Generated {NUM_CITIES} cities: {cities}")

# Function to calculate the total distance of a tour
def calculate_total_distance(tour):
    distance = 0
    for i in range(NUM_CITIES):
        distance += calculate_distance(cities[tour[i]], cities[tour[(i + 1) % NUM_CITIES]])
    return distance

# Initialize a population with random permutations of cities (for Genetic Algorithm)
def initialize_population():
    population = []
    for _ in range(POPULATION_SIZE):
        individual = list(range(NUM_CITIES))
        random.shuffle(individual)
        population.append(individual)
    return population

# Tournament selection (selects the fittest individual from a randomly chosen subset of the population)
def tournament_selection(population):
    tournament_size = 5
    tournament = random.sample(population, tournament_size)
    return min(tournament, key=calculate_total_distance)

# Crossover
def crossover(parent1, parent2):
    if random.random() > CROSSOVER_RATE:
        return parent1[:]  # No crossover, return parent1 as is

    start, end = sorted(random.sample(range(NUM_CITIES), 2))
    child = [-1] * NUM_CITIES

    child[start:end + 1] = parent1[start:end + 1]

    pos = (end + 1) % NUM_CITIES
    for gene in parent2:
        if gene not in child:
            child[pos] = gene
            pos = (pos + 1) % NUM_CITIES

    return child

# Mutate an individual by swapping two cities
def mutate(individual):
    if random.random() < MUTATION_RATE:
        idx1, idx2 = random.sample(range(NUM_CITIES), 2)
        individual[idx1], individual[idx2] = individual[idx2], individual[idx1]

# Evolve the population through selection, crossover, and mutation
def evolve_population(population):
    new_population = []
    for _ in range(POPULATION_SIZE):
        parent1 = tournament_selection(population)
        parent2 = tournament_selection(population)
        child = crossover(parent1, parent2)
        mutate(child)
        new_population.append(child)
    return new_population

# Run the genetic algorithm and display the best path
def run_genetic_algorithm():
    if not cities:
        print("Please generate cities first!")
        return

    population = initialize_population()
    best_distance = float('inf')
    best_solution = None
    genetic_progress.clear()

    for generation in range(GENERATIONS):
        population = evolve_population(population)
        for individual in population:
            distance = calculate_total_distance(individual)
            if distance < best_distance:
                best_distance = distance
                best_solution = individual

        genetic_progress.append(best_distance)

        if generation % 100 == 0:
            print(f"Generation {generation}, Best Distance: {best_distance:.2f}")

    print(f"Genetic Algorithm Finished! Best Distance: {best_distance:.2f}")
    print(f"Best route: {best_solution}")

    ax.clear()
    ax.plot(genetic_progress, label="Genetic Algorithm")
    ax.set_title("Algorithm Progress")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Distance")
    ax.grid(True)
    ax.legend()
    canvas_plot.draw()

    canvas.delete("all")

    for i, city_index in enumerate(best_solution):
        x, y = cities[city_index]
        centered_x = x + canvas_center_x - 100
        centered_y = y + canvas_center_y - 100

        canvas.create_oval(centered_x - 5, centered_y - 5, centered_x + 5, centered_y + 5, fill="blue")
        canvas.create_text(centered_x, centered_y - 15, text=str(i + 1), font=("Arial", 10), fill="red")

    for i in range(NUM_CITIES):
        city1 = cities[best_solution[i]]
        city2 = cities[best_solution[(i + 1) % NUM_CITIES]]
        centered_x1 = city1[0] + canvas_center_x - 100
        centered_y1 = city1[1] + canvas_center_y - 100
        centered_x2 = city2[0] + canvas_center_x - 100
        centered_y2 = city2[1] + canvas_center_y - 100
        canvas.create_line(centered_x1, centered_y1, centered_x2, centered_y2, fill="red", width=2)


# Function to perform a small random swap of two cities (for Simulated Annealing)
def swap_cities(tour):
    new_tour = tour[:]
    idx1, idx2 = random.sample(range(NUM_CITIES), 2)
    new_tour[idx1], new_tour[idx2] = new_tour[idx2], new_tour[idx1]
    return new_tour


# Simulated Annealing Algorithm
def simulated_annealing():
    if not cities:
        print("Please generate cities first!")
        return

    current_solution = list(range(NUM_CITIES))
    random.shuffle(current_solution)
    current_distance = calculate_total_distance(current_solution)

    best_solution = current_solution[:]
    best_distance = current_distance
    sa_progress.clear()

    temperature = INITIAL_TEMPERATURE

    # Cooling process
    while temperature > FINAL_TEMPERATURE:
        new_solution = swap_cities(current_solution)
        new_distance = calculate_total_distance(new_solution)

        delta_distance = new_distance - current_distance

        if delta_distance < 0 or random.random() < math.exp(-delta_distance / temperature):
            current_solution = new_solution
            current_distance = new_distance

            if current_distance < best_distance:
                best_solution = current_solution[:]
                best_distance = current_distance

        sa_progress.append(best_distance)

        temperature *= COOLING_RATE

    print(f"Simulated Annealing Finished! Best Distance: {best_distance:.2f}")
    print(f"Best route: {best_solution}")

    ax.clear()
    ax.plot(sa_progress, label="Simulated Annealing", color="green")
    ax.set_title("Algorithm Progress")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Distance")
    ax.grid(True)
    ax.legend()
    canvas_plot.draw()

    canvas.delete("all")

    for i, city_index in enumerate(best_solution):
        x, y = cities[city_index]
        centered_x = x + canvas_center_x - 100
        centered_y = y + canvas_center_y - 100

        canvas.create_oval(centered_x - 5, centered_y - 5, centered_x + 5, centered_y + 5, fill="blue")
        canvas.create_text(centered_x, centered_y - 15, text=str(i + 1), font=("Arial", 10), fill="red")

    for i in range(NUM_CITIES):
        city1 = cities[best_solution[i]]
        city2 = cities[best_solution[(i + 1) % NUM_CITIES]]
        centered_x1 = city1[0] + canvas_center_x - 100
        centered_y1 = city1[1] + canvas_center_y - 100
        centered_x2 = city2[0] + canvas_center_x - 100
        centered_y2 = city2[1] + canvas_center_y - 100
        canvas.create_line(centered_x1, centered_y1, centered_x2, centered_y2, fill="green", width=2)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

button_gc = tk.Button(button_frame, text="Generate cities", command=generate_cities)
button_gc.pack(side=tk.LEFT, padx=10)

button_ga = tk.Button(button_frame, text="Genetic algorithm", command=run_genetic_algorithm)
button_ga.pack(side=tk.LEFT, padx=10)

button_sa = tk.Button(button_frame, text="Simulated annealing", command=simulated_annealing)
button_sa.pack(side=tk.LEFT, padx=10)

root.mainloop()
