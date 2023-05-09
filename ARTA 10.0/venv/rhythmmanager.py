"""
Project: Adaptive Rhythmic Training Application (ARTA)
File   : rhythmmanager.py
Date   : 21/01/2022
Author : Yann Savard

This code is open source, except for some parts that were taken
from external sources and their sources are mentioned in the code.

History: programmed from september 2021 to february 2022 as part of my bachelor project:
"Conception and Evaluation of New Rhythm-Based Dexterity Training Methods with Adaptive Game Mechanics and AI"
"""

import pygame
import pygame.midi
import time
import random as rnd

class RhythmManager():
    def __init__(self, g_manager):
        self.gm= g_manager
        self.grm = self.gm.grid_manager

        # rhythmic patterns
        self.rhythmic_patterns_base=[] #all base rhythmic patterns
        self.rhythmic_idx_p= -1 # current index in  self.all_rhythmic_patterns (0 to 95)
        self.r_idx_to_press=0
        self.rhythmic_patterns_now = []  # with 4 indexes (4 following lists)
        self.rp1=[]
        self.rp2=[]
        self.rp3=[]
        self.rp4=[]
        self.all_rhythmic_patterns = []  # [0]= 96 indexes (combined rhythmic patterns) 1= [image kind for this note]
        self.pre_silence_length = []
        self.post_silence_length = []

        self.rhythmic_pattern = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.day_int=0

        #day exercises:

        #mode 0:
        self.day1_0 = [31, 0, 1, 2, 3, 4, 31, 10, 11, 12, 13, 14, 31, 20, 21, 22, 23, 24, 31, 32, 32, 32, 32, 31, 31]
        self.day2_0 = [31, 5, 6, 7, 8, 9, 31, 15, 16, 17, 18, 19, 31, 25, 26, 27, 28, 29, 31, 32, 32, 32, 32, 31, 31]

        #mode 1:
        #---------------------------------------------------------------------------------------------------------------
        #optimized patterns - set 1 - This part was not used in the bachelor project related to this program.
        # self.day1_1 = [31, 31, 34, 35, 36, 37, 31, 38, 39, 40, 41, 42, 31, 43, 44, 45, 46, 47, 31, 48, 49, 50, 51, 52, 33]
        # self.day2_1 = [31, 31,  1,  2,  3,  4,  31, 10, 11, 12, 13, 14, 31, 0,  1,  2,  3,  4,  31, 10, 11, 12, 30, 30 ,33]

        # optimized patterns - set 2
        # self.day1_1 = [72, 31, 54, 55, 56, 57, 31, 58, 59, 60, 61, 62, 31, 63, 64, 65, 66, 67, 31, 68, 69, 70, 71, 30, 31]
        self.day1_1 = [72, 31, 54, 55, 56, 57, 31, 68, 69, 70, 71, 71, 31, 53, 54, 55, 56, 57, 31, 68, 69, 70, 71, 30, 31]
        self.day2_1 = [72, 31, 10, 11, 12, 13, 31, 0,  1,  2,  3,  4,  31, 73, 11, 12, 13, 14, 31, 0,  1,  2,  3,  30, 31]
        # ---------------------------------------------------------------------------------------------------------------

        self.day_now=[] #today's practice (rhythmic patterns)
        self.day_now_idx = 0

        self.r_patterns_count = [0]
        self.player=None

    def set_player(self):
        """Sets the pygame midi player pygame.midi and the metronome sound."""
        pygame.midi.init()
        self.player = pygame.midi.Output(0, 0, 4096)
        self.player.set_instrument(113)

    def play_sound(self, sound):
        """Plays the metronome sound."""
        if sound == 0:
            self.player.note_on(120,100)
        if sound == 1:
            pass # for future sounds...

    def set_rm(self):
        """Sets the list self.rhythmic_patterns_base that contains all rhythmic patterns used in all training rounds of
        self.gm.mode 1 and 2. Also sets the list  self.rhythmic_patterns_base, which contains the four rhythmic patterns
         shown in the grid of the graphical interface."""
        self.set_rhythmic_patterns_list()
        self.set_rp_lists()
        self.rhythmic_idx_p=0

    def get_day(self):
        """Loads the present day of the current 10 days training program (day 1 or day 2 are always alternating).
        Day is loaded from '.txt' file in path 'Performance/performance_data.txt' """

        # load day(int) from text file (Performance/performance_data.txt)
        if self.day_now_idx == 0:
            self.day_int = self.gm.load_day()
            # mode 0 - training for the A.I.
            if self.gm.mode == 0:
                if self.day_int == 1:
                    self.day_now = self.day1_0
                else:
                    self.day_now = self.day2_0
            # mode 1 - evaluation
            else:
                if self.day_int == 1:
                    self.day_now = self.day1_1
                else:
                    self.day_now = self.day2_1

    def set_rp_lists(self):
        """Sets the self.rhythmic_patterns_base, appending all rhythmic patterns (self.rp1 to self.rp4) to it. """
        self.get_day()

        #set rhythmic patterns lists
        if  self.day_now_idx == 0:
            self.rp1 = self.rhythmic_patterns_base[self.day_now[(self.day_now_idx + 0) % len(self.day_now)]]
            self.rp2 = self.rhythmic_patterns_base[self.day_now[(self.day_now_idx + 1) % len(self.day_now)]]
            self.rp3 = self.rhythmic_patterns_base[self.day_now[(self.day_now_idx + 2) % len(self.day_now)]]
        else:
            self.rp1 = self.rp2
            self.rp2 = self.rp3
            self.rp3 = self.rp4

        # generate random rhythmic pattern (if index of rp4 in self.rhythmic_patterns_base is 32)
        x = self.day_now[(self.day_now_idx + 3) % len(self.day_now)]
        if x == 32:
            self.generate_random_pattern()
            self.rp4 = self.rhythmic_patterns_base[-1]
        else:
            self.rp4 = self.rhythmic_patterns_base[self.day_now[(self.day_now_idx + 3) % len(self.day_now)]]


        self.rhythmic_patterns_now.clear()
        self.rhythmic_patterns_now.append(self.rp1)
        self.rhythmic_patterns_now.append(self.rp2)
        self.rhythmic_patterns_now.append(self.rp3)
        self.rhythmic_patterns_now.append(self.rp4)

        # self.all_rhythmic_patterns
        self.all_rhythmic_patterns.clear()
        for pattern in self.rhythmic_patterns_now:
            for i in range(24):
                self.all_rhythmic_patterns.append([pattern[i], ""])

        self.grm.set_lists()



    def set_tempo_values(self, bpm):
        """Set tempo values according to bpm parameter"""
        if self.gm.bpm + bpm >= self.gm.min_bpm and self.gm.bpm + bpm <= self.gm.max_bpm:
            self.gm.bpm += bpm
            self.gm.tempo = 60/self.gm.bpm

    def set_rhythmic_patterns_list(self):
        """
        Sets the self.rhythmic_patterns_base list, appending all rhythmic patterns to it. Note: each rhythmic pattern
        has exactly 24 rhythmic values and the term half-pattern means the first or last 12 values of a rhythmic
        pattern.

        legend of all rhythmic values in rhythmic patterns:
        0= silence - void
        1= soft
        2= accent
        3= accent zoomed
        """

        #mode 0 - training for the A.I.
        #---------------------------------------------------------------------------------------------------------------
        #indexes 0 to 4


        self.rhythmic_patterns_base.append([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                            1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1])
        self.rhythmic_patterns_base.append([2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1,
                                            2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1])
        self.rhythmic_patterns_base.append([2, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1,
                                            1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1])
        self.rhythmic_patterns_base.append([1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1,
                                            2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2])
        self.rhythmic_patterns_base.append([1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1,
                                            2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1])


        # indexes 5 to 9 - same as 0 to 4, except that the 2 are changed to 3 (the accents become zoomed accents)
        temp=[]
        for i in range(0, 5):
            for j in self.rhythmic_patterns_base[i]:
                if j == 2:
                    temp.append(3)
                else:
                    temp.append(j)
            self.rhythmic_patterns_base.append(temp)
            temp=[]

        # indexes 10 to 14
        if self.gm.mode == 0:
            self.rhythmic_patterns_base.append([2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1,
                                                2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1])
            self.rhythmic_patterns_base.append([2, 0, 0, 1, 2, 0, 0, 1, 2, 0, 0, 1,
                                                2, 0, 0, 1, 2, 0, 0, 1, 2, 0, 0, 1])
            self.rhythmic_patterns_base.append([2, 0, 0, 1, 2, 0, 0, 1, 2, 0, 0, 0,
                                                1, 2, 0, 0, 0, 1, 2, 0, 0, 0, 1, 2])
            self.rhythmic_patterns_base.append([0, 0, 0, 1, 2, 0, 0, 0, 1, 2, 0, 0,
                                                0, 1, 2, 0, 0, 0, 1, 2, 0, 0, 0, 1])
            self.rhythmic_patterns_base.append([2, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 1,
                                                2, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 1]) #
        else:
            #indexes 10 to 14 - adjusted
            self.rhythmic_patterns_base.append([1, 1, 1, 1, 1, 0, 1, 2, 0, 1, 2, 0,
                                                1, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2])
            self.rhythmic_patterns_base.append([1, 1, 1, 2, 0, 1, 1, 2, 0, 1, 1, 2,
                                                0, 1, 1, 2, 1, 1, 1, 2, 0, 1, 1, 2])
            self.rhythmic_patterns_base.append([0, 1, 1, 2, 0, 1, 1, 2, 1, 1, 1, 1,
                                                2, 0, 1, 1, 1, 2, 0, 1, 1, 1, 2, 0])
            self.rhythmic_patterns_base.append([1, 1, 1, 2, 1, 1, 1, 1, 2, 0, 1, 1,
                                                1, 2, 0, 1, 1, 1, 2, 0, 1, 1, 1, 2])
            self.rhythmic_patterns_base.append([1, 1, 1, 1, 1, 2, 0, 1, 1, 1, 1, 2,
                                                1, 1, 1, 1, 1, 2, 0, 1, 1, 1, 1, 2]) # total of 0 values= 21


        # indexes 15 to 19 - same as 10 to 14, except that the 2 are changed to 3 (the accents become zoomed accents)
        temp = []
        for i in range(10, 15):
            for j in self.rhythmic_patterns_base[i]:
                if j == 2:
                    temp.append(3)
                else:
                    temp.append(j)
            self.rhythmic_patterns_base.append(temp)
            temp = []

        #indexes 20 to 24 - rhythms from Mozart's Jupiter Symphony 1st movement
        self.rhythmic_patterns_base.append([2, 0, 0, 0, 2, 0, 0, 1, 2, 0, 0, 0,
                                            2, 0, 0, 1, 2, 0, 1, 0, 2, 0, 1, 0])
        self.rhythmic_patterns_base.append([2, 0, 0, 0, 2, 0 ,0 ,1 ,2 ,0 ,0 ,0,
                                            2, 0, 0, 1, 2, 0, 1, 0, 2, 0, 1, 0])
        self.rhythmic_patterns_base.append([2, 0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0,
                                            1, 1, 1, 1, 2, 0, 1, 0, 2, 0, 1, 0])
        self.rhythmic_patterns_base.append([2, 0, 1, 0, 1, 1, 1, 1, 2, 0, 1, 0,
                                            2, 0, 1, 0, 2, 0, 1, 0, 1, 1, 1, 1])
        self.rhythmic_patterns_base.append([1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1,
                                            2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2])


        # indexes 25 to 29 - same as 20 to 24, except that the 2 are changed to 3 (the accents become zoomed accents)
        temp = []
        for i in range(20, 25):
            for j in self.rhythmic_patterns_base[i]:
                if j == 2:
                    temp.append(3)
                else:
                    temp.append(j)
            self.rhythmic_patterns_base.append(temp)
            temp = []


        #index 30 - softs
        self.rhythmic_patterns_base.append([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        # index 31 - pause - test
        self.rhythmic_patterns_base.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]) #last == 0
        #index 32 - for random patterns
        self.rhythmic_patterns_base.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        #---------------------------------------------------------------------------------------------------------------
        #mode 1 - evaluation
        # -----------------------------------FIRST SET OF OPTIMIZED PATTERNS--------------------------------------------
        # (The section was implemented for this the bachelor project related to this program, but not used in the
        # 2 official evaluation trainings of self.gm.mode 1 and 2)
        # ---------------------------------------------------------------------------------------------------------------
        #indexes 33 to 37 - optimized patterns part 1
        self.rhythmic_patterns_base.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                            2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
        self.rhythmic_patterns_base.append([2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3,
                                            3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2])
        self.rhythmic_patterns_base.append([3, 2, 2, 3, 2, 2, 3, 2, 2, 3, 2, 2,
                                            3, 3, 2, 3, 3, 2, 3, 3, 2, 3, 3, 2])
        self.rhythmic_patterns_base.append([1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3,
                                            2, 3, 3, 2, 3, 3, 2, 3, 3, 2, 3, 3])
        self.rhythmic_patterns_base.append([2, 0, 2, 1, 2, 0, 2, 1, 2, 0, 2, 1,
                                            2, 0, 2, 1, 2, 0, 2, 1, 2, 0, 2, 1])

        # indexes 38 to 42 - optimized patterns part 2
        self.rhythmic_patterns_base.append([2, 0, 2, 3, 2, 0, 2, 3, 2, 0, 2, 3,
                                            2, 0, 2, 3, 2, 0, 2, 3, 2, 0, 2, 3 ])
        self.rhythmic_patterns_base.append([2, 0, 0, 2, 1, 2, 0, 2, 1, 2, 0, 2,
                                            1, 2, 0, 2, 1, 2, 0, 2, 1, 2, 0, 2])
        self.rhythmic_patterns_base.append([1, 2, 3, 2, 3, 1, 2, 3, 2, 3, 1, 2,
                                            3, 2, 3, 1, 2, 3, 2, 3, 1, 2, 3, 2])
        self.rhythmic_patterns_base.append([3, 0, 0, 1, 2, 3, 3, 2, 1, 2, 3, 3,
                                            2, 1, 2, 3, 3, 2, 1, 2, 3, 3, 2, 1])
        self.rhythmic_patterns_base.append([2, 3, 2, 3, 1, 2, 3, 2, 3, 1, 2, 3,
                                            2, 3, 1, 2, 3, 2, 3, 1, 2, 3, 2, 3])

        # indexes 43 to 47 - optimized patterns part 3
        self.rhythmic_patterns_base.append([1, 2, 3, 0, 0, 3, 2, 1, 1, 2, 3, 0,
                                            0, 3, 2, 1, 1, 2, 3, 0, 0, 3, 2, 1])
        self.rhythmic_patterns_base.append([0, 2, 2, 3, 0, 3, 2, 2, 0, 2, 2, 3,
                                            0, 3, 2, 2, 0, 2, 2, 3, 0, 3, 2, 2])
        self.rhythmic_patterns_base.append([0, 3, 3, 2, 2, 3, 3, 0, 0, 3, 3, 2,
                                            2, 3, 3, 0, 0, 3, 3, 2, 2, 3, 3, 0])
        self.rhythmic_patterns_base.append([2, 0, 2, 1, 1, 2, 0, 3, 2, 0, 2, 1,
                                            1, 2, 0, 3, 2, 0, 2, 1, 1, 2, 0, 3])
        self.rhythmic_patterns_base.append([1, 2, 3, 2, 0, 2, 0, 2, 1, 2, 3, 2,
                                            0, 2, 0, 2, 1, 2, 3, 2, 0, 2, 0, 2])

        # indexes 48 to 52 - optimized patterns part 4
        self.rhythmic_patterns_base.append([2, 3, 1, 3, 2, 2, 0, 3, 2, 3, 1, 3,
                                            2, 2, 0, 3, 2, 3, 1, 3, 2, 2, 0, 3])
        self.rhythmic_patterns_base.append([1, 2, 1, 2, 3, 2, 0, 2, 1, 2, 1, 2,
                                            3, 2, 0, 1, 1, 2, 1, 2, 3, 2, 0, 2])
        self.rhythmic_patterns_base.append([3, 1, 2, 3, 2, 0, 2, 1, 3, 1, 2, 3,
                                            2, 0, 2, 1, 3, 1, 2, 3, 2, 0, 2, 1])
        self.rhythmic_patterns_base.append([0, 3, 1, 2, 3, 2, 0, 2, 0, 3, 1, 2,
                                            3, 2, 0, 2, 0, 3, 1, 2, 3, 2, 0, 2])
        self.rhythmic_patterns_base.append([1, 2, 3, 1, 2, 3, 3, 2, 1, 2, 3, 1,
                                            2, 3, 3, 2, 1, 2, 3, 1, 2, 3, 3, 2])

        #-----------------------------------SECOND SET OF OPTIMIZED PATTERNS--------------------------------------------

        # index 53
        self.rhythmic_patterns_base.append([3, 3, 2, 3, 3, 3, 2, 3, 3, 3, 2, 3,
                                            3, 3, 2, 3, 3, 3, 2, 3, 3, 3, 2, 3])

        #indexes 54 to 57 - optimized patterns - 2nd set - part 1 ------------- 21 * 0

        self.rhythmic_patterns_base.append([3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2,
                                            3, 2, 3, 2, 1, 0, 3, 0, 3, 0, 1, 1])
        self.rhythmic_patterns_base.append([1, 0, 3, 0, 3, 0, 1, 1, 3, 0, 3, 2,
                                            3, 0, 2, 1, 3, 0, 3, 2, 3, 0, 2, 1])
        self.rhythmic_patterns_base.append([3, 0, 3, 2, 3, 0, 2, 1, 3, 0, 3, 2,
                                            3, 0, 2, 1, 2, 0, 3, 2, 3, 2, 3, 3])
        self.rhythmic_patterns_base.append([2, 0, 3, 2, 3, 2, 3, 3, 2, 0, 3, 2,
                                            3, 2, 3, 3, 2, 0, 3, 2, 3, 2, 3, 3])

        # indexes 58 to 62 - optimized patterns - 2nd set - part 2 ------------- 0 * 0
        self.rhythmic_patterns_base.append([2, 3, 3, 3, 2, 3, 3, 3, 2, 3, 3, 3,
                                            2, 3, 3, 3, 2, 3, 3, 3, 2, 3, 3, 3])
        self.rhythmic_patterns_base.append([3, 1, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1,
                                            3, 1, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3])
        self.rhythmic_patterns_base.append([1, 3, 1, 3, 1, 3, 1, 3, 3, 3, 1, 3,
                                            3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 1, 3])
        self.rhythmic_patterns_base.append([3, 1, 2, 3, 2, 1, 3, 2, 3, 1, 2, 3,
                                            2, 1, 3, 2, 3, 1, 2, 3, 2, 1, 3, 2])
        self.rhythmic_patterns_base.append([3, 1, 2, 3, 2, 1, 3, 2, 3, 1, 2, 3,
                                            2, 1, 3, 2, 3, 1, 2, 3, 2, 1, 3, 2])

        # indexes 63 to 67 - optimized patterns - 2nd set - part 3 ------------ 16 * 0
        self.rhythmic_patterns_base.append([3, 2, 2, 3, 3, 2, 2, 3, 3, 2, 2, 3,
                                            3, 2, 2, 3, 2, 3, 3, 0, 3, 2, 0, 2])
        self.rhythmic_patterns_base.append([2, 3, 3, 0, 3, 2, 0, 2, 2, 3, 3, 0,
                                            3, 2, 0, 2, 2, 3, 3, 0, 3, 2, 0, 2])
        self.rhythmic_patterns_base.append([2, 3, 3, 0, 3, 3, 0, 2, 2, 3, 2, 1,
                                            3, 3, 1, 0, 2, 3, 2, 1, 3, 3, 1, 0])
        self.rhythmic_patterns_base.append([2, 3, 2, 1, 3, 3, 1, 0, 2, 3, 2, 1,
                                            3, 3, 1, 0, 3, 3, 3, 1, 3, 2, 0, 3])
        self.rhythmic_patterns_base.append([3, 3, 3, 1, 3, 2, 0, 3, 3, 3, 3, 1,
                                            3, 2, 0, 3, 3, 3, 3, 1, 3, 2, 0, 3])

        # indexes 68 to 71 - optimized patterns - 2nd set - part 4 ------------ 0 * 0
        self.rhythmic_patterns_base.append([3, 2, 2, 3, 3, 2, 2, 3, 3, 2, 2, 3,
                                            3, 2, 2, 3, 3, 2, 2, 3, 3, 2, 2, 3])
        self.rhythmic_patterns_base.append([2, 3, 3, 1, 2, 3, 1, 3, 2, 3, 3, 1,
                                            2, 3, 1, 3, 2, 3, 3, 1, 2, 3, 1, 3])
        self.rhythmic_patterns_base.append([2, 2, 3, 1, 3, 3, 1, 3, 2, 2, 3, 1,
                                            3, 3, 1, 3, 2, 2, 3, 1, 3, 3, 1, 3])
        self.rhythmic_patterns_base.append([3, 2, 3, 1, 3, 2, 3, 2, 3, 2, 3, 1,
                                            3, 2, 3, 2, 3, 2, 3, 1, 3, 2, 3, 2])

        #index 72 - all silences
        self.rhythmic_patterns_base.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        # index 73 - variation of index 10
        self.rhythmic_patterns_base.append([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                            1, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2])
        # ---------------------------------------------------------------------------------------------------------------

    def generate_random_pattern(self):
        """Generates a random rhythmic pattern for the index 32 of the self.rhythmic_patterns_base list. The values of
         index 32 are all 0 and they will be replaced by random values in this method."""

        seed = str(time.time())
        seed = int(seed[-2:])
        rnd.seed(seed)
        new_pattern = []
        for i in range(24):
            n = rnd.randint(0, 3)
            if self.day_now == self.day1_0 and n == 3:  # kind 3 is replaces by kind 2 for day 1
                n = 2
            new_pattern.append(n)
        self.rhythmic_patterns_base.append(new_pattern)
        if len(self.rhythmic_patterns_base) >= 38:
            del self.rhythmic_patterns_base[-5]

    def generate_random_half_pattern(self):
        """Generates a half-pattern (12 values long) with random values for the optimization process of rhythmic
        patterns used with the artificial intelligence (neural network)."""

        new_pattern = []
        for i in range(12):
            n = rnd.randint(0, 3)
            n= float(n * 0.1 * 3)
            n= round(n,1)
            new_pattern.append(n)

        return new_pattern
