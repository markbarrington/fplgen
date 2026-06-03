from Population import Population
from Individual import Individual
from random import random, randint
from fpl import fpl

class Algorithm():

    # Constants - Control Genetic Algorithm
    Uniform_rate = 0.5
    Mutation_rate = 0.015
    Tournament_size = 3
    Elitism = True

    Mutated = 0

    # Compete, Crossover and Mutate current population to create evolved population
    @staticmethod
    
    def evolve_population(population_passed,generation):
        print("Evolving population... ")

        #if generation % 100 == 0:
        #    Algorithm.Mutation_rate *= 1.5

        new_population = Population(
            population_passed.size(),
            False,
            scenario=population_passed.scenario,
        )

        # If Elitism is enabled then copy the best scoring individual to the next generation
        if Algorithm.Elitism:
            new_population.individuals.append(population_passed.get_fittest())
            #print "Elite            : ", population_passed.fitness_of_the_fittest()
            elitism_off_set = 1
        else:
            elitism_off_set = 0
   
        #Do crossover over the entire population 
        for i in range(elitism_off_set, population_passed.size()):
            individual1 = Algorithm.tournament_selection(population_passed)
            individual2 = Algorithm.tournament_selection(population_passed)
            new_individual = Algorithm.crossover(individual1, individual2)
            new_population.individuals.append(new_individual)
   
        #print "Elite after cross    : ", new_population.OutputFittest()

        #Do mutation randomly
        Algorithm.Mutated = 0
        for i in range(elitism_off_set, population_passed.size()):
            #print "Mutate Index ", i
            Algorithm.mutate(new_population.get_individual(i), scenario=population_passed.scenario)

        #print("Mutated %s" % Algorithm.Mutated)

        #print "Elite after mututate : ", new_population.OutputFittest()

        #Repair any individuals broken by crossover or mutation
        #for individual in new_population.individuals:
        #    individual.genes = fpl.repairteam(individual.genes)

        #print "Elite after repair   : ", new_population.fitness_of_the_fittest()

                     
        for i in range(population_passed.size()):
            new_population.get_individual(i).reset_score()

        #print "Elite after reset    : ", new_population.fitness_of_the_fittest()

        return new_population

    # Perform Crossover - Single Split
    @staticmethod
    def crossover(individual1_passed, individual2_passed):
        new_sol = Individual([None] * individual1_passed.size())
        for i in range(0,individual1_passed.size()):
            if random() <= Algorithm.Uniform_rate:
                new_sol.set_gene(i, individual1_passed.get_gene(i))
            else:
                new_sol.set_gene(i, individual2_passed.get_gene(i))

        return new_sol

    # Apply random mutation to individual
    @staticmethod
    def mutate(individual_passed, scenario=None):
        mutated = False
        #print "Gene Size ", individual_passed.size()
        # players
        start_index = 15 if scenario is not None else 0
        for i in range(start_index,individual_passed.size()-2):
            if random() <= Algorithm.Mutation_rate:
                gene = fpl.getrandomplayer(individual_passed.get_gene(i))
                individual_passed.set_gene(i, gene)
                Algorithm.Mutated += 1
                mutated = True
        # transfer pattern
        if random() <= Algorithm.Mutation_rate:
            gene = fpl.mutatepattern(individual_passed.get_gene(individual_passed.size()-2))
            individual_passed.set_gene(individual_passed.size()-2,gene)
            mutated = True
        # Chip weeks

        if random() <= Algorithm.Mutation_rate:
            gene = fpl.mutatechips(individual_passed.get_gene(individual_passed.size()-1))
            individual_passed.set_gene(individual_passed.size()-1,gene)
            mutated = True

        # replacement index

        #if random() <= Algorithm.Mutation_rate:
        #    gene = []
        #    for j in range(0,5):
        #        gene.append(fpl.getrandomindex(individual_passed.get_gene(15+j)))
        #    individual_passed.set_gene(individual_passed.size()-1,gene)

        return mutated

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

        fittest = tournament.get_fittest(False)
        return fittest
