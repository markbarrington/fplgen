from random import randint
from FitnessCalc import FitnessCalc
from fpl import fpl

# Each individual represents a team
class Individual():

    # 15 players per team  
    DefaultGeneLength = 15

    # Initialise an individual
    def __init__(self):
        self.genes = []
        self.geneScore = -1

        self.genes = fpl.generateteam()		

    # Get an individual player from a team
    def get_gene(self, index):
        return self.genes[index]

    # Set an individual player in a team	
    def set_gene(self, index, what_to_set):
        self.genes[index] =  what_to_set

    # Return the size of the individual	
    def size(self):
        return len(self.genes)

    # Set the score for the individual
    def set_score(self, score):
        self.geneScore = score

    # Get the score for an individual
    def get_score(self):
        return self.geneScore

    # Reset the score for an individual
    def reset_score(self):
        self.geneScore = -1
