"""
Project: Adaptive Rhythmic Training Application (ARTA)
File   : performancemanager.py
Date   : 21/01/2022
Author : Yann Savard

This code is open source, except for some parts that were taken
from external sources and their sources are mentioned in the code.

History: programmed from september 2021 to february 2022 as part of my bachelor project:
"Conception and Evaluation of New Rhythm-Based Dexterity Training Methods with Adaptive Game Mechanics and AI"
"""

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

#inputs
import pyautogui
import pynput
from pynput.mouse import Button, Controller

#pygame
import pygame

#e-mail
import socket
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

#time
import time
import datetime

#images
#from colorsys import hsv_to_rgb
import os
from PIL import Image

#various
import math
import random as rnd


class PerformanceManager():
    def __init__(self, g_manager):
        self.gm = g_manager
        self.grm = self.gm.grid_manager
        self.rm = self.gm.rhythm_manager
        self.ann = None
        self.runits_all=[]
        self.runits_4_patterns=[]
        self.stats_colors=['b','g','r','m','c','y','k', (100,100,100), (150,150,150), (175, 175, 175), (255,255,0), (255,0, 255)]
        self.labels = [
            "accuracy","performance",
            "performance_24","runit_bpm",
            "error", "bpm(max)", "time_to_press",
            "time_pressed","neural_char_value"]

        # performance
        self.initial_bpm= 0.0 # bpm value measured after the initial test
        self.max_bpm=0.0 # maximum speed in bpm allowed by the program
        self.accuracy_values=[] # list of accuracy values of each runit as they are calculated each note
        self.performance_values=[] # list of performance values of each runit as they are calculated each note
        self.errors=[] # list of errors of all runits as they occur
        self.pressed_times = [] # list of pressed times for each runit if they are presssed, otherwise, the value is 0.0.

        # adaptive mechanics
        self.t_modification_frq = 2 # frequence at which the the tempo value can be modified with the adaptive mechanic
        self.t_mod_frq_max = 8 # max value of self.t_modification_frq
        self.t_mod_frq_min= 1 # min value of self.t_modification_frq
        self.successes=0 # number of runits successfully pressed in a row

        self.t_modification_step=1 # max bpm that can be added or
                                      # subtracted every x notes (x= self.t_modification_frq)
        self.t_mod_step_min= 0 # min value of self.t_modification_step
        self.t_mod_step_max = 5 # max value of self.t_modification_step
        self.t_mod_error_factor=1.0

        self.lr_keys_on= True # True if left and right arrows are enabled

        # output data matrix
        self.nn_matrix_params= 28 # number of parameters for each runit (for the output data matrix)
        self.arr_shape=(2,self.nn_matrix_params)
        self.neural_matrix=np.zeros(2 * self.nn_matrix_params).reshape(*self.arr_shape)

        # raw input data (loaded from file from files in raw-output-data folder)
        self.raw_input_data=None

        # datasets attributes
        self.data_set_shape_x = (1, 25, self.nn_matrix_params, 1) # self.nn_matrix_params=28
        self.data_set_x = np.zeros(self.data_set_shape_x)
        self.data_set_shape_y = (1, self.nn_matrix_params)
        self.data_set_y = np.zeros(self.data_set_shape_y)
        self.data_set_idx=0
        self.all_data_x=np.zeros(self.data_set_shape_x)
        self.all_data_y = np.zeros(self.data_set_shape_y)
        self.data_set_files=0 #number of data set files in directory path "Performance/performance_data/data_set"
        self.ds_files_idx = 0 #index of currently processed data set file

        #to save output data
        self.data_set_folder=''
        self.server= ""
        self.pseudo_name=''
        self.data_valid= False
        self.continue_training=False

        self.colors=[] # colors list for graphics

        #evaluation of rhythmic methods after the evaluation training of mode 1
        self.param_values_day1 = []
        self.param_values_day2 = []
        self.t1_1, self.t1_2 = [], []
        self.p1_1, self.p1_2 = [], []
        self.t2_1, self.t2_2 = [], []
        self.p2_1, self.p2_2 = [], []
        self.t3_1, self.t3_2 = [], []
        self.p3_1, self.p3_2 = [], []
        self.t4_1, self.t4_2 = [], []
        self.p4_1, self.p4_2 = [], []
        self.t5_1, self.t5_2 = [], []

        self.bpm_total_day_1 = 0.0
        self.bpm_total_day_2 = 0.0
        self.acc_total_day_1 = 0.0
        self.acc_total_day_2 = 0.0
        self.perf_total_day_1 = 0.0
        self.perf_total_day_2 = 0.0


    def manage_t_modification_frq(self, value):
        """
        Modifies the attribute self.t_modification_frq
        :param value: value to set self.t_modification_frq
        :return: nothing
        """
        #positive value
        if self.t_modification_frq + value > self.t_mod_frq_max or \
            self.t_modification_frq + value < self.t_mod_frq_min:
            return
        self.t_modification_frq += value


    def manage_adaptive_t_modification_step(self, value):
        """
              Modifies the attribute self.t_modification_step
              :param value: value to set self.t_modification_step
              :return: nothing
              """
        # positive value
        if self.t_modification_step + value > self.t_mod_step_max or \
                self.t_modification_step + value < self.t_mod_step_min:
            return
        self.t_modification_step += value

    def get_adapt_params_activation(self):
        """
        Manages if a new tempo should be set in method manage_adaptive_mechanics.
        :return: True if new tempo should be set, False if not.
        """
        if self.successes == self.t_modification_frq:
            self.successes=0
            return True
        else:
            return False

    def manage_adaptive_mechanics(self, error):
        """
        Part of the adaptive mechanic that manages the tempo changes.
        :param error: True if a mistake was made during the training.
        :return:
        """
        if error == False:
            set_vars= self.get_adapt_params_activation()
            if set_vars:
                self.rm.set_tempo_values(self.t_modification_step)
        # each error causes the tempo to decrease x times more the self.t_modification_step value
        # (x being self.t_mod_error_factor)
        else:
            self.rm.set_tempo_values(-self.t_modification_step * self.t_mod_error_factor)

    def calculate_accuracy(self, runit):
        """
        Calculates the timing accuracy with which the present runit has been pressed during the training.
        :param runit: runit that should be pressed now
        :return: The accuracy
        """
        max_delay=self.gm.tempo * 0.5 # accuracy = 0
        min_delay= 0.0 # accuracy= 1
        pressed_delay= abs(runit.time_pressed - runit.time_to_press)

        if pressed_delay <= max_delay:
            acc = abs(1 - pressed_delay / max_delay)
            runit.accuracy = round(acc, 4)
            runit.accuracy =  min(runit.accuracy * 1.3, 1.0)
        else:
            runit.accuracy=0.0

        self.accuracy_values.append(runit.accuracy)

        return runit.accuracy

    def calculate_performance(self, runit):
        """
        Calculates the performance of the present runit, according to the accuracy and tempo.
        :param runit: runit that should be pressed now
        :return:
        """
        accuracy=self.calculate_accuracy(runit)
        if runit.error == 0 and accuracy > 0.000:
            runit.performance= (accuracy * self.gm.bpm)/(1 * self.gm.max_bpm)
            runit.performance= min(runit.performance, 1)
            self.performance_values.append(runit.performance)
            #print("performance= ",runit.performance, "max_bpm= ", self.max_bpm)

        #accuracy and performance are 0.0
        else:
            if runit.char != '':
                #set attributes related to errors
                runit.error=1.0
                self.successes = 0
                self.manage_adaptive_mechanics(True)

            self.accuracy_values.append(runit.accuracy)
            self.performance_values.append(runit.performance)

    def calculate_perf_span(self, average_span, runit):
        """
        Calculates the performance, accuracy, bpm and error averages of the present runit.
        :param average_span: number of previous runits to consider(inclusing the present runit)
        :param runit: runit that should be pressed now
        :return:
        """
        average_bpm= 0.0
        average_acc= 0.0
        average_perf=0.0
        average_error=0.0

        idx= self.gm.notes[-1] - average_span

        for i in range(idx, self.gm.notes[-1]):
            average_bpm += self.runits_all[i].runit_bpm
            average_acc += self.runits_all[i].accuracy
            average_perf += self.runits_all[i].performance
            average_error += self.runits_all[i].error

        if average_span == 12:
            runit.bpm_average_12 = average_bpm/12
            runit.accuracy_average_12= average_acc/12
            runit.performance_average_12 = average_perf/12
            runit.error_average_12 = average_error/12


        if average_span == 24:
            runit.bpm_average_24 = average_bpm/24
            runit.accuracy_average_24 = average_acc/24
            runit.performance_average_24 = average_perf/24
            runit.error_average_24 = average_error/24

        if average_span == 96:
            runit.bpm_average_96 = average_bpm / 96
            runit.accuracy_average_96 = average_acc / 96
            runit.performance_average_96 = average_perf / 96
            runit.error_average_96 = average_error / 96


    def calc_av_perf_pattern(self):
        """Calculates the average performance of this pattern half.
        The value is the same for all runits of this pattern half"""
        perf_12= self.runits_all[-2].performance_average_12
        acc_12= self.runits_all[-2].accuracy_average_12
        for i in range(1, 13):
            idx1=(i+1)
            self.runits_all[-idx1].perf_av_0_5_pattern=perf_12
            self.runits_all[-idx1].acc_av_0_5_pattern = acc_12
            self.neural_matrix[-i][11] = perf_12
            self.neural_matrix[-i][7] = acc_12


    def calc_av_bpm_pattern(self):
        """Calculates the average bpm of this pattern half.
        The value is the same for all runits of this half of pattern"""

        idx = self.gm.notes[-1] - 12
        average_bpm=0.0
        #calculate average
        for i in range(idx, self.gm.notes[-1]):
            average_bpm += self.runits_all[i].runit_bpm

        average_bpm= average_bpm * 0.0833333 # 0.0833333 = 1/12
        average_bpm *= 3.0 # amplify value for the neural network.

        #set average for all 12 last runits
        for i in range(1, 13):
            idx1 = (i + 1)

            self.runits_all[-idx1].bpm_av_0_5_pattern = average_bpm
            self.neural_matrix[-i][27] = average_bpm


    def resize_runits_matrix(self):
        """
        Resize self.runits_all to a size of 600 and the neural matrix to a shape of (600, 28)
        """
        if len(self.runits_all) >= 604:
            for i in range(600):
                del self.runits_all[0]
                #start deleting 3 runits later for the matrix,
                # because 3 were deleted in the method
                # self.save_output_data()
                if i >= 3:
                    self.neural_matrix = np.delete(self.neural_matrix, 0, axis=0)

    def set_out_time_values(self):
        """Converts neural_matrix time values to a span of 0.0 to 1.0"""

        idx=0
        for runit in self.runits_all:
            if idx > 0:
                if  runit.time_pressed != 0.0:
                    runit.time_pressed= (runit.time_pressed - self.gm.round_start) / (self.gm.round_end - self.gm.round_start)

                if idx < len(self.runits_all) - 3: # value at this index is the last runit in the neural_matrix
                    runit.time_to_press = (runit.time_to_press - self.gm.round_start) / (self.gm.round_end - self.gm.round_start)
                else:
                    pass

                idx_matrix = idx - 1
                if idx > 0:
                    #time_to_press
                    self.neural_matrix[idx_matrix][2] = runit.time_to_press
                    #time_pressed
                    self.neural_matrix[idx_matrix][3] = runit.time_pressed

            idx += 1


    #source: https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    def get_performance_data_files(self,path):
        """
        Returns a list of all files in the given path.
        :param path: folder path
        :return: list of all files
        """
        # in folder path
        files = []
        for name in os.listdir(path):
            if os.path.isfile(os.path.join(path, name)):
                files.append(name)
        return files


    def show_methods_evaluation(self, day, stats_kind, parameter):
        """
        Generates and saves graphics that compare the training results of day 1 (in blue) and 2 (in green) of evaluation training sessions in self.gm.mode 1 and 2.

        :param day: day 1 or day 2 of training sessions.
        :param stats_kind: sections_averages_curves or all_training_averages
        :param parameter: parameter to evaluate (
                          parameter 0= runit.runit_bpm
                          parameter 4= runit.accuracy
                          parameter 8= runit.performance)
        :return: nothing
        """
        # get all folders
        if day == 1:
            files = self.get_performance_data_files("Performance/performance_data/raw_output_data_day_1")
        else:
            files = self.get_performance_data_files("Performance/performance_data/raw_output_data_day_2")

        self.data_set_files = len(files)

        total_day_1 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        total_day_2 = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        for i in files:
            file_name = i
            if day == 1:
                self.raw_input_data = np.loadtxt(f'Performance/performance_data/raw_output_data_day_1/{file_name}',
                                             delimiter=",")
            else:
                self.raw_input_data = np.loadtxt(f'Performance/performance_data/raw_output_data_day_2/{file_name}',
                                                 delimiter=",")

            t1_list, p1_list, t2_list, p2_list, t3_list, p3_list, t4_list, p4_list, t5_list = [],[],[],[],[],[],[],[],[]

            for j in range(600):


                if j > 23 and j <= 47:  # test 1
                    t1_list.append(float(self.raw_input_data[j][parameter]))
                    p1_list.append(0.0) # add 24 runits to part one with value 0, because it has only 96 runits
                elif j > 47 and j <= 143:  # part 1
                    p1_list.append(float(self.raw_input_data[j][parameter]))

                if j > 143 and j <= 167:  # test 2
                    t2_list.append(float(self.raw_input_data[j][parameter]))
                elif j > 167 and j <= 287:  # part 2
                    p2_list.append(float(self.raw_input_data[j][parameter]))
                elif j > 287 and j <= 311: # test 3
                    t3_list.append(float(self.raw_input_data[j][parameter]))
                elif j > 311 and j <= 431:  # part 3
                    p3_list.append(float(self.raw_input_data[j][parameter]))
                elif j > 431 and j <= 455:  # test 4
                    t4_list.append(float(self.raw_input_data[j][parameter]))
                elif j > 455 and j <= 575:  # part 4
                    p4_list.append(float(self.raw_input_data[j][parameter]))
                elif j > 575 and j <= 599:  # test 5
                    t5_list.append(float(self.raw_input_data[j][parameter]))

            #calculate average values
            t1, t2, t3, t4, t5 = 0, 0, 0, 0, 0
            for k in range(24):
                if k > 11:
                    t1 += t1_list[k]
                    t2 += t2_list[k]
                    t3 += t3_list[k]
                    t4 += t4_list[k]
                    t5 += t5_list[k]
            t1 /= 12
            t2 /= 12
            t3 /= 12
            t4 /= 12
            t5 /= 12

            p1, p2, p3, p4 = 0, 0, 0, 0
            for k in range(120):
                if k <= 95:
                    p1 += p1_list[k]
                else:
                    p1 += 0
                p2 += p2_list[k]
                p3 += p3_list[k]
                p4 += p4_list[k]

                # general note for trainings 1 and 2 (modes 1 and 2):
                # the silences in the rhythmic patterns of parts 1 and 3 (value= 0.0)
                # are only considered to calculate the accuracy averages, not the performance and bpm averages

            #------------------------------MODE 1 --- training 1 -----------------------------------------------------

            if self.gm.mode == 1:
                # parts 1 and 3
                if parameter == 4: # accuracy
                    if day == 1:
                        p1 /= (96 - 32) # day 1 has 32 silences in part 1
                        p3 /= (120 - 16)  # day 1 has 16 silences in part 3
                    else:          # performance and bpm
                        p1 /= (96 - 33) # day 2 has 33 silences in part 1
                        p3 /= (120 - 21)  # day 2 has 21 silences in part 3

                else:              # performance and bpm
                    p1 /= 96
                    p3 /= 120

            #------------------------------MODE 2--- training 2 ------------------------------------------------------

            if self.gm.mode == 2:
                # parts 1 and 3
                if parameter == 4:  # accuracy
                    # day 1 and 2 have 18 silences in parts 1 and 3
                    p1 /= (96 - 18)
                    p3 /= (120 - 18)
                else:               # performance and bpm
                    p1 /= 96
                    p3 /= 120

            #-------------------------------------------Modes 1 and 2 --------------------------------------------------

            # part 2
            p2 /= 120

            # part 4
            p4 /= 120



            temp = [t1, p1, t2, p2, t3, p3, t4, p4, t5]
            max_temp= max(temp)
            # -------------------------AVERAGE PERFORMANCE GROUPED IN PARTS FOR EACH DAY (1 and 2)--* SECTION 1 *-----------

            if stats_kind == "sections_averages_curves":
                if day == 1:
                    self.t1_1.append(t1)
                    self.p1_1.append(p1)
                    self.t2_1.append(t2)
                    self.p2_1.append(p2)
                    self.t3_1.append(t3)
                    self.p3_1.append(p3)
                    self.t4_1.append(t4)
                    self.p4_1.append(p4)
                    self.t5_1.append(t5)
                else:
                    self.t1_2.append(t1)
                    self.p1_2.append(p1)
                    self.t2_2.append(t2)
                    self.p2_2.append(p2)
                    self.t3_2.append(t3)
                    self.p3_2.append(p3)
                    self.t4_2.append(t4)
                    self.p4_2.append(p4)
                    self.t5_2.append(t5)

        #------------------------------AVERAGE PERFORMANCE FOR EACH DAY (1 and 2)---------------------------------------
            if stats_kind == "all_training_average":
                # calculate average of list values of each index (each round section)
                if day == 1:
                    for i in range (9):
                        total_day_1[i] += temp[i]
                else:
                    for i in range(9):
                        total_day_2[i] += temp[i]

        #calculate average values of all files combines
        if stats_kind == "all_training_average":
            if day == 1:
                for i in range(9):
                    total_day_1[i] /= len(files)
                self.param_values_day1 = total_day_1
            else:
                for i in range(9):
                    total_day_2[i] /= len(files)
                self.param_values_day2 = total_day_2

                self.show_all_training_average(parameter, day)
        # --------------------------------------------------------------------------------------------------------------
        # -------------------------AVERAGE PERFORMANCE GROUPED IN PARTS FOR EACH DAY (1 and 2)--* SECTION 2 *-----------
        if stats_kind == "sections_averages_curves":
            if day == 2:
                self.show_sections_averages_curves(parameter)
                self.clear_evaluation_lists()


    def show_all_training_average(self, parameter, day):
        """
        Generates a cumulation of averages of all rounds of evaluation trainings for the parameters
        speed, accuracy or performance. (in blue: day 1; in green: day 2)
        :param parameter: parameter to evaluate (
                          parameter 0= runit.runit_bpm
                          parameter 4= runit.accuracy
                          parameter 8= runit.performance)
        :param day: day 1 or 2 of the evaluation training (self.gm.mode 1 or 2)
        :return: nothing
        """
        # x  axis
        x = np.arange(27)

        # y  axis
        results = []
        colors= []

        # add all the parameter values for the total averages
        #----------------------------------------------------
        tot_day1= 0.0
        tot_day2 = 0.0
        for i in range(9):
            tot_day1 += self.param_values_day1[i]
            tot_day2 += self.param_values_day2[i]

        tot_day1 /= 9
        tot_day2 /= 9

        if parameter == 0:
            self.bpm_total_day_1 = tot_day1 * 100 # show results in percent
            self.bpm_total_day_2 = tot_day2 * 100
        if parameter == 4:
            self.acc_total_day_1 = tot_day1 * 100
            self.acc_total_day_2 = tot_day2 * 100
        if parameter == 8:
            self.perf_total_day_1 = tot_day1 * 100
            self.perf_total_day_2 = tot_day2 * 100
        #----------------------------------------------------

        # combine results of day 1 as a single list for the graphic

        for j in range(len(self.param_values_day1)):
            if parameter == 0:
                results.append(self.param_values_day1[j] * 750) # show results in bpm
            else:
                results.append(self.param_values_day1[j] * 100) # show results in percent
            colors.append('b')
            if parameter == 0:
                results.append(self.param_values_day2[j] * 750)
            else:
                results.append(self.param_values_day2[j] * 100)
            colors.append('g')
            results.append(0)
            # red color ('r') will not appear, the value is 0, but the list needs the same number of values as results list.
            colors.append('r')


        fig, ax = plt.subplots()
        ax.bar(x, results, color=colors)
        # fig.suptitle('Results for both rhythmic training methods')

        if parameter == 0:
            param_str = "BPM"
        if parameter == 4:
            param_str = "Accuracy"
        if parameter == 8:
            param_str = "Performance"

        img_name = f"Performance/performance_data/evaluation_graphics/averages_all_training-{param_str}.png"
        plt.savefig(img_name, dpi=100)
        # plt.show()

    def show_parameter_totals(self):
        """
        Saves a graphic (plt figure) with the average performance
        for each part of the training accomplished on day 1 and 2 as colored bars (blue= day 1; green= day 2)
        (files loaded from path 'Performance/performance_data/raw_output_data folder'
        save to path: 'Performance/performance_data/evaluation_graphics'
        :return:
        """
        # x  axis
        x = np.arange(9)

        # y  axis
        results = []
        colors = []

        # combine results of day 1 as a single list for the graphic

        # bpm
        results.append(0.0)
        colors.append('r')   # red color ('r') will not appear, the value is 0,
                             # but the list needs the same number of values as results list.
        results.append(self.bpm_total_day_1)
        colors.append('b')
        results.append(self.bpm_total_day_2)
        colors.append('g')
        results.append(0)
        colors.append('r')
        # accuracy
        results.append(self.acc_total_day_1)
        colors.append('b')
        results.append(self.acc_total_day_2)
        colors.append('g')
        results.append(0)
        colors.append('r')

        # performance
        results.append(self.perf_total_day_1)
        colors.append('b')
        results.append(self.perf_total_day_2)
        colors.append('g')

        print(f"Difference between day 1 and day 2: {(1 - self.perf_total_day_2/self.perf_total_day_1) * 100} %")

        fig, ax = plt.subplots()
        ax.set_xlim(left=0, right=len(results))
        ax.set_ylim(bottom=0, top=100)
        ax.bar(x, results, color=colors)

        img_name = f"Performance/performance_data/evaluation_graphics/averages_all_training-BPM-ACC-PERF_day1_day2.png"
        plt.savefig(img_name, dpi=100)

    # source of syntax for figure plotting: https://geog0111.readthedocs.io/en/latest/Chapter2_Numpy_matplotlib.html
    def show_sections_averages_curves(self, parameter):
        """ Saves a graphic (plt figure) with the average performance
        for each part of the training accomplished on day 1 and 2 as colored bars (blue= day 1; green= day 2)
        (files loaded from path 'Performance/performance_data/raw_output_data folder'
        save to path: 'Performance/performance_data/evaluation_graphics'

        Graphics parameters:
                          Left= parameter 0 (runit.runit_bpm_
                          Center= parameter 4 (runit.accuracy)
                          Right parameter 8 (runit.performance)"""

        # set graphic dimensions
        sw, sh = pyautogui.size()
        graph_dimX = sw * 0.5
        graph_dimY = sh * 0.5

        lists_lenght= len(self.t1_1) # lenght of all self.t... and self.p... lists

        #test 1
        for i in range(9):
            listDay_1 = []
            listDay_2 = []

            if i == 0:
                listDay_1 = self.t1_1
                listDay_2 = self.t1_2
            if i == 1:
                listDay_1 = self.p1_1
                listDay_2 = self.p1_2
            if i == 2:
                listDay_1 = self.t2_1
                listDay_2 = self.t2_2
            if i == 3:
                listDay_1 = self.p2_1
                listDay_2 = self.p2_2
            if i == 4:
                listDay_1 = self.t3_1
                listDay_2 = self.t3_2
            if i == 5:
                listDay_1 = self.p3_1
                listDay_2 = self.p3_2
            if i == 6:
                listDay_1 = self.t4_1
                listDay_2 = self.t4_2
            if i == 7:
                listDay_1 = self.p4_1
                listDay_2 = self.p4_2
            if i == 8:
                listDay_1 = self.t5_1
                listDay_2 = self.t5_2

            # x  axis
            x = np.arange(lists_lenght)

            # y  axis
            results1 = []
            results2 = []
            labels= ['T1','P1','T2','P2','T3','P3','T4','P4','T5']

            for j in range(lists_lenght):
                if parameter == 0:
                    results1.append(listDay_1[j] * 750)
                    results2.append(listDay_2[j] * 750)
                else:
                    results1.append(listDay_1[j] * 100)
                    results2.append(listDay_2[j] * 100)

            fig = plt.figure(figsize=(graph_dimX * 0.01, graph_dimY * 0.01), dpi=100)
            fig.suptitle(f'Results for both rhythmic training methods - {labels[i]}')
            ax = fig.add_subplot(1, 1, 1)
            ax.set_xlim(left=0, right=len(results1) - 1)
            if parameter == 0:
                ax.set_ylim(bottom=0, top= 400)
            else:
                ax.set_ylim(bottom=0, top= 100)
            plt.plot(x, results1, 'b', linewidth=2)
            plt.plot(x, results2, 'g', linewidth=2)


            if parameter == 0:
                param_str = "BPM"
            if parameter == 4:
                param_str = "Accuracy"
            if parameter == 8:
                param_str = "Performance"

            if i % 2 == 0:
                section = "_Test"
            else:
                section = "-Part"

            number= math.floor(i/2) + 1


            img_name = f"Performance/performance_data/evaluation_graphics/sections_averages_curves-{number}{section}-{param_str}.png"
            plt.savefig(img_name, dpi=100)
            # plt.show()


    def clear_evaluation_lists(self):
        """
        Clears p- and t- parameters lists after they were usedin method method self.show_sections_averages_curves(),
        preparing for the next use of the method self.show_sections_averages_curves() with the next parameter.
        """
        self.t1_1.clear()
        self.p1_1.clear()
        self.t2_1.clear()
        self.p2_1.clear()
        self.t3_1.clear()
        self.p3_1.clear()
        self.t4_1.clear()
        self.p4_1.clear()
        self.t5_1.clear()
        self.t1_1.clear()
        self.t1_2.clear()
        self.p1_2.clear()
        self.t2_2.clear()
        self.p2_2.clear()
        self.t3_2.clear()
        self.p3_2.clear()
        self.t4_2.clear()
        self.p4_2.clear()
        self.t5_2.clear()
        self.t1_2.clear()

        self.param_values_day1.clear()
        self.param_values_day2.clear()


    def reshape_raw_output_data(self, shuffle):
        """
        Generates x and input data for the data set of the neural network.
        The data is first loaded from files in path 'Performance/performance_data/raw_output_data', with the shape (600, 28)
        Data is reshaped into x shape (1, 25, 28) and y shape (1, 28) and flattened to be saved as 'input_x.out' and
        'input_y.out' files to the following path: Performance\performance_data\data_set.
        :param shuffle:
        :return:
        """

        #get all folders

        files= self.get_performance_data_files("Performance/performance_data/raw_output_data")


        if shuffle:
            seed = str(time.time())
            seed = int(seed[-2:])
            rnd.seed(seed)
            rnd.shuffle(files)

        self.data_set_files = len(files)

        print("")
        print("Reshaping and converting raw input data files in folder \'Performance/performance_data/raw_output_data\' "
              "into a data set for the neural network..")
        print("This may take a few minutes, depending on the size of the data set..")
        print("")

        for i in files:
            file_name=i

            self.raw_input_data = np.loadtxt(f'Performance/performance_data/raw_output_data/{file_name}',
                                                 delimiter=",")

            for part in range(4):  # there are 4 rounds in each data of the performance_data folder
                start_idx = 37 + part * 120
                rows_number = 25
                for i in range(96):  # 96 images to create for each round
                    shape = (25, self.nn_matrix_params)
                    temp_matrix = np.zeros(shape)
                    for j in range(len(self.raw_input_data)):

                        if j >= start_idx:
                            # modify last column
                            if j == start_idx + rows_number - 1:
                                array = self.raw_input_data[j]
                                arrays = self.set_last_array(array)
                                last_array_x = arrays[0]  # for data_set_x
                                output_array_y = arrays[1]  # for data_set_y

                                # append arrays to data set
                                output_array_x = temp_matrix  # data_set_x
                                output_array_x[-1] = last_array_x

                                temp_matrix = output_array_x

                                # save matrix
                                self.save_data_sets(output_array_x, output_array_y, ((part * 120) + i), file_name)

                                start_idx += 1
                                break

                            else:
                                array = self.raw_input_data[j]
                                temp_matrix[j - start_idx] = array


    def save_data_sets(self, arr_x, arr_y, rows, file_name):
        """
        Saves the input data x and y for the neural network as data set files 'input_x.out' and 'input_y.out' to
        the following path: Performance\performance_data\data_set"""
        #--------------------------DATA IMAGES--------------------------------------------------------------------------
        # Generate images that represent the raw_output_data.

        # # data_set_x image - shape will be 25 * 28 pixels
        # self.colors = []
        # rgb = (0, 0, 0)
        #
        # for i in range(arr_x.shape[0]):
        #     for j in range(arr_x.shape[1]):
        #         try:
        #             rgb = (arr_x[j][i],
        #                    arr_x[j][i],
        #                    arr_x[j][i])
        #             rgb = (int(round(rgb[0] * 255)),
        #                    int(round(rgb[1] * 255)),
        #                    int(round(rgb[2] * 255)))
        #         except:
        #             pass
        #         self.colors.extend(rgb)
        #
        # # Convert list to bytes
        # self.colors = bytes(self.colors)
        #
        # # save image in data_set_x folder
        # img = Image.frombytes('RGB', ( int(arr_x.shape[0]), arr_x.shape[1]), self.colors)
        # img_name = f"img-{rows}.png"
        # folder = f"Performance/out_images/{file_name[:-4]}"
        # if not os.path.exists(folder):
        #     os.makedirs(folder)
        # img.save(f'{folder}/{img_name}', 'PNG')

        # --------------------------------------------------------------------------------------------------------------
        #---------------------------------------DATA SET NP.ARRAYS------------------------------------------------------


        #create - assign data set folder

        folder = f"Performance/performance_data/data_set"
        self.data_set_folder=folder
        if not os.path.exists(folder):
            os.makedirs(folder)


        # reshape data
        shape= (25,self.nn_matrix_params,1)
        new_arr_x= np.zeros(shape)

        for i in range(25):
            for j in range(self.nn_matrix_params):
                new_arr_x[i][j][0]= arr_x[i][j]


        #set data_set_x
        if self.data_set_idx <= 383:
            self.data_set_x[self.data_set_idx]=new_arr_x
        if self.data_set_idx < 383:
            idx = (np.size(self.data_set_x, 0))
            self.data_set_x = np.insert(self.data_set_x,
                                        idx,
                                        0.0,
                                        axis=0)
        shape = (1, self.nn_matrix_params)
        new_arr_y = np.zeros(shape)

        for i in range(self.nn_matrix_params):
            new_arr_y[0][i]= arr_y[i]


        #set data_set_y
        if self.data_set_idx <= 383:
            self.data_set_y[self.data_set_idx] = arr_y
        if self.data_set_idx < 383:
            idx = (np.size(self.data_set_y, 0))
            self.data_set_y = np.insert(self.data_set_y,
                                        idx,
                                        0.0,
                                        axis=0)

        # save arrays
        # assign and save arrays to text files
        if self.data_set_idx == 383:
            print(f"{file_name}=", self.data_set_idx + 1, " inputs")
            file_x = f"{folder}/{file_name[:-4]}-data_set_x.out"
            flattened_x = np.asarray(self.data_set_x, dtype=np.float32)
            flattened_x= self.data_set_x.flatten()
            np.savetxt(file_x, flattened_x, delimiter=',')

            file_y = f"{folder}/{file_name[:-4]}-data_set_y.out"
            data_set_y = np.asarray(self.data_set_y, dtype=np.float32)
            np.savetxt(file_y, data_set_y, delimiter=',')

            self.combine_data_sets(self.data_set_x, self.data_set_y)
            self.data_set_idx=0

            #reset arrays
            self.reset_data_set_arrays()

            return

        # append index
        #---------------------------------------------------------------------------------------------------------------

        self.data_set_idx += 1

    def reset_data_set_arrays(self):
        shape_x = (1, 25, self.nn_matrix_params, 1)
        self.data_set_x = np.zeros(shape_x)
        shape_y = (1, self.nn_matrix_params)
        self.data_set_y= np.zeros(shape_y)


    def combine_data_sets(self,set_x, set_y):
        # data_set_x
        # --------------------------------------------------------------------------------------------------------------
        if self.all_data_x.shape[0] == 1:  # subtract 1 to shape[0] for the first iteration
            decrement=1
        else:
            decrement = 0

        shape_x=(self.all_data_x.shape[0] + set_x.shape[0] - decrement,
                self.all_data_x.shape[1],
                self.all_data_x.shape[2],
                self.all_data_x.shape[3])

        new_set_x=np.zeros(shape_x)

        for i in range(new_set_x.shape[0]):
            if i < self.all_data_x.shape[0] and self.all_data_x.shape[0] != 1:
                new_set_x[i]= self.all_data_x[i]
            else:
                new_set_x[i] = set_x[i - self.all_data_x.shape[0]]
        #---------------------------------------------------------------------------------------------------------------
        # data_set_y
        shape_y = (self.all_data_y.shape[0] + set_y.shape[0] - decrement,
                   self.all_data_y.shape[1])

        new_set_y = np.zeros(shape_y)

        for i in range(new_set_y.shape[0]):
            if i < self.all_data_y.shape[0] and self.all_data_y.shape[0] != 1:
                new_set_y[i] = self.all_data_y[i]
            else:
                new_set_y[i] = set_y[i - self.all_data_y.shape[0]]
        # ---------------------------------------------------------------------------------------------------------------

        #assign new set to all_data_set
        self.all_data_x = new_set_x
        self.all_data_y=new_set_y

        if  self.ds_files_idx == self.data_set_files - 1:
            self.save_combined_data_sets()
            self.ds_files_idx=0
        else:
            self.ds_files_idx += 1

    def save_combined_data_sets(self):
        folder= f"{self.data_set_folder}/Input_Data"
        if not os.path.exists(folder):
            os.makedirs(folder)

        file_x = f"{folder}/inputs_x.out"
        data_sets_x = np.asarray(self.all_data_x, dtype=np.float32)
        data_sets_x = self.all_data_x.flatten()
        np.savetxt(file_x, data_sets_x, delimiter=',')

        file_y = f"{folder}/inputs_y.out"
        data_sets_y = np.asarray(self.all_data_y, dtype=np.float32)
        np.savetxt(file_y, data_sets_y, delimiter=',')

    def load_input_data_set(self):

        folder= f'Performance/performance_data/data_set/Input_Data'

        print("")
        print("Loading data set from folder \'Performance/performance_data/data_set/Input_Data\'. ")
        print("This may also take a few minutes, depending on the size of the data set...")
        print("")

        files = self.get_performance_data_files(folder)
        file_x= f'{folder}/{files[0]}'
        file_y = f'{folder}/{files[1]}'
        shape_x, shape_y = self.get_input_data_shape(file_y)

        self.all_data_x = np.loadtxt(file_x, delimiter=",")
        self.all_data_x = np.reshape(self.all_data_x, shape_x)
        self.all_data_y = np.loadtxt(file_y, delimiter=",")
        print("")

    def get_input_data_shape(self, file_set_y):
        """
        Returns the shapes of the x and y data sets in files 'input_x.out' and 'input_y.out' in path
        'Performance/performance_data/data_set/Input_Data.
        :param file_set_y: y data set '.out' file
        :return: shape of x data set; shape of y data set
        """
        #source: https://www.kite.com/python/answers/how-to-get-a-line-count-of-a-file-in-python

        file = open(file_set_y, "r")
        nonempty_lines = [line.strip("\n") for line in file if line != "\n"]
        line_count = len(nonempty_lines)
        file.close()

        return (line_count,25,self.nn_matrix_params,1),(line_count, self.nn_matrix_params)

    def set_last_array(self, array):
        """Replaces parameters of the last array of the x data input and the y data input for the value 0.0,
        keeping only the relevant values for the neural network.

        Values 13 to 24 stay the same for x and y data. Values 11, 25, 26, 27 is the ground truth of the y data that
        will be predicted by the neural network, given only the x data.

        :param array: last array of a x data set input of shape ( 25, 28, 1)
        :return: The modified x data last array; new y data array
        """

        # just the value of runit.perf_av_0_5_pattern
        array_x = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, array[12],
                   array[13], array[14], array[15], array[16], array[17], array[18],
                   array[19], array[20], array[21], array[22], array[23], array[24],
                   0.0, 0.0, 0.0]
        # value of runit.perf_av_0_5_pattern + all rvs values of rhythmic pattern
        array_y = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, array[11], array[12],
                   array[13], array[14], array[15], array[16], array[17], array[18],
                   array[19], array[20], array[21], array[22], array[23], array[24],
                   array[25], array[26], array[27]]
        return [array_x, array_y]

    def show_save_stats(self, file_name, show_graph, test):
        """
        Saves round performance graphics, given the values in self.neural_matrix to the path
        'Performance/performance_data/evaluation_graphics/day_1 or day_2', according to training day.
        :param file_name: Name give in method self.gm.manage_graph_images: [date_time]-[training round part]
        :param show_graph: True if graphic should be shown
        :param test: True if the part of training round that is being processed now is a Test part (T1 to T5)
        :return: nothing
        """
        sw, sh = pyautogui.size()
        graph_dimX = sw * 0.5
        graph_dimY = sh * 0.5

        x_dim = len(self.runits_all)- 1
        y_dim = 1
        # Parameters

        x_len = x_dim  # Number of points to display
        y_range = [0, y_dim]  # Range of possible Y values to display

        # Create figure for plotting
        fig = plt.figure(figsize=(graph_dimX * 0.01, graph_dimY * 0.01), dpi=100)

        ax = fig.add_subplot(1, 1, 1)
        if test:
            ax.set_xlim(left=len(self.runits_all) - 25, right=len(self.runits_all) - 1)
        else:
            ax.set_xlim(left=len(self.runits_all) - 121, right=len(self.runits_all) - 1)
        ax.set_ylim(bottom=0, top=1)
        ax.set_ylim(y_range)

        matrix= self.neural_matrix
        x=[]
        y=[]
        for i in range(0, 5):
            for j in range(len(self.runits_all) - 1):
                x.append(j)
                if i == 4:  # error  - not in the matrix
                    y.append(self.runits_all[j].error)  # errors start at index 2
                else:
                    if i == 0:  # accuracy
                        param = 4
                    if i == 1:
                        param = 8  # performance
                    if i == 2:
                        param = 10  # performance_24
                    if i == 3:
                        param = 0  # bpm

                    y.append(matrix[j][param])

            plt.plot(x, y, self.stats_colors[i], linewidth=1.5, label= self.labels[i]);
            x.clear()
            y.clear()

        #source of syntax: https://geog0111.readthedocs.io/en/latest/Chapter2_Numpy_matplotlib.html
        plt.xlabel("Rhythmic Units")
        plt.ylabel("Values")
        plt.legend(loc="best")

        # img_name=f"Zip-me/{file_name}.png"
        day= self.rm.day_int
        img_name=f"Performance/performance_data/evaluation_graphics/day_{day}/{file_name}.png"
        plt.savefig(img_name, dpi=100)

        if show_graph:
            plt.show()

        self.gm.focus_on_window()

    def save_output_data(self):
        """
        Saves output data files 'input_x.out' and 'input_y.out' to the paths
        'Performance/performance_data/[raw_output_data_day_1] or [raw_output_data_day_2]'
        """
        if self.data_valid == True:
            date_time = self.get_time_date()
            # -------------------------------------------------------------------------------
            folder = 'Performance/performance_data/raw_output_data'
            # folder = f"Zip-me"
            if not os.path.exists(folder):
                os.makedirs(folder)
            if self.gm.mode == 1:
                if self.rm.day_int == 1:
                    file_name = f"Performance/performance_data/raw_output_data_day_1/{self.pseudo_name}-{date_time}-{self.gm.round}.out"
                else:
                    file_name = f"Performance/performance_data/raw_output_data_day_2/{self.pseudo_name}-{date_time}-{self.gm.round}.out"
            else:
                file_name = f"Performance/performance_data/raw_output_data/{self.pseudo_name}-{date_time}.out"

            # file_name = f"Zip-me/{self.pseudo_name}-{date_time}-{self.gm.round}.out"

            # self.synaptic_weights_plt = self.synaptic_weights.reshape(1, self.synaptic_weights.size)
            self.neural_matrix = np.delete(self.neural_matrix, 0, axis=0)
            self.neural_matrix = np.delete(self.neural_matrix, -1, axis=0)
            self.neural_matrix = np.delete(self.neural_matrix, -1, axis=0)
            np.savetxt(file_name, self.neural_matrix, delimiter=',')

    def get_time_date(self):
        """
        Gets and returns the time and data now as string.
        :return: time and data now.
        """
        # source: https://www.w3resource.com/python-exercises/python-basic-exercise-3.php
        now = datetime.datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H_%M_%S")
        return date_time
        # -------------------------------------------------------------------------------

    def set_initial_tempo(self):
        """Set the initial tempo and bpm values according to the typing speed during self.gm.game_state 0
        (for self.gm.mode 0 or 1) or as default value of 80 bpm for self.gm.mode 2 (second evaliuation training)"""
        if self.gm.mode == 0:
            total_time= self.pressed_times[-1] - self.pressed_times[0]
            self.gm.tempo=total_time/len(self.pressed_times)
            self.gm.bpm= 60/self.gm.tempo
            self.initial_bpm= self.gm.bpm
        else:
            self.gm.bpm = 80
            self.gm.tempo = 60/80

    def set_default_tempo(self):
        """
        Sets the default value of 80 bpm in self.gm.mode 2 (second evaluation training)
        """
        self.gm.bpm = 80
        self.gm.tempo = 60 / 80


    def sort_patterns_performance(self, parameter, optimize, number, iterations):
        """Sorts the rhythmic patterns in self.all_data_y according to specific parameters:
        args: parameter:  value in the array of self.all_data_y (11= perf_av_0_5_pattern; 27= bpm_av_0_5_pattern)
              optimize: True if
              number: number of patterns to show and optimize
                      (min= 4, max= (self.all_data_x.shape[0] - 1) - all the patterns exept the last 2 rows)
              iterations: number of iterations to optimize the parameters
        """
        # number= self.all_data_x.shape[0] - 1 # show all

        self.ann= self.gm.neural_network
        param_list_x= []
        param_list_y =[]

        param_list_x= np.zeros(self.all_data_x.shape)
        param_list_y= np.zeros(self.all_data_y.shape)

        all_p_y= self.all_data_y

        # param_list_x = np.zeros((475000,28,28))
        # param_list_y = np.zeros((475000,28))
        # all_p_y = param_list_y

        param_values=[]
        param_indexes=[]

        for i in range(len(all_p_y)):
            param_values.append(all_p_y[i][parameter])     #performance value
            # print("all_p_y[i][parameter]= ", all_p_y[i][parameter])

        #sort values from best to worst
        batch_lenght= min(param_list_y.shape[0], 500)
        # the method self.grm.quick_sort has a limitation of values indxes - 10000 is within its limits
        batch_count= math.floor(all_p_y.shape[0] / batch_lenght)
        rest= round(all_p_y.shape[0] % batch_lenght)
        if rest > 0:
            batch_count += 1

        all_batches=[]
        for i in range(batch_count):

            if batch_count == 0:
                max_val = rest - 1
            elif i < batch_count:
                max_val= int(i  * batch_lenght) + int(batch_lenght - 1)
            else:
                max_val = int(i  * batch_lenght) +  rest - 1
            min_val= int(i  * batch_lenght)

            all_batches.append(param_values[min_val:max_val])

        sorted_batches = []
        for i in range(len(all_batches)):
            list= all_batches[i]
            sorted_batches.append(self.grm.quick_sort(list))


        # take first values of each batch (number / batch_count in each batch)

        unsorted_values =[]
        values_per_batch= max(1, round(number/batch_count))

        for i in range(len(sorted_batches)):
            if i < len(sorted_batches):
                count = values_per_batch
            else:
                count = min(rest, values_per_batch)
            for j in range(count):
                unsorted_values.append(sorted_batches[i][j])


        sorted_p_values= self.grm.quick_sort(unsorted_values)
        sorted_p_values = sorted_p_values[:number]
        # print( "sorted_p_values= ",  sorted_p_values)

        for i in range(len(sorted_p_values)):
            param_indexes.append((param_values.index(sorted_p_values[i])))

            list_idx=param_indexes[i]
            #append rhythmic patterns x and y to lists
            param_list_x[i]= self.all_data_x[list_idx]
            param_list_y[i]= self.all_data_y[list_idx]


        #show data as plt image
        shape_x = (number, 28, 1)
        array_y = np.zeros(shape_x)

        for r in range(0, number):
            idx = param_indexes[r]
            for i in range(28):
                array_y[r][i] = all_p_y[idx][i]  # prediction
        plt.imshow(array_y)
        plt.show()

        #assign lists
        if parameter == 11:
            self.ann.best_perf_x = param_list_x
            self.ann.best_perf_y = param_list_y
        if parameter == 27:
            self.ann.best_bpm_x = param_list_x
            self.ann.best_bpm_y = param_list_y

        #optimize patterns
        if optimize:
            self.ann.optimize_patterns(parameter, param_list_x, param_list_y, 0, number, iterations)

    def sort_optimize_patterns(self, number, optimize, iterations):
        """
        :param number:
        :param optimize: True if the rhythmic patterns of the current dataset with the best performance average values by
        should be optimized by generating patterns that have a higher prediction of these values with the neural network.
        :param iterations: number of iterations for the optimization of the patterns (each iteration, a different random
        rhythmic is predicted by the neural network.
        :return: nothing

        """
        # Performance average (parameter 11= runit.perf_av_0_5_pattern)
        self.sort_patterns_performance(
            parameter=11,
            optimize=False,  # can be set to True, otherwise, only the list of the X (X is the param. number's value)
            # best rhythmic patterns for PERFORMANCE averages will be shown.
            number=number,
            iterations=iterations)

        # Speed average (parameter 27= runit.bpm_av_0_5_pattern)
        self.sort_patterns_performance(
            parameter=27,
            optimize=optimize,  # always False - optimizing is only possible for the parameter 11, the performance.
            # the list of the X (X is the param. number's value) best
            # rhythmic patterns for SPEED averages will be shown.
            number=number,
            iterations=iterations)

    def evaluate_training(self, mode):
        """
        Generates performance average graphics for each round of the the current training (data sets in the folders:
         performance_data/raw_output_data_day_1 and raw_output_data_day_2) and for the whole training.
         The parameters show in the graphics are the average values for bpm, accuracy and performance
         parameter 0= runit.runit_bpm
         parameter 4= runit.accuracy
         parameter 8= runit.performance
        :param mode: 1= first evaluation training of the major project related to this program
                     2= second evaluation training of the same project
        :return:
        """
        self.gm.mode= mode

        # bpm averages
        self.show_methods_evaluation(1, "all_training_average", parameter=0)
        self.show_methods_evaluation(2, "all_training_average", parameter=0)
        self.show_methods_evaluation(1, "sections_averages_curves", parameter=0)
        self.show_methods_evaluation(2, "sections_averages_curves", parameter=0)

        # accuracy averages - only in mode 1 - evaluation mode
        self.show_methods_evaluation(1, "all_training_average", parameter=4)
        self.show_methods_evaluation(2, "all_training_average", parameter=4)
        self.show_methods_evaluation(1, "sections_averages_curves", parameter=4)
        self.show_methods_evaluation(2, "sections_averages_curves", parameter=4)

        # performance averages
        self.show_methods_evaluation(1, "all_training_average", parameter=8)
        self.show_methods_evaluation(2, "all_training_average", parameter=8)
        self.show_methods_evaluation(1, "sections_averages_curves", parameter=8)
        self.show_methods_evaluation(2, "sections_averages_curves", parameter=8)

        # total of all parameters
        self.show_parameter_totals()
