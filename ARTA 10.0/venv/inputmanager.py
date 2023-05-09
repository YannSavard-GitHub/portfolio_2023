"""
Project: Adaptive Rhythmic Training Application (ARTA)
File   : inputmanager.py
Date   : 21/01/2022
Author : Yann Savard

This code is open source, except for some parts that were taken
from external sources and their sources are mentioned in the code.

History: programmed from september 2021 to february 2022 as part of my bachelor project:
"Conception and Evaluation of New Rhythm-Based Dexterity Training Methods with Adaptive Game Mechanics and AI"
"""

import pygame
from pygame.locals import *
import time


class InputManager():
    def __init__(self, g_manager):
        self.gm= g_manager
        self.grm= g_manager.grid_manager
        self.rm= g_manager.rhythm_manager
        self.pm = g_manager.perf_manager


    def manage_key_inputs(self, event, keys):
        """Manages all keyboard inputs."""
        #state play
        if self.gm.game_state == 1:

            #adaptive parameters
            self.manage_adaptive_parameters(keys)

            #verify pressed key
            if self.grm.char_idx < len(self.grm.text) and \
                    self.grm.char_idx < 96:

                if event.type == pygame.KEYDOWN:
                    key = event.key

                    if key >= 32 and key <= 255:

                        runit = self.pm.runits_4_patterns[self.rm.rhythmic_idx_p]
                        runit_to_press = self.pm.runits_4_patterns[self.rm.r_idx_to_press]
                        # --------------------------------------compare keys--------------------------------------------
                        if (event.unicode == runit.char or event.unicode == runit_to_press.char) and \
                                self.gm.notes[-1] >= -1:
                            pygame.key.set_repeat(0, 0)  # set key repeat (stop repeating)

                            if event.unicode == runit_to_press.char:
                                self.grm.set_success_char(runit_to_press)
                                runit = runit_to_press
                            else:
                                if event.unicode == runit.char:
                                    self.grm.set_success_char(runit)

                            time_p = time.perf_counter()

                            # set runit attributes
                            runit.time_pressed = time_p
                            runit.success= 1.0
                            self.pm.successes += 1

                            # adaptive mechanics - verify if parameters should be ajusted now
                            self.pm.manage_adaptive_mechanics(False)

                            # pm (PerformanceManager): set max_bpm
                            if self.gm.bpm > self.pm.max_bpm:
                                self.pm.max_bpm = self.gm.bpm

                            # time pressed
                            self.pm.pressed_times.append(time_p)

                        else:
                            runit.error = 1.0
                            print("error wrong")

                    if key == pygame.K_ESCAPE:
                        plt.close('all')
                        exit()

        #game state test
        end_test=False
        if self.gm.game_state == 0:

            if self.grm.char_idx < len(self.grm.text) and \
                    self.grm.char_idx < 96:

                if event.type == pygame.KEYDOWN:
                    key = event.key

                    if key >= 32 and key <= 255:
                        if event.unicode == self.grm.text[self.grm.char_idx]:
                            #select char
                            if self.grm.char_idx < len(self.grm.text) - 1:
                                self.grm.select_char(True)
                                self.grm.char_idx += 1
                            elif self.grm.char_idx == len(self.grm.text) - 1:
                                end_test = True
                            self.pm.pressed_times.append(time.perf_counter())
                            self.gm.rhythm_manager.play_sound(0)

                    if key == pygame.K_ESCAPE:
                        plt.close('all')
                        exit()

            else: #no more characters in the text string
                end_test = True

        if end_test:
            if self.gm.mode == 0:
                self.grm.sort_letters(self.pm.pressed_times)
            self.gm.finalize_test()


    def manage_adaptive_parameters(self, keys):
        """Manages keyboard inputs related to the adapted mechanics: all arrow keys."""
        if keys[pygame.K_F1]:
            if self.rm.lr_keys_on:
                self.rm.lr_keys_on=False
            else:
                self.rm.lr_keys_on=True

        if self.gm.mode == 0 or (self.gm.mode == 1 and self.rm.lr_keys_on):
            #tempo adjustments
            if keys[pygame.K_UP]:
                if self.grm.param_selected == 1:
                    self.pm.manage_t_modification_frq(1)

                if self.grm.param_selected == 2:
                    self.rm.set_tempo_values(5)
                    pygame.key.set_repeat(20, 20)  # set key repeat

                if self.grm.param_selected == 3:
                    self.pm.manage_adaptive_t_modification_step(1)

            if keys[pygame.K_DOWN]:
                if self.grm.param_selected == 1:
                    self.pm.manage_t_modification_frq(-1)
                if self.grm.param_selected == 2:
                    self.rm.set_tempo_values(-5)
                    pygame.key.set_repeat(20, 20)  # set key repeat
                if self.grm.param_selected == 3:
                    self.pm.manage_adaptive_t_modification_step(-1)


            #set selected parameter
            if keys[pygame.K_LEFT]:
                pygame.key.set_repeat(0, 0)  # stop key repeat
                if self.grm.param_selected != 1:
                    self.grm.param_selected -= 1
            if keys[pygame.K_RIGHT]:
                pygame.key.set_repeat(0, 0)  # stop key repeat
                if self.grm.param_selected != 3:
                    self.grm.param_selected += 1





