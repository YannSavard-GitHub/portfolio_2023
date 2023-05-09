"""
Project: Adaptive Rhythmic Training Application (ARTA)
File   : runit.py
Date   : 21/01/2022
Author : Yann Savard

This code is open source, except for some parts that were taken
from external sources and their sources are mentioned in the code.

History: programmed from september 2021 to february 2022 as part of my bachelor project:
"Conception and Evaluation of New Rhythm-Based Dexterity Training Methods with Adaptive Game Mechanics and AI"
"""

class RUnit():
    def __init__(self, g_manager):
        self.gm = g_manager
        self.grm = self.gm.grid_manager
        self.rm = self.gm.rhythm_manager
        self.pm = self.gm.perf_manager

        #main properties
        self.idx=0
        self.image = None
        self.kind=0
        self.char= ""
        self.number=0 # ASCII value
        self.neural_char_value=0.0
        self.grid_pos = (0, 0)
        self.way_pos = (0, 0)
        #----------------------------------

        #timing
        self.time_to_press=0.0
        self.time_pressed = 0.0
        self.t_mod_step_up= 0.0
        self.t_mod_step_down = 0.0
        self.t_modification_frq=0.0


        #performance related attributes their average

        # speed
        self.runit_bpm=0.0
        self.bpm_av_0_5_pattern=0.0

        # accuracy
        self.accuracy = 0.0     # 0-1
        self.accuracy_average_12 = 0.0
        self.accuracy_average_24 = 0.0
        self.acc_av_0_5_pattern = 0.0 # accuracy of a half pattern (indexes 0 to 11 or 12 to 23)

        # performance
        self.performance = 0.0  # 0-1
        self.performance_average_12 = 0.0
        self.performance_average_24 = 0.0
        self.perf_av_0_5_pattern = 0.0 # performance of a half pattern (indexes 0 to 11 or 12 to 23)

        self.rhythmic_value=0

        self.rv1=0
        self.rv2=0
        self.rv3=0
        self.rv4=0
        self.rv5=0
        self.rv6=0
        self.rv7=0
        self.rv8=0
        self.rv9=0
        self.rv10=0
        self.rv11=0
        self.rv12=0

        #errors
        self.error=0.0      # error for this note 1=error 0=successfully pressed
        self.success=0.0        # 1= successfully pressed runit




    def set_rvs(self):
        """Sets the rhythmic values attributes of the runit, rescaling them for the neural matrix
        (self.pm.neural_matrix)."""

        #set rhythmic_value
        self.rhythmic_value=self.rm.rhythmic_patterns_now[0][self.rm.rhythmic_idx_p] * 3.0 * 0.1

        #set rvs
        if self.rm.rhythmic_idx_p <= 11:
            next_pattern_idx = 0 # to set first half of the current rhythmic pattern (indexes 0 to 11)
        else:
            next_pattern_idx = 12  # to set second half of the current rhythmic pattern (indexes 12 to 23)

        idx = 0
        #set rvs

        for i in self.rm.rhythmic_patterns_now[0]:
            if idx == 0 + next_pattern_idx:
                self.rv1 = i * 3.0 * 0.1
            if idx == 1 + next_pattern_idx:
                self.rv2 = i * 3.0 * 0.1
            if idx == 2 + next_pattern_idx:
                self.rv3 = i * 3.0 * 0.1
            if idx == 3 + next_pattern_idx:
                self.rv4 = i * 3.0 * 0.1
            if idx == 4 + next_pattern_idx:
                self.rv5 = i * 3.0 * 0.1
            if idx == 5 + next_pattern_idx:
                self.rv6 = i * 3.0 * 0.1
            if idx == 6 + next_pattern_idx:
                self.rv7 = i * 3.0 * 0.1
            if idx == 7 + next_pattern_idx:
                self.rv8 = i * 3.0 * 0.1
            if idx == 8 + next_pattern_idx:
                self.rv9 = i * 3.0 * 0.1
            if idx == 9 + next_pattern_idx:
                self.rv10 = i * 3.0 * 0.1
            if idx == 10 + next_pattern_idx:
                self.rv11 = i * 3.0 * 0.1
            if idx == 11 + next_pattern_idx:
                self.rv12 = i * 3.0 * 0.1

            idx +=1

    def set_half_pattern_attr(self):
        """Sets the attributes that are calculated at the half of each rhythmic pattern -
        self.acc_av_0_5_pattern and self.perf_av_0_5_pattern (self.bpm_av_0_5_pattern is calculated in self.pm)"""
        acc_values = 0
        perf_values = 0

        for i in range(12):
            idx= -13 + i
            acc_values += self.pm.runits_all[idx].accuracy
            perf_values += self.pm.runits_all[idx].performance

        self.acc_av_0_5_pattern= acc_values * 0.083333 # 0.083333 == 1/12 --> to avoid a division (for program's performance)
        self.perf_av_0_5_pattern= perf_values * 0.083333


