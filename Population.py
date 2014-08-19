from Individual import Individual
from FitnessCalc import FitnessCalc
from fpl import fpl

class Population():

    def __init__(self, population_size, initialise):
        self.individuals = []

        #Creates the individuals
        if (initialise):
            for i in range(population_size):
                new_individual = Individual()
                self.individuals.append(new_individual)
  
    # Determine the fitness of an individual
    def get_fitness(self, individual_passed):
        fitness = individual_passed.get_score()
        if fitness == -1:
            fitness = fpl.scoreteam(individual_passed.genes)
            individual_passed.set_score(fitness)
        return fitness

    # Get the score of the fittest individual in a population
    def fitness_of_the_fittest(self):
        fitness_of_the_fittest = self.get_fitness(self.get_fittest())
        return fitness_of_the_fittest

    # Get the fittest individual in a population
    def get_fittest(self):
        fittest = self.individuals[0]
        for i in range(len(self.individuals)):
            if self.get_fitness(fittest) <= self.get_fitness(self.individuals[i]) :
                fittest = self.individuals[i]
        return fittest

    # Get the average fitness of a population
    def get_average_fitness(self):
        totalFitness = 0
        scores = []
        for i in range(len(self.individuals)):
            score = self.individuals[i].get_score()
            totalFitness += score
            scores.append(score)
        return totalFitness / len(self.individuals)

    # Get the size of a population
    def size(self):
        return len(self.individuals)

    # Get a specific member of a population    
    def get_individual(self, index):
        return self.individuals[index]

    # Set a specific member of a population        
    def save_individual(self, index, individual_passed):
        self.individuals[index] = individual_passed

    # Output the fittest individual in a population
    def OutputFittest(self):
        fittest = self.get_fittest()
        fpl.scoreteam(fittest.genes,True)

