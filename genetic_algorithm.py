import random
import numpy as np
import pygame
import copy

scale = 2  # 2 pixels = 1 cm in real life
robot_width, robot_length = 16, 26  # real robot width in cm, real robot length in cm
l_dist, t_dist = 200, 200  # odleglosc sciany pomieszczenia od lewej i gornej krawedzi okna [w rzeczywistej odleglosci cm]
robot_start_positions = [
    [l_dist * scale + 19 * scale, t_dist * scale + 105 * scale],
    [l_dist * scale + 50 * scale, t_dist * scale + 80 * scale],
    [l_dist * scale + 100 * scale, t_dist * scale + 20 * scale],
    [l_dist * scale + 30 * scale, t_dist * scale + 120 * scale],
    [l_dist * scale + 110 * scale, t_dist * scale + 100 * scale],
    [l_dist * scale + 90 * scale, t_dist * scale + 10 * scale],
    [l_dist * scale + 50 * scale, t_dist * scale + 100 * scale],
    [l_dist * scale + 10 * scale, t_dist * scale + 30 * scale],
    [l_dist * scale + 100 * scale, t_dist * scale + 60 * scale],
    [l_dist * scale + 60 * scale, t_dist * scale + 80 * scale]
]  # position of the left upper corner of the robot, here 19cm from left wall


class Robot:

    def __init__(self, genom, map):
        self.fitness = 0
        self.pos = pygame.Rect(robot_start_positions[map][0],
                               robot_start_positions[map][1],
                               robot_width * scale, robot_length * scale)
        self.robot_direction = 0  # direction of the front of the robot: 0-down, 1-up, 2-left, 3-right
        self.did_reach_target = False
        self.did_hit_wall = False
        self.genom = genom
        self.propability_of_selection = 0

    def reset_values(self, map):
        self.pos = pygame.Rect(robot_start_positions[map][0],
                               robot_start_positions[map][1],
                               robot_width * scale, robot_length * scale)
        self.robot_direction = 0  # direction of the front of the robot: 0-down, 1-up, 2-left, 3-right
        self.did_reach_target = False
        self.did_hit_wall = False
        self.propability_of_selection = 0

    def calulate_fitness(self, target_pos):
        if self.did_reach_target:
            self.fitness = 10000
        else:
            ###TO DO: poprawić, aby było kompatybilne z pygame
            # 100 / dystans euklidesowy do celu
            self.fitness = 100000 / np.sqrt((self.pos.x - target_pos[0])**2 +
                                            (self.pos.y - target_pos[1])**2)
            if self.did_hit_wall:
                self.fitness = 0.8 * self.fitness
            # print(self.fitness)
        return self.fitness

    def calculate_propability_of_selection(self, fitness_sum):
        self.propability_of_selection = self.fitness / fitness_sum


def create_population(size, map, genom_size):
    # każdy osbnik ma zakodowaną sekwencję komend prosto, prawo, lewo, zawróć
    number_of_instructions = genom_size  # zmienna określająca długość tej sekwencji
    population = []
    for i in range(size):
        # kodowanie całkowitoliczbowe
        # 0 - prosto
        # 1 - prawo
        # 2 - lewo
        # 3 - zawróć
        genom = np.random.randint(4, size=(number_of_instructions))
        # print(genom)
        population.append(Robot(genom, map))
    print("population created")
    return population


def selection(population):
    # selekcja proporcjonalna
    cum_distribution = 0
    r = np.random.rand()
    for i, robot in enumerate(population):
        cum_distribution += robot.propability_of_selection
        if r <= cum_distribution:
            # print(i)
            return copy.deepcopy(robot)


def crossover(selected_first_parent, selected_second_parent):
    # Krzyżowanie dwupunktowe
    size = len(selected_first_parent.genom)

    # dwa losowe punkty krzyżowania
    a = random.randint(0, size - 1)
    b = random.randint(0, size - 1)
    if a > b:
        a, b = b, a

    first_baby = selected_first_parent.genom
    second_baby = selected_second_parent.genom

    first_baby[a:b] = selected_second_parent.genom[a:b]
    second_baby[a:b] = selected_first_parent.genom[a:b]

    return first_baby, second_baby


def mutation(baby_genom):
    size = len(baby_genom)
    mutation_rate = 0.2
    r = np.random.rand()
    if r < mutation_rate:
        # print("mutation!")
        ind = random.randint(0, size - 1)
        baby_genom[ind] = random.randint(0, 3)
    return baby_genom


def create_next_generation(population, fitness_sum, map):

    population.sort(key=lambda x: x.fitness, reverse=True)
    print("sorted by firness: ")
    for robot in population:
        print(robot.fitness)
    print("Best fintess: ", population[0].fitness)

    new_population = []

    # 2 najlepszych zostaje w nowej populacji
    population[0].reset_values(map)
    population[1].reset_values(map)

    new_population.append(copy.deepcopy(population[0]))
    new_population.append(copy.deepcopy(population[1]))

    #print("best genom: ", new_population[0].genom)

    for robot in population:
        robot.calculate_propability_of_selection(fitness_sum)
    # sortowanie
    #population.sort(key=lambda x: x.propability_of_selection, reverse=True)
    for i in range(int((len(population) - 2) / 2)):
        selected_first_parent = selection(population)
        selected_second_parent = selection(population)
        first_baby_genom, second_baby_genom = crossover(
            selected_first_parent, selected_second_parent)
        first_baby_genom = mutation(first_baby_genom)
        second_baby_genom = mutation(second_baby_genom)
        new_population.append(Robot(first_baby_genom, map))
        new_population.append(Robot(second_baby_genom, map))
    # print("genom after: ", new_population[0].genom)
    print("next generation created")
    return new_population
