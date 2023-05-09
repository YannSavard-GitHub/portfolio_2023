"""
Project: Adaptive Rhythmic Training Application (ARTA)
File   : main.py
Date   : 21/01/2022
Author : Yann Savard

This code is open source, except for some parts that were taken
from external sources and their sources are mentioned in the code.

History: programmed from september 2021 to february 2022 as part of my bachelor project:
"Conception and Evaluation of New Rhythm-Based Dexterity Training Methods with Adaptive Game Mechanics and AI"
"""

from venv.gamemanager import GameManager


if __name__ == '__main__':

    # UNCOMMMENT ONLY THE SECTION (all between the section's lines) THAT YOU WANT TO USE (1 AT A TIME) AND COMMENT
    # ALL THE OTHER ONES.

    gameManager= GameManager()

    # # SECTION 1: Application Start - Rhythmic training with the application
    # ------------------------------------------------------------------------------------------------------------------
    # mode 0: Training to generate data for the neural network
    # mode 1: Training to evaluate the different rhythmic training methods - 1st training
    gameManager.start_app(mode=1)
    # ------------------------------------------------------------------------------------------------------------------

    # SECTION 2: Generation of data set from training performance files -
    # Training, evaluation and saving of the implemented neural network.
    #------------------------------------------------------------------------------------------------------------------
    #
    # # Generate data_set for the training of the neural network from the raw_output_data files
    # # in the following folder: 'Performance/performance_data/raw_output_data'
    # gameManager.perf_manager.reshape_raw_output_data(True)
    #
    # # load data_set for following path: Performance/performance_data/data_set/Input_Data
    # gameManager.perf_manager.load_input_data_set()
    # gameManager.neural_network.split_data_set(4/5)
    #
    # # Neural network
    # gameManager.neural_network.set_tensorboard_cnn()
    # gameManager.neural_network.train_model()
    # gameManager.neural_network.evaluate_model()
    # gameManager.neural_network.save_model()

    #-------------------------------------------------------------------------------------------------------------------

    # SECTION 3 - Evaluation of performance and the neural network; optimization of rhythmic
    # patterns (performance average)
    #-------------------------------------------------------------------------------------------------------------------
    # # Generate data_set for the training of the neural network from the raw_output_data files
    # # in the following folder: 'Performance/performance_data/raw_output_data'
    #
    # gameManager.perf_manager.reshape_raw_output_data(False) # only use if raw_output_data has not been reshaped
    #
    # # load data_set for following path: Performance/performance_data/data_set/Input_Data
    # gameManager.perf_manager.load_input_data_set()
    #
    # gameManager.neural_network.split_data_set(4/5)
    # # Load the neural network after model has been trained from the following path: 'Neural_Network_Models\model'
    # gameManager.neural_network.load_model()
    #
    # #show training and validation (test) predictions of the neural network for the current dataset
    # gameManager.neural_network.compare_pred_true()
    #
    # # Optimize the rhythmic patterns of the current dataset with the best performance values by
    # # generating new patterns that have a higher prediction for the performance average of those rhythmic patterns
    # # If the parameter optimize is True, the patterns will be optimized \
    # # (number=number of patterns; iteration=number of iterations for the optimization process)
    # gameManager.perf_manager.sort_optimize_patterns(number=50, optimize= True, iterations=250)
    # ------------------------------------------------------------------------------------------------------------------
    #
    # #SECTION 4 - Evaluation of training sessions - Only for evaluation modes (1 and 2):
    # # ----------------------------------------------------------------------------------------------------------------
    # mode 2 - just used with this section: Training to evaluate the different rhythmic training methods -
    # 2nd training of my bachelor project

    # Generate graphics (from dataset in the files in the following folders:
    # day 1 of training: Performance/performance_data_/raw_output_data_day_1
    # day 2 of training: Performance/performance_data_/raw_output_data_day_2)

    gameManager.perf_manager.evaluate_training(mode=2)
    #-------------------------------------------------------------------------------------------------------------------

