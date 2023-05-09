"""
Project: Adaptive Rhythmic Training Application (ARTA)
File   : gamemanager.py
Date   : 21/01/2022
Author : Yann Savard

This code is open source, except for some parts that were taken
from external sources and their sources are mentioned in the code.

History: programmed from september 2021 to february 2022 as part of my bachelor project:
"Conception and Evaluation of New Rhythm-Based Dexterity Training Methods with Adaptive Game Mechanics and AI"
"""

from venv.window import PgWindow
from venv.gridmanager import GridManager
from venv.rhythmmanager import RhythmManager
from venv.inputmanager import InputManager
from venv.performancemanager import PerformanceManager
from venv.runit import RUnit
from venv.neuralnetwork import NeuralNetwork
#from venv.dbmanager import DatabaseManager

#multiprocessing
import multiprocessing
from multiprocessing import Process
from multiprocessing import Value, Lock


#pygame
import pygame
import pygame.midi
from pygame.locals import *

#matplotlib
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.backends.backend_tkagg as bbt
import matplotlib.backends.backend_agg as agg

#numpy
import numpy as np
from numpy import loadtxt

#gui
import pyautogui

#inputs
import pynput
from pynput.mouse import Button, Controller

#outputs
import os

#others
import threading
import time
import datetime
import random
from itertools import count
import pylab
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor


