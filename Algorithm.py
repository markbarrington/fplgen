from Population import Population
from Individual import Individual
from random import random, randint
from fpl import fpl

class Algorithm():

    # Constants - Control Genetic Algorithm
    Uniform_rate = 0.5
    Mutation_rate = 0.015
    Tournament_size = 5
    Elitism = True

    # Compete, Crossover and Mutate current population to create evolved population
    @staticmethod
    def evolve_population(population_passed):
        print("Evolving population...")

        new_population = Population(population_passed.size(), False)

        # If Elitism is enabled then copy the best scoring individual to the next generation
        if Algorithm.Elitism:
            new_population.individuals.append(population_passed.get_fittest())
            elitism_off_set = 1
        else:
            elitism_off_set = 0
   
        #Do crossover over the entire population 
        for i in range(elitism_off_set, population_passed.size()):
            individual1 = Algorithm.tournament_selection(population_passed)
            individual2 = Algorithm.tournament_selection(population_passed)
            new_individual = Algorithm.crossover(individual1, individual2)
            new_population.individuals.append(new_individual)
   
        #Do mutation randomly
        for i in range(elitism_off_set, population_passed.size()):
            Algorithm.mutate(new_population.get_individual(i))

        #Repair any individuals broken by crossover or mutation
        for individual in new_population.individuals:
            individual.genes = fpl.repairteam(individual.genes)
                     
        for i in range(population_passed.size()):
            new_population.get_individual(i).reset_score()

        return new_population

    # Perform Crossover - Single Split
    @staticmethod
    def crossover(individual1_passed, individual2_passed):
        new_sol = Individual()
        for i in range(individual1_passed.size()):
            if random() <= Algorithm.Uniform_rate:
                new_sol.set_gene(i, individual1_passed.get_gene(i))
            else:
                new_sol.set_gene(i, individual2_passed.get_gene(i))
        return new_sol

    # Apply random mutation to individual
    @staticmethod
    def mutate(individual_passed):
        for i in range(individual_passed.size()):
            if random() <= Algorithm.Mutation_rate:
                gene = fpl.getrandomplayer()
                individual_passed.set_gene(i, gene)

    # Select fittest individuals by tournament selection
    @staticmethod	
    def tournament_selection(population_passed):
        #Tournament pool
        tournament = Population(Algorithm.Tournament_size, False)

        """ Tournament selection technique.
            How it works: The algorithm choose randomly five
            individuals from the population and returns the fittest one """
        for i in range(Algorithm.Tournament_size):
            random_id = int(random() * population_passed.size())
            tournament.individuals.append(population_passed.get_individual(random_id))
            tournament.individuals[i].set_score(population_passed.get_individual(random_id).get_score())

        fittest = tournament.get_fittest()
        return fittest

