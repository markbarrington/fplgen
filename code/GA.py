from FitnessCalc import FitnessCalc
from Population import Population
from Algorithm import Algorithm
from time import time
from fpl import fpl

# Import the player data from a file

print("Importing player data")
fpl.getplayerdata()
print("Player data imported")

# Time the algorithm

start = time()

# Set solution value higher than highest possible score.
# Look for the best possible answer
FitnessCalc.set_solution(10000)

# Create the initial random population
print("Creating intial population")
my_pop = Population(10000, True)
print("Population created")
savedpoints = 0
# Loop until number of generations is complete
generation_count = 0
while my_pop.fitness_of_the_fittest() < FitnessCalc.get_max_fitness():
    generation_count += 1
    print("Starting Generation %s" % generation_count)

    # Output the best solution every 100 generations
    if generation_count % 20 == 0:
        print("Outputting Current Status")
        points = my_pop.OutputFittest()
        #if points < savedpoints:
        #    print "Elitism Failed"
        #    break
            
    # Quit after a set number of generations
    if generation_count == 300:
        break

    # Output current generation data and produce next generation
    print("Average Fitness : %s" % my_pop.get_average_fitness())
    print("Generation : %s Fittest : %s " % (generation_count, my_pop.fitness_of_the_fittest()))
    my_pop = Algorithm.evolve_population(my_pop, generation_count)
    print("******************************************************")
  
# Output algorithm run time
finish = time()
print ("Time elapsed : %s " % (finish - start)) 

# Output the best solution found
my_pop.OutputFittest()