class GameManager():
    def __init__(self):

        #class objects
        self.window = PgWindow(self)
        self.grid_manager = GridManager(self)
        self.rhythm_manager = RhythmManager(self)
        self.perf_manager = PerformanceManager(self)
        self.input_manager = InputManager(self)
        self.neural_network = NeuralNetwork(self)

        #multi-processing
        self.lock = Lock()  # for multi-processes

        #game states
        self.mode= 0  #0= training for generate data for the A.I.    1= evaluation of rhythmic training#
        self.game_state=0  #0=test - 1=play
        self.test_set = False # if game state test is set
        self.play_set= False # if game state play is set
        self.test_done=False

        #timing
        self.timeStart= 0.0
        self.timeNow = 0.0
        self.time_division = 8
        self.tempo= 1.0
        self.min_bpm=5
        self.max_bpm=750

        self.bpm= 60/self.tempo
        self.timerDelay = 1/self.time_division
        self.note_delay=0.0
        self.ticks= 0 #ticks since the the start of the timer
        self.notes = [-5]  # list of all incremented notes (for the neural network)

        # round time
        self.round_start = 0.0
        self.next_round_start=0.0
        self.round_end = 0.0

        #display
        self.screen= None
        self.y_pos = 10

        #plt graphics
        self.x_coor = []
        self.y_coor = []
        self.values = 0  # y_coor_values
        self.animation= None
        self.animations=[]
        self.fig = None
        self.index= count()
        self.tot_graphs=3
        self.this_graphs_idx = 0 #index of current graph

        #rounds
        self.round=1
        self.next_round=1 #value of round before before the round value is saved in the Performance/round-evaluation.txt file

        # parameters for the neural network
        #================================================================
        self.time_now = []
        self.note_division = []

        # ================================================================

    def start_app(self, mode):
        """
        Runs the application according to the mode entered in parameter.
        :param mode: 0= training for the A.I.
                     1= evaluation mode for the different rhythmic training methods implemented.
        :return: nothing
        """
        self.mode=mode
        self.game_state= 0 # 0= test before the training
        self.set_test()


    def focus_on_window(self):
        """Focuses the program on the present window - this methdd is temporary, until a better solution is found.

        :returns: nothing
        """
        pygame.mouse.set_pos([0, 0])
        mouse = Controller()
        mouse.click(Button.left, 1)

    def StartPygame(self):
        """Runs the pygame window, mixer and manages keyboard inputs.

        :returns: nothing
        """

        pygame.init()
        #pygame documentation: https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.init
        # init(frequency=44100, size=-16, channels=2, buffer=512, devicename=None, allowedchanges=AUDIO_ALLOW_FREQUENCY_CHANGE | AUDIO_ALLOW_CHANNELS_CHANGE) -> None
        pygame.mixer.pre_init(22050, -16, 2, 32)
        self.screen = pygame.display.set_mode((0,0))#, pygame.FULLSCREEN)#(400, 800))#
        pygame.display.set_caption("ARTA")
        # set objects
        self.grid_manager.set_surface()
        self.rhythm_manager.set_player()
        self.focus_on_window()
        # Main Loop
        running = 1;
        while (running):
            events = pygame.event.get()
            for event in events:
                keys = pygame.key.get_pressed()
                if event.type == pygame.KEYDOWN:
                    self.focus_on_window()
                    self.input_manager.manage_key_inputs(event, keys)
                else:
                    pygame.event.set_grab(False)
            if self.play_set == False:
                self.play_set=True
            if self.test_set == False:
                self.test_set = True
            self.manage_game_states()

    def manage_game_states(self):
        """Manages the two game states - 0= test ; 1= play

        "return: nothing"""

        if self.game_state == 0:  # state test1
            if self.test_set == False:
                self.set_test()
            else:
                self.manage_test()

        if self.game_state == 1:  # state play
            if self.play_set == False:
                self.set_play()
            else:
                self.manage_play()

    #---------------------------------------------------------------------------------------------

    def manage_timer(self):
        """ This method is the central timer of the program. It manages the different aspects of the program and
        synchronizes them toguether. The method is organized in time interval sections: half-notes,
        notes, rhythmic pattern lenght (24 notes intervals) and other sections: performance,
        fine-tuning of the metronome sound.

        :return: nothing
        """
        self.timeNow = time.perf_counter()

        if self.timeNow - self.timeStart >= self.timerDelay * self.tempo:

            #grid_manager
            self.grid_manager.manage_surface()
            # ------------------------------HALF-NOTES----------------------------------------------
            #                  half-notes -  in the middle of two notes

            if self.notes[-1] >= -1 and self.ticks % self.time_division == \
                    self.time_division * 0.5:
                #
                # append char_idx ----> only when there is a char to press and no silence
                #
                if self.rhythm_manager.all_rhythmic_patterns[self.rhythm_manager.rhythmic_idx_p + 1][0] != 0:
                    self.grid_manager.char_idx += 1
                    self.grid_manager.char_idx = self.grid_manager.char_idx % 96

                    #append r_idx_to_press
                    self.rhythm_manager.r_idx_to_press += 1 #++++++++++++++++++++++++++++++++++++++++

                # append runit to self.perf_manager.runits_all list
                if self.notes[-1] >= -1:
                    runit = self.perf_manager.runits_4_patterns[self.rhythm_manager.rhythmic_idx_p]
                    self.perf_manager.runits_all.append(runit)
                    if self.notes[-1] >= 26:
                        print("")

                #----------------------PERFORMANCE SECTION--------------------------------------------------------------

                # set round start time
                if self.notes[-1] % 600 == 599:
                    self.next_round_start= time.perf_counter()

                 #set start time at the third note because at the end of each round,
                # the saving of output data happens at the second note - see section *** SAVE OUTPUT DATA *** afew lines below


                if self.notes[-1] % 600 == 599:
                    self.next_round_start = time.perf_counter()
                if self.notes[-1] % 600 == 3:   # start of each round. Rounds start at this time and ends when
                    # self.notes[-1] % 600 == 2. (reason: the performance of the last runit of a round is calculated 1
                    # runit later than it occurs and the output matrix needs 3 extra runits that will be striped before saved in file as raw-output-data)
                    self.round_start = self.next_round_start

                # calculate performance (and accuracy) of runit and average performance (and accuracy) of the previous runit(s)
                if self.notes[-1] >= 0:
                    self.perf_manager.calculate_performance(runit)
                    if self.notes[-1] >= 11:
                        self.perf_manager.calculate_perf_span(12, runit)
                        if self.notes[-1] >= 23:
                            self.perf_manager.calculate_perf_span(24, runit)
                            if self.notes[-1] >= 95:
                                self.perf_manager.calculate_perf_span(96, runit)
                                # runit - set half pattern attributes


                #calculate pattern performance and bpm average of all runits of the present half-rhythmic pattern
                if self.notes[-1] > 0 and self.notes[-1] % 12 == 0:
                    self.perf_manager.calc_av_perf_pattern()
                    self.perf_manager.calc_av_bpm_pattern()

                #adaptive mechanics
                runit.t_mod_step_up=self.perf_manager.t_modification_step/self.perf_manager.t_mod_step_max
                runit.t_mod_step_down = self.perf_manager.t_modification_step/self.perf_manager.t_mod_step_max


                #manage graph images in folder
                if self.notes[-1] > 0 and self.notes[-1] % 12 == 11:
                    self.manage_graph_images()

                #prepare training validation window to save (see in show_validation_tkwindow() method for details)
                if self.notes[-1] == 0:
                    self.window.show_validation_tkwindow()

                #********************* SAVE OUTPUT DATA ******************
                if self.notes[-1] % 600 == 2 and self.notes[-1] > 2: # end of each round
                    #set round end time
                    self.round_end=time.perf_counter()
                    #adapt time runit values  for neural_matrix
                    self.perf_manager.set_out_time_values()
                    #show data validation window
                    self.window.show_validation_tkwindow()
                    #resize neural_matrix
                    self.perf_manager.resize_runits_matrix()
                    #reset notes
                    self.notes = [-5, -4, -3, -2, -1, 0, 1, 2]
                    #adapt tempo
                    if self.mode == 1:
                        self.perf_manager.set_default_tempo()
                # *********************************************************
                    #append round values
                    self.round += 1
                    self.next_round += 1

                if self.notes[-1] >= 0:
                    runit = self.perf_manager.runits_all[self.notes[-2]]
                    if runit.time_pressed == 0.0 and runit.char != '':   #set error if the char wasn't pressed in time
                        runit.error=1.0
                        # set attributes related to errors
                        self.perf_manager.successes=0
                        self.perf_manager.manage_adaptive_mechanics(True)

                    # append the attributes of the previous runit to the neural_matrix
                    # and save relevant attributes to text file
                    self.save_array_to_txt(runit)

                # ----------------------PERFORMANCE SECTION--(END)------------------------------------------------------

                # ----------------------RHYTHMIC PATTERN LENGHT SECTION-------------------------------------------------

                if self.notes[-1] == 23 or \
                        (self.notes[-1] % 24 == 23 and self.notes[-1] > 0):

                    # start_distance conditions for way images
                    if self.grid_manager.start_distance == True:
                        self.grid_manager.start_distance = False

                    #append r_patterns_count
                    count= self.rhythm_manager.r_patterns_count[-1] + 1
                    self.rhythm_manager.r_patterns_count.append(count)

                    #append index in rhythmic pattern list self.grid_manager.day_now
                    self.rhythm_manager.day_now_idx += 1

                    # manage text indexes at the end of a trial
                    if self.notes[-1] > 0 and self.notes[-1] % 600 == 599:
                        if self.mode == 0: #training for the A.I.
                            self.grid_manager.manage_text_indexes()

                    # set next rhythmic pattern lists
                    if self.mode == 1 and  self.grid_manager.adapt_char_idx == True:
                        self.grid_manager.char_idx += 1
                        self.grid_manager.adapt_char_idx=False



                    self.grid_manager.update_lists(True)


            #---------------------FINE TUNING: SYNCHRONIZATION OF METRONOME SOUND---------------------------------------
            #play note with a little delay to compensate midi output latency

            self.ajust_playing_delay()

            #---------------------------------------NOTES SECTION-------------------------------------------------------
            #                         At the moment that notes are played

            if self.ticks % self.time_division == 0:

                # set rhythmic_idx_p
                if self.notes[-1] >= 0:
                    self.rhythm_manager.rhythmic_idx_p = (self.rhythm_manager.rhythmic_idx_p + 1) % 24
                    self.rhythm_manager.r_idx_to_press = self.rhythm_manager.rhythmic_idx_p

                #append note
                self.notes.append(self.notes[-1] + 1)

                # set runit attributes
                if self.notes[-1] >= 0 and self.notes[-1] <= 599:
                    runit = self.perf_manager.runits_4_patterns[self.rhythm_manager.rhythmic_idx_p]
                    runit.time_to_press = time.perf_counter()
                    runit.runit_bpm = self.bpm / self.max_bpm
                    runit.set_rvs()
            # ----------------------------------------------------------------------------------------------------------

            self.ticks += 1
            self.timeStart = self.timeNow

    def ajust_playing_delay(self):
        """
        Plays the metronome sound at the right time, considering the latency of the audio buffer
        and the delays caused by the graphics being saved in real-time. This is fined-tune to the best of my current knowledge and with trial and error,
        the following formula was found:
        :return: nothing
        """
        #formula:
        factor=  round(self.bpm / 50) % self.time_division
        factor2= (factor * 125 + 125) % 1000
        factor2= factor2 * 0.001

        # in those bpm values spans, the sound stops to play if the standard latency compensation (here below) is used. This is fine tuning.
        if (self.bpm >= 325 and self.bpm <= 385) or \
            self.bpm > 610:
            if self.ticks % self.time_division == 0:
                self.rhythm_manager.play_sound(0)

        #this is the standard latency compensation
        else:
            if self.ticks % self.time_division == self.time_division - self.time_division * factor2:
                self.rhythm_manager.play_sound(0)

        #Uncomment the following to see the trial and error process that I used to calculate the formula:
        pass

        #calculation of the formula through observations:

        # #if self.bpm <= 50:
        # if factor == 0:
        #     if self.ticks % self.time_division == self.time_division - self.time_division * 0.125:
        #         self.rhythm_manager.play_sound(0)
        # # elif self.bpm >= 51 and self.bpm <= 100:
        # if factor == 1:
        #     if self.ticks % self.time_division == self.time_division - self.time_division * 0.250:
        #         self.rhythm_manager.play_sound(0)
        # #elif self.bpm >= 101 and self.bpm <= 150:
        # if factor == 2:
        #     if self.ticks % self.time_division == self.time_division - self.time_division * 0.375:
        #         self.rhythm_manager.play_sound(0)
        # #elif self.bpm >= 151 and self.bpm <= 175:
        # if factor == 3:
        #     if self.ticks % self.time_division == self.time_division - self.time_division * 0.5:
        #         self.rhythm_manager.play_sound(0)
        # #elif self.bpm >= 176 and self.bpm <= 200:
        # if factor == 4:
        #     if self.ticks % self.time_division == self.time_division - self.time_division * 0.625:
        #         self.rhythm_manager.play_sound(0)
        # #elif self.bpm >= 201 and self.bpm <= 250:
        # if factor == 5:
        #     if self.ticks % self.time_division == self.time_division - self.time_division * 0.750: #at the end acc values lower
        #         self.rhythm_manager.play_sound(0)
        # #elif self.bpm >= 251 and self.bpm <= 300:
        # if factor == 6:
        #     if self.ticks % self.time_division == self.time_division - self.time_division * 0.875:
        #         self.rhythm_manager.play_sound(0)
        # #elif self.bpm >= 301 and self.bpm <= 350:
        # if factor == 7:
        #     if self.ticks % self.time_division == self.time_division - self.time_division:
        #         self.rhythm_manager.play_sound(0)

    def manage_graph_images(self):
        """
        Saves the performance graphics in the folder at the end of each test sections and each 4 parts of the training.

        :return: nothing
        """
        file_name=""
        date_time= self.perf_manager.get_time_date()

        test = True
        pair_idx= self.grid_manager.chr_pair_idx + 1
        test=False

        if self.mode == 0 and self.notes[-1] % 600 == 23:   # test 1
            file_name = f"T1-{pair_idx}"
            test = True
        elif self.mode == 1 and self.notes[-1] % 600 == 47:  # test 1 - test 1 is one pattern later in mode 1
            file_name = f"T1-{pair_idx}"
            test = True
        elif self.notes[-1] % 600 == 143:       # part 1
            file_name = f"P1-{pair_idx}"
        elif self.notes[-1] % 600 == 167:  # test 2
            file_name = f"T2-{pair_idx}"
            test = True
        elif self.notes[-1] % 600 == 287:       # part 2
            file_name = f"P2-{pair_idx}"
        elif self.notes[-1] % 600 == 311:  # test 3
            file_name = f"T3-{pair_idx}"
            test = True
        elif self.notes[-1] % 600 == 431:        # part 3
            file_name = f"P3-{pair_idx}"
        elif self.notes[-1] % 600 == 455:  # test 4
            file_name = f"T4-{pair_idx}"
            test = True
        elif self.notes[-1] % 600 == 575:       # part 4
            file_name = f"P4-{pair_idx}"
        elif self.notes[-1] % 600 == 599 and self.notes[-1] > 0: # test 5
            file_name = f"T5-{pair_idx}"
            test = True
        else:
            return
        # save stats as image
        self.perf_manager.show_save_stats(f"{date_time}-{file_name}", False, test )

    # --------------------------------------------------------------------------------------------
    # GAME STATES
    # ---------------------------------------------------------------------------------------------

    def set_play(self):
        """
        Sets the game state play according to the current one (0 or 1) entered in the main function.

        :return: nothing
        """
        self.perf_manager.set_initial_tempo()
        self.rhythm_manager.set_rm()
        self.grid_manager.resize_text()

        if self.mode == 1:
            self.grid_manager.char_idx -= 1
            self.rhythm_manager.lr_keys_on=False
            self.max_bpm = 1000

        self.grid_manager.set_surface()

        # important to set before self.manage_game_states()
        self.play_set = True
        self.manage_game_states()

    def manage_play(self):
        """
        Manages the game state play.
        """
        self.manage_timer()

    def finalize_play(self):
        """Exits program"""
        exit()

    def set_test(self):
        """
        Sets the game state test by starting the live graphics and th pygame window.
        """
        self.start_multi_processes()

    def manage_test(self):
        """
        Manages the game state test.
        """
        self.grid_manager.manage_surface()

    def finalize_test(self):
        """
        Finalizes the game state test.
        """
        # reset values
        self.grid_manager.char_idx=0
        self.game_state=1
        self.test_done=True
        self.set_play()

    # ---------------------------------------------------------------------------------------------


    def start_multi_processes(self):
        """
        Manages the multi-processing of pygame and the live graphics, so that they can be run at the same time.
        """
        iteration = 0
        processes = []

        #start time
        self.timeStart = time.perf_counter()

        multiprocessing.freeze_support()

        # parameters graphics
        for i in range(self.tot_graphs):
            self.this_graphs_idx += 1
            p = Process(target=self.runGraph, args=( self.this_graphs_idx,))
            processes.append(p)

        # pygame
        p = Process(target=self.StartPygame)
        processes.append(p)

        for process in processes:
            process.start()

            # commands between

        for process in processes:
            process.join()

    def runGraph(self, graph_id):
        # source of structure: https://stackoverflow.com/questions/51949185/non-blocking-matplotlib-animation
        """Runs the live graphics.

        :param graph_id: The ID number of this graphic.
        :return: nothing
        """

        sw, sh = pyautogui.size()
        graph_dimX = sw * 0.333333
        graph_dimY = sh / self.tot_graphs * 0.5

        x_dim = 50
        y_dim = 50
        # Parameters
        print('show')
        x_len = x_dim  # Number of points to display
        y_range = [0, y_dim]  # Range of possible Y values to display

        # Create figure for plotting
        fig = plt.figure(figsize=(graph_dimX * 0.01, graph_dimY * 0.01), dpi=100)
        # self.window.graphs_in_canvas(fig)

        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlim(left=0, right=20)
        ax.set_ylim(bottom=0, top=1)
        xs = list(range(0, x_dim))
        ys = [0] * x_len
        ax.set_ylim(y_range)

        # Create a blank line
        line, = ax.plot(xs, ys, color="b", lw=4)

        def animate(i, ax,):
            """
            Animates the current graphic.

            :param i: number of iterations
            :param ax: the axis of the plt figure fig in runGraph method.
            :return: the graphic line that is being plotted.
            """
            # append data
            self.x_coor.append(self.ticks)

            values = open('Graphs/graphs_data.txt', 'r+')
            rline = values.readline()
            rlines = rline.split(',')


            #append value to graph according to its index
            if len(rlines) >= 2:
                value=0.0
                if graph_id == 1: #accuracy
                    value = float(rlines[0])
                if graph_id == 2: #performance
                    value = float(rlines[1])
                if graph_id == 3:# performance_24
                    value = float(rlines[2])
                if graph_id == 4: # bpm
                    value = float(rlines[3])
                    print("bpm - anim= ",  value)
                if graph_id == 5: # error
                    value = float(rlines[4])

                self.y_coor.append(value)
                #values.close()
            else:
                self.y_coor.append(0.0)


            self.ticks += 1  # ticks value of this graph

            # delete and reset line
            if self.ticks % x_dim == x_dim - 1:
                # plt.clf()
                ax.cla()
                ax.plot(self.x_coor[:i], self.y_coor[:i], color='b', lw=3)  # adjust axis values

                # ax = fig.add_subplot(1, 1, 1)
                l1 = self.ticks
                l2 = self.ticks + x_dim
                ax.set_xlim(left=l1, right=l2)
                if graph_id == 1 and rlines[0] != '' and value != value:
                    value = float(rlines[3])
                    ax.set_ylim(bottom=0, top=value) # top= perf_manager.max_bpm (max bpm reached during this game)
                else:
                    ax.set_ylim(bottom=0, top=1)

                # Add labels and positions
                if graph_id == 1:  # accuracy
                    plt.title('Accuracy')
                    plt.xlabel('Time')
                    plt.ylabel('Accuracy')
                if graph_id == 2:  # performance
                    plt.title('Performance-Note')
                    plt.xlabel('Time')
                    plt.ylabel('Performance')
                if graph_id == 3:
                    plt.title('Performance-24-Notes')
                    plt.xlabel('Time')
                    plt.ylabel('Performance')
                if graph_id == 4:
                    plt.title('Typing-Speed')
                    plt.xlabel('Time')
                    plt.ylabel('Chars/Min.')
                if graph_id == 5:
                    plt.title('Errors')
                    plt.xlabel('Time')
                    plt.ylabel('Errors')

                plt.show()

                # graphs positions
                if graph_id == 1:  # accuracy
                    self.move_figure(fig, graph_dimX * 1.58, graph_dimY * 2)
                if graph_id == 2:  # performance
                    self.move_figure(fig, graph_dimX * 0.4, graph_dimY * 2)
                if graph_id == 3:  # performance_24
                    self.move_figure(fig, graph_dimX * 0.4, graph_dimY * 0.4)

            # Update line with new Y values
            line.set_xdata(self.x_coor[-x_dim:])
            line.set_ydata(self.y_coor[-y_dim:])
            self.current_fig = fig

            return line,


        # Set up plot to call animate() function periodically

        ani = FuncAnimation(fig,
                            animate,
                            fargs=(ax,),
                            interval=125,
                            blit=True)
        plt.show()

    def save_array_to_txt(self, runit):
        """
        Saves the relevant parameters of the runit in the self.perf_manager.neural_matrix and in the text
        file related to the live graphics (Graphs/graphs_data.txt).

        :param runit: the runit of the current note.
        :return: nothing
        """
        file = open('Graphs/graphs_data.txt', "a+")
        #if self.notes[-1] == 0:
        file.truncate(0)

        if self.notes[-1] >= 1:
            self.perf_manager.neural_matrix= np.insert(
                self.perf_manager.neural_matrix,
                -1,
                0.0,
                axis=0)

            #append runit values to the neural_matrix
            self.perf_manager.neural_matrix[self.notes[-2]][0] = runit.runit_bpm
            self.perf_manager.neural_matrix[self.notes[-2]][1] = runit.t_modification_frq
            self.perf_manager.neural_matrix[self.notes[-2]][2] = runit.time_to_press
            self.perf_manager.neural_matrix[self.notes[-2]][3] = runit.time_pressed
            self.perf_manager.neural_matrix[self.notes[-2]][4] = runit.accuracy
            self.perf_manager.neural_matrix[self.notes[-2]][5] = runit.accuracy_average_12
            self.perf_manager.neural_matrix[self.notes[-2]][6] = runit.accuracy_average_24
            self.perf_manager.neural_matrix[self.notes[-2]][7] = runit.acc_av_0_5_pattern
            self.perf_manager.neural_matrix[self.notes[-2]][8] = runit.performance
            self.perf_manager.neural_matrix[self.notes[-2]][9] = runit.performance_average_12
            self.perf_manager.neural_matrix[self.notes[-2]][10] = runit.performance_average_24

            #------------------values that appear in the performance results--------------------------------------------
            #          (SECTION: evaluation and optimization of parameters - in main.py)

            self.perf_manager.neural_matrix[self.notes[-2]][11] = runit.perf_av_0_5_pattern
            self.perf_manager.neural_matrix[self.notes[-2]][12] = runit.rhythmic_value
            self.perf_manager.neural_matrix[self.notes[-2]][13] = runit.rv1
            self.perf_manager.neural_matrix[self.notes[-2]][14] = runit.rv2
            self.perf_manager.neural_matrix[self.notes[-2]][15] = runit.rv3
            self.perf_manager.neural_matrix[self.notes[-2]][16] = runit.rv4
            self.perf_manager.neural_matrix[self.notes[-2]][17] = runit.rv5
            self.perf_manager.neural_matrix[self.notes[-2]][18] = runit.rv6
            self.perf_manager.neural_matrix[self.notes[-2]][19] = runit.rv7
            self.perf_manager.neural_matrix[self.notes[-2]][20] = runit.rv8
            self.perf_manager.neural_matrix[self.notes[-2]][21] = runit.rv9
            self.perf_manager.neural_matrix[self.notes[-2]][22] = runit.rv10
            self.perf_manager.neural_matrix[self.notes[-2]][23] = runit.rv11
            self.perf_manager.neural_matrix[self.notes[-2]][24] = runit.rv12
            self.perf_manager.neural_matrix[self.notes[-2]][25] = runit.t_mod_step_up
            self.perf_manager.neural_matrix[self.notes[-2]][26] = runit.t_mod_step_down
            self.perf_manager.neural_matrix[self.notes[-2]][27] = runit.bpm_av_0_5_pattern

            # --------------- values that appear in the performance results---END--------------------------------


            #write graph values in text file
            file.write(f"{round(runit.accuracy, 4)},{round(runit.performance, 4)},"
                       f"{round(runit.performance_average_24, 4)},{round(runit.runit_bpm, 4)},{round(runit.error, 4)}")

            # print("runit.error = ", runit.error)
            # print("runit.error = ", self.perf_manager.neural_matrix[self.notes[-2]][5])
            os.fsync(file.fileno())

    def load_day(self):
        """
        Loads the current day of training (1 or 2)
        """
        time_date = self.perf_manager.get_time_date()

        txt = open('Performance/performance_data.txt', 'r+', encoding="utf8")
        rlines = txt.readlines()
        txt_str = rlines[-1]
        txt_split = txt_str.split('|')

        #first practice
        if len(txt_split) == 2 and txt_split[-2] == "day 1":
            #write today's date
            txt.write(f"{time_date}|")
            txt.write(f"day 2|")
            txt.close()

            #read new line
            txt = open('Performance/performance_data.txt', 'r+', encoding="utf8")
            rlines = txt.readlines()
            txt_str = rlines[-1]
            txt_split = txt_str.split('|')
            day= int(txt_split[-4][-1])
            txt.close()
            return day

        #get day - all other practices
        date= txt_split[-3]
        date= date[0:10]
        date_now= time_date[0:10]

        if date != date_now:
            day = int(txt_split[-2][-1])
            # write new day
            next_day = 0
            if day == 1:
                next_day = "day 2|"
            else:
                next_day = "day 1|"
            txt.write(f"{time_date}|")
            txt.write(next_day)
            txt.close()

        #practice the same day
        else:
            day = int(txt_split[-4][-1])

        return day

    #source: https://newbedev.com/how-do-you-set-the-absolute-position-of-figure-windows-with-matplotlib
    def move_figure(self, f, x, y):
        """
        Move figure's upper left corner to pixel (x, y)

        :param f: the figure (live graphic)
        :param x: x position
        :param y: y position
        :return: nothing
        """

        backend = matplotlib.get_backend()
        if backend == 'TkAgg':
            f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
        elif backend == 'WXAgg':
            f.canvas.manager.window.SetPosition((x, y))
        else:
            # This works for QT and GTK
            # You can also use window.setGeometry
            f.canvas.manager.window.move(x, y)
