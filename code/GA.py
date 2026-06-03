import argparse
import random
from pathlib import Path
from time import time

import fpl as fpl_module
from Algorithm import Algorithm
from FitnessCalc import FitnessCalc
from Population import Population
from fpl import fpl
from paths import DATA_DIR


DEFAULT_POPULATION_SIZE = 10000
DEFAULT_GENERATION_LIMIT = 300
DEFAULT_MAX_FITNESS = 10000
DEFAULT_STATUS_INTERVAL = 20
DEFAULT_INPUT = DATA_DIR / "fplreview.csv"
DEFAULT_GAMEWEEK = fpl_module.gameweek
DEFAULT_FORECASTWEEKS = fpl_module.forecastweeks


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="Run the FPLgen genetic algorithm against fplreview projections."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to a fplreview CSV export.",
    )
    parser.add_argument(
        "--population",
        type=positive_int,
        default=DEFAULT_POPULATION_SIZE,
        help="Population size for the GA run.",
    )
    parser.add_argument(
        "--generations",
        type=positive_int,
        default=DEFAULT_GENERATION_LIMIT,
        help="Maximum generation count before stopping.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible runs.",
    )
    parser.add_argument(
        "--gameweek",
        type=positive_int,
        default=DEFAULT_GAMEWEEK,
        help="First gameweek to load from the fplreview export.",
    )
    parser.add_argument(
        "--forecastweeks",
        type=positive_int,
        default=DEFAULT_FORECASTWEEKS,
        help="Number of gameweeks to load from the fplreview export.",
    )
    return parser.parse_args(args)


def apply_runtime_options(seed=None, gameweek=None, forecastweeks=None):
    if seed is not None:
        random.seed(seed)
    if gameweek is not None:
        fpl_module.gameweek = gameweek
    if forecastweeks is not None:
        fpl_module.forecastweeks = forecastweeks


def run(
    input_path=DEFAULT_INPUT,
    population_size=DEFAULT_POPULATION_SIZE,
    generation_limit=DEFAULT_GENERATION_LIMIT,
    seed=None,
    gameweek=DEFAULT_GAMEWEEK,
    forecastweeks=DEFAULT_FORECASTWEEKS,
    max_fitness=DEFAULT_MAX_FITNESS,
    status_interval=DEFAULT_STATUS_INTERVAL,
):
    apply_runtime_options(seed=seed, gameweek=gameweek, forecastweeks=forecastweeks)

    print("Importing player data")
    fpl.getplayerdata(input_path)
    print("Player data imported")

    start = time()
    FitnessCalc.set_solution(max_fitness)

    print("Creating intial population")
    my_pop = Population(population_size, True)
    print("Population created")

    generation_count = 0
    while my_pop.fitness_of_the_fittest() < FitnessCalc.get_max_fitness():
        generation_count += 1
        print("Starting Generation %s" % generation_count)

        if status_interval and generation_count % status_interval == 0:
            print("Outputting Current Status")
            my_pop.OutputFittest()

        if generation_count == generation_limit:
            break

        print("Average Fitness : %s" % my_pop.get_average_fitness())
        print(
            "Generation : %s Fittest : %s "
            % (generation_count, my_pop.fitness_of_the_fittest())
        )
        my_pop = Algorithm.evolve_population(my_pop, generation_count)
        print("******************************************************")

    finish = time()
    print("Time elapsed : %s " % (finish - start))

    fittest_score = my_pop.OutputFittest()
    return {
        "population": my_pop,
        "generation_count": generation_count,
        "fittest_score": fittest_score,
        "elapsed": finish - start,
    }


def main(args=None):
    options = parse_args(args)
    run(
        input_path=options.input,
        population_size=options.population,
        generation_limit=options.generations,
        seed=options.seed,
        gameweek=options.gameweek,
        forecastweeks=options.forecastweeks,
    )


if __name__ == "__main__":
    main()
