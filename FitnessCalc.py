class FitnessCalc():
    # Set to value higher than highest possible score value  
    Solution = 1000

    @staticmethod
    def set_solution(solution_passed):
        FitnessCalc.Solution = int(solution_passed)

    @staticmethod
    def get_max_fitness():
        return 1000

    @staticmethod
    def targetValue():
        return 14

