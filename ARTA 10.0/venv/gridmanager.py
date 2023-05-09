"""
Project: Adaptive Rhythmic Training Application (ARTA)
File   : gridmanager.py
Date   : 21/01/2022
Author : Yann Savard

This code is open source, except for some parts that were taken
from external sources and their sources are mentioned in the code.

History: programmed from september 2021 to february 2022 as part of my bachelor project:
"Conception and Evaluation of New Rhythm-Based Dexterity Training Methods with Adaptive Game Mechanics and AI"
"""

from venv.runit import RUnit
import pygame
from pygame.locals import *
from PIL import Image, ImageFont, ImageDraw
import math


class GridManager():
    def __init__(self, g_manager):
        self.gm = g_manager

        # objects initialized in method self.set_surface()
        self.rm = None
        self.pm = None

        # screen - dimensions
        self.screen_width = 0
        self.screen_height = 0
        self.chars_dim = (0, 0)
        self.chars_width = 0
        self.chars_heigth = 0
        self.chars_ratio_y = 24

        # text
        self.initial_text="" # just for evaluation mode (self.gm.mode == 1)
        self.text = ""  # for text from file
        self.text_classified = ""

        self.chr_pair_idx=0 # sorted chars pairs (idx for self.classified_chars list)
        self.classified_chars=[]
        self.char_idx = 0  # char index to press in self.text
        self.adapt_char_idx=True #to adapt index if gm.mode == 1
        self.first_char_success=False # True if the image of the runit at index 0 should be set to success image.

        # params of the following lists: [[image, position],[image, position] ...]
        self.char_img_List_base = []  # for char images
        self.char_img_List_actual = []  # for char images (with integrated rhythmic pattern)
        self.char_img_List_grid = []  # for char images in grid
        self.list_grid_prop = []  # stored parameters of char images in grid. (position, kind, number)
        self.char_img_List_way = []  # for char images in the way
        #self.list_way_prop = []  # stored parameters of char images in way. (position)
        self.base_char_img_dict = []  # for char images - keys: ASCII value of character ; values: Tuple: ([0]= image , [1]= image position)

        # ---------------evaluation mode - gm.mode=1 -----------------------------
        self.hand_now = 0  # 0= text for the right hand  1= text for the left hand
        self.txt_start_idx=0 # index in self.text to start the round with
        #-------------------------------------------------------------------------
        # way
        self.way_move = 0.0
        self.start_distance = True

        # grid
        self.ref_grid_pos = (0, 0)

        # arrows
        self.arrow_l_img = None
        self.arrow_r_img = None

        #line
        self.w_line_img = None

        #needle
        self.needle_img = None
        self.needle_min_pos=(0,0)
        self.needle_max_pos=(0,0)
        self.needle_first_pos = (0, 0)
        self.needle_pos=(0,0)

        #parameters
        self.param_selected=2

        #parameters text images
        self.params_img = None
        self.params_selected_img = None
        self.tempo_font= None
        self.tc_delay_font= None
        self.tc_value_font = None

    def set_screen_chars_dimensions(self):
        """Set characters images dimensions according screen dimensions."""
        self.screen_width, self.screen_height = self.gm.screen.get_size()
        #set same width and heigth dimensions (according to screen height)
        self.chars_dim = (round(self.screen_height / self.chars_ratio_y),
                          round(self.screen_height / self.chars_ratio_y))
        self.chars_width, self.chars_heigth = self.chars_dim

    def set_surface(self):
        """Manages the relevant parameters and methods related to the graphical interface in both self.gm.game_states 0 and 1."""
        # initialize objects
        self.rm = self.gm.rhythm_manager
        self.pm = self.gm.perf_manager

        # images
        self.set_screen_chars_dimensions()

        self.generate_char_images()                # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ to uncomment

        self.set_line_needle_arrows()
        self.set_parameter_images()

        # images and text
        if self.gm.play_set == False:
            self.load_txt()

        # lists
        if self.gm.game_state == 0:
            self.set_lists()
        if self.gm.game_state == 1:
            self.gm.rhythm_manager.set_rp_lists()

        self.set_images_pos()

        # variables
        self.way_move = 1 / self.gm.time_division

        if self.gm.game_state == 1:
            self.char_idx = -1

    def set_parameter_images(self):
        """Renders adaptive parameters text fonts on the graphical interface."""

        #fonts
        pygame.font.init()
        font = pygame.font.SysFont('calibri', 24)

        # parameter images
        # ----------------------------------------------------------------
        if self.param_selected == 1:
            font.set_underline(True)
        self.tc_delay_font = font.render(f'T-modification-frq (chr):  {self.pm.t_modification_frq}', True, (255, 255, 255))

        font.set_underline(False)
        if self.param_selected == 2:
            font.set_underline(True)
        self.tempo_font = font.render(f'Tempo (chr/min):  {int(self.gm.bpm)}', True, (255, 255, 255))

        font.set_underline(False)
        if self.param_selected == 3:
            font.set_underline(True)
        self.tc_value_font = font.render(f'T-modification-Step (chr/min):  {self.pm.t_modification_step}', True, (255, 255, 255))

        #positions
        p1 = (self.ref_grid_pos[0] + self.chars_width * 1.8, self.ref_grid_pos[1] + self.chars_width * 5) # bottom-left
        p2= (self.ref_grid_pos[0] + self.chars_width * 10.25, self.ref_grid_pos[1] + self.chars_width * 5) # bottom-middle
        p3 = (self.ref_grid_pos[0] + self.chars_width * 16.9, self.ref_grid_pos[1] + self.chars_width * 5) # bottom-right

        self.gm.screen.blit(self.tempo_font, p2)
        self.gm.screen.blit(self.tc_delay_font, p1)
        self.gm.screen.blit(self.tc_value_font, p3)
        # ----------------------------------------------------------------

    def manage_surface(self):
        """Renders the black background and manages the methods related to graphics and their movement in the
        graphical interface. Manages parameters of the last runit to be pressed, if it was pressed in time."""
        self.gm.screen.fill((0, 0, 0))
        self.show_grid_images()

        # game state play
        if self.gm.game_state == 1:
            self.move_way_images()
            self.move_needle()
            self.set_parameter_images()


            #set runit attributes if the last runit was pressed at the end of the grid (index 24 becomes index 0)
            if self.first_char_success  == True and self.rm.rhythmic_idx_p == 0:
                runit= self.pm.runits_4_patterns[0]
                self.set_success_char(runit)
                runit.error=0.0
                runit.time_pressed= self.pm.pressed_times[-1]
                self.first_char_success = False


        pygame.display.update()

    def manage_text_indexes(self):
        """
        Manages text indexes at the end of a trial in self.gm.mode 0.
        """
        # append chr_pair_idx and set new text
        if self.chr_pair_idx == 0:
            self.chr_pair_idx = 1
        else:
            self.chr_pair_idx = (self.chr_pair_idx + 1) % len(self.classified_chars)
        self.set_text(self.chr_pair_idx)

    def generate_char_images(self):
        """Generates character's text images with the base images in path 'Images_base'
        and saves them in path 'Images'. The first 4 base image are related to rhythmic values 0 to 3 (in self.rm),
        ISS.png is the selected image during the test at the beginning of rounds (self.gm.game_state 0) and
        _Isuccess.png is the image appearing when a character is pressed successfully during a round. All images all
        resized just once at the start of the program.
        """

        for i in range(255 - 32):
            for j in range(10):
                # Images
                if j == 0:
                    img = Image.open("Images_base/IVOID.png")
                if j == 1:
                    img = Image.open("Images_base/IS.png")
                if j == 2:
                    img = Image.open("Images_base/IA.png")
                if j == 3:
                    img = Image.open("Images_base/IAZ.png")
                if j == 4:
                    img = Image.open("Images_base/ISS.png")
                if j == 5:
                    img = Image.open("Images_base/_ISUCCESS.png")

                # add font
                size = img.size[1]
                font = ImageFont.truetype('Fonts/DejaVuSans.ttf', round(0.8 * size))
                char = chr((i + 32))
                image_editable = ImageDraw.Draw(img)
                image_editable.text((0.2 * size, 0), char, (0, 0, 0), font=font)

                # scale
                img = img.resize((self.chars_heigth, self.chars_heigth))

                # save image
                text = f"Images/{j}-{ord(char)}.png"
                img.save(text)

    def set_success_char(self, runit):
        """Sets the success attribute of the runit given in parameter to True and changes the related image in the list
        self.char_img_List_grid, before the image success image of this runit's text character is rendered. """
        idx = 0

        # game state test
        if self.gm.game_state == 0:
            idx = self.char_idx

        # game state play
        if self.gm.game_state == 1:
            idx = runit.idx
            if self.first_char_success == True:
                idx=0
                self.first_char_success = False
            elif idx == 24:
                self.first_char_success = True
                return
            else:
                idx = runit.idx  #self.rm.rhythmic_idx_p# get previous rhythmic index (previous image's index)

            if self.rm.all_rhythmic_patterns[idx][0] != 0:
                # get success kind
                kind = 5
                number = runit.number

                img = self.get_image(kind, number)

                # replace image in char_img_List_grid
                self.char_img_List_grid[idx] = img
                self.show_grid_images()

    def select_char(self, next_char):
        """Selects the next runit's text character to be pressed in the graphical interface and manages the related lists."""
        # get selected kind

        # game state test
        if self.gm.game_state == 0:
            idx = self.char_idx
            if next_char:  # get next index -> to select the next char (if idx is not the first one)
                idx += 1

        # game state play
        if self.gm.game_state == 1:
            idx = self.rm.rhythmic_idx_p # get next index -> ... (if idx is not the first one)

        kind = self.list_grid_prop[idx][1]
        number = self.list_grid_prop[idx][2]

        if kind == 1:
            kind = 4
        else:
            return

        img = self.get_image(kind, number)

        # replace image in self.char_img_List_grid
        # and its parameter 1 (kind) in self.list_grid_prop
        self.char_img_List_grid[idx] = img
        self.list_grid_prop[idx][1] = kind
        self.show_grid_images()

        if self.gm.game_state == 1:

            self.pm.runits_4_patterns[idx].kind=kind

    def get_image(self, kind, asc_value):
        """
        Gets the image the kind and asc_value given in parameter.
        :param kind: image in path 'Images' (rhythmic value, selected or success)
        :param asc_value: the asc II keyboard character's font image.
        :return: the loaded image suitable for use by pygame.
        """
        try:
            img = pygame.image.load(f"Images/{kind}-{asc_value}.png")
        except:
            pass

        return img

    def show_grid_images(self):
        """
        Shows the text images in the grid at the bottom of the graphical interface, the white arrows and the white line above the grid.
        :return:
        """
        if self.gm.game_state == 0 and self.char_idx == 0:
            self.select_char(False)

        for i in range(len(self.char_img_List_grid)):
            self.gm.screen.blit(self.char_img_List_grid[i],
                                self.pm.runits_4_patterns[i].grid_pos)

        # arrows
        self.gm.screen.blit(self.arrow_l_img,  # on the right of the grid
                            (self.ref_grid_pos[0] + self.chars_width * 24, self.ref_grid_pos[1]))

        self.gm.screen.blit(self.arrow_r_img,  # on the left of the grid
                            (self.ref_grid_pos[0] - self.chars_width, self.ref_grid_pos[1]))
        #white line
        height= self.ref_grid_pos[1] - int(round(self.chars_width * 0.250))
        self.gm.screen.blit(self.w_line_img,  # on the left of the grid
                            (self.ref_grid_pos[0], height))

    def move_needle(self):
        """Moves the vertical needle in the text grid at the bottom of the screen from left to right, up to the last
        position at the end of the grid, where it then returns at the starting position at the left of the grid."""

        # set needle position
        if self.gm.notes[-1] < 0:  # at the beginning
            self.needle_pos = self.needle_min_pos
        elif self.gm.notes[-1] == 0: # at the beginning
            self.needle_pos= (self.needle_min_pos[0] + self.chars_width * 1.625 + 1, self.needle_min_pos[1])
            self.gm.screen.blit(self.needle_img,  self.needle_pos)
        else:
            #needle at the max position (x axis)
            if self.needle_pos[0] >= self.needle_max_pos[0] - int(round(self.chars_width * 0.125) + 1):
                self.needle_pos = self.needle_min_pos
            else:
                self.needle_pos = (self.needle_pos[0] + self.chars_width * self.way_move, self.needle_pos[1])

            self.gm.screen.blit(self.needle_img, self.needle_pos)

    def move_way_images(self):
        """Manages the movement of the way images that move from top to bottom in the center of the screen."""
        # position images
        for i in range(len(self.char_img_List_way)):

            img, pos = self.char_img_List_way[i], self.pm.runits_4_patterns[i].way_pos

            # set image position
            new_pos = (pos[0], pos[1] + self.chars_heigth * self.way_move)
            #self.list_way_prop[i] = new_pos
            #set position in list
            self.pm.runits_4_patterns[i].way_pos= new_pos

            if pos[1] > self.chars_heigth * 1 and pos[1] < self.chars_heigth * 15 - self.chars_heigth * 0.325:
                self.gm.screen.blit(img, new_pos)

    def update_lists(self, set_lists):
        """Updates and switches the lists when the needle is passed the last text character in the text grid."""
        # char_idx ajustment if the first index of the present rhythmic pattern was 0
        if self.gm.mode == 0:
            if self.rm.r_patterns_count[-1] >= 2:  # change index at the end of the pattern where idx 0== 0
                if self.rm.rp1[0] == 0:
                    self.char_idx -= 1

        #switch lists
        self.rm.set_rp_lists()

        #images
        self.set_images_pos()

    def set_lists(self):
        """Resets and/or sets the list related to all text images in the graphical interface."""
        if len(self.char_img_List_base) != 0:
            self.char_img_List_base.clear()
            self.char_img_List_grid.clear()
            self.list_grid_prop.clear()
            self.char_img_List_way.clear()
            self.pm.runits_4_patterns.clear()

        idx = self.char_idx % 96
        if self.gm.mode == 0: # training mode for the A.I.
            if self.rm.r_patterns_count[-1] >= 1: #important ajustment of indexes after pattern switches
                idx_txt=idx
                idx = 0
            else:
                idx_txt = 0
        else:
            idx_txt = idx
            idx = 0

        for i in range(len(self.text)):
            idx_txt = idx_txt % 96
            # append images in lists
            # state test
            if self.gm.game_state == 0:
                kind = 1

            # state play
            if self.gm.game_state == 1:
                # get image kind
                if idx < 24:
                    kind = self.rm.rhythmic_patterns_now[0][idx]
                if idx >= 24 and idx < 48:
                    kind = self.rm.rhythmic_patterns_now[1][idx % 24]
                if idx >= 48 and idx < 72:
                    kind = self.rm.rhythmic_patterns_now[2][idx % 24]
                if idx >= 72 and idx < 96:
                    kind = self.rm.rhythmic_patterns_now[3][idx % 24]

            if self.gm.game_state == 0:
                number = ord(self.text[idx_txt])

            if self.gm.game_state == 1:
                number = ord(self.text[idx_txt])

                if self.rm.r_patterns_count[-1] >= 1:
                    pass
                    # adjust index after pattern switch
                    # idx_txt = (idx_txt + 24) % 96
                    # char = self.text[idx_txt]
                    # number = ord(char)


            # get image
            img = self.get_image(kind, number)

            # append img to lists
            self.char_img_List_base.append(img)
            self.char_img_List_grid.append(img)
            self.list_grid_prop.append([(0, 0), kind, number])
            self.char_img_List_way.append(img)
            #self.list_way_prop.append((0, 0))
            if self.gm.game_state == 1:
                if kind != 0:
                    self.rm.all_rhythmic_patterns[idx][1] = self.text[idx_txt]

            # RUnit

            runit = RUnit(self.gm)
            runit.image = img
            runit.number=number
            runit.kind=kind
            runit.neural_char_value=number/255
            runit.idx= idx
            #runit.char
            if self.gm.game_state == 1:
                if kind == 0:
                    runit.char = ''
                    if idx == 0:
                        idx_txt += 1
                else:
                    runit.char=self.text[idx_txt]

            self.pm.runits_4_patterns.append(runit)

            #set indexes
            idx += 1
            if self.gm.game_state == 0 and idx == 95: #last char of test
                return
            if self.gm.game_state == 1:
                idx = idx % 96

            if kind != 0:
                idx_txt += 1

    def set_images_pos(self):
        """Sets the positions of way and grid text characters, as well as the needle's positions on the graphical interface."""
        # way positions according to self.start_distance

        # (True= position is 4 * self.chars_heigth higher than the
        # position where images should be pressed)
        if self.start_distance and self.rm.r_patterns_count[-1] == 0:
            way_pos1_x, way_pos1_y = (round(self.screen_width * 0.5 - self.chars_width * 0.5),
                                      round(self.chars_heigth * 11 - self.chars_heigth * 0.250))
        # if the pattern count is more than 0, the images are ajusted
        # by a distance of self.chars_heigth * 0.5 to compensate the switch
        # of the rhythmic patterns that occured
        # in th game (half a beat after the last char)
        elif self.start_distance == False and self.rm.r_patterns_count[-1] > 0:
            way_pos1_x, way_pos1_y = (round(self.screen_width * 0.5 - self.chars_width * 0.5),
                                      round(self.chars_heigth * 14 + self.chars_heigth * 0.5)) # <---------- 0.5 ajustment
        else:
            way_pos1_x, way_pos1_y = (round(self.screen_width * 0.5 - self.chars_width * 0.5),
                                      round(self.chars_heigth * 15 - self.chars_heigth * 0.0))

        for i in range(len(self.pm.runits_4_patterns)):
            self.pm.runits_4_patterns[i].way_pos=(way_pos1_x, way_pos1_y - i * self.chars_heigth)
            #self.list_way_prop[i] = (way_pos1_x, way_pos1_y - i * self.chars_heigth)

        # grid positions
        grid_pos1_x, grid_pos1_y = (
        round(self.screen_width * 0.5 - 12 * self.chars_heigth), round(self.chars_heigth * 16))
        self.ref_grid_pos = (grid_pos1_x, grid_pos1_y)

        row = -1
        for i in range(len(self.char_img_List_grid)):
            i_mod = i % 24
            if i_mod == 0:
                row += 1
            self.pm.runits_4_patterns[i].grid_pos = \
                (grid_pos1_x + i_mod * self.chars_heigth, grid_pos1_y + row * self.chars_heigth)

        #needle position
        self.needle_min_pos= (self.ref_grid_pos[0] - int(round(self.chars_heigth * 0.5)), self.ref_grid_pos[1])
        self.needle_max_pos = (self.ref_grid_pos[0] +
                               self.chars_width * 23 + int(round(self.chars_heigth * 0.5)), self.ref_grid_pos[1])


    def generate_param_images(self):
        """Loads the adaptive mechanic parameter's images from file, resizes them and saves them to path 'Images'
         to be loaded and used by pygame."""

        img = Image.open(f"Images_base/IS.png")
        img2 = Image.open(f"Images_base/ISS.png")
        img = img.resize((self.chars_width * 4, self.chars_heigth))
        img2 = img.resize((self.chars_width * 4, self.chars_heigth))
        img.save(f"Images/IS.png")
        img.save(f"Images/ISS.png")
        self.params_img = pygame.image.load(f"Images/IS.png")
        self.params_selected_img = pygame.image.load(f"Images/ISS.png")

    def set_line_needle_arrows(self):
        """Loads and resizes the arrow, white line and needle images, saves them to path 'Images' and reloads them to
        be used by pygame."""

        # left arrow images
        img = Image.open(f"Images_base/Arrow-Left.png")
        img = img.resize((self.chars_heigth, self.chars_heigth))
        img.save(f"Images/Arrow-Left-scaled.png")
        self.arrow_l_img = pygame.image.load(f"Images/Arrow-Left-scaled.png")

        # right  arrow images
        img2 = Image.open(f"Images_base/Arrow-Right.png")
        img2 = img2.resize((self.chars_heigth, self.chars_heigth))
        img2.save(f"Images/Arrow-Right-scaled.png")
        self.arrow_r_img = pygame.image.load(f"Images/Arrow-Right-scaled.png")

        # white line image
        img3 = Image.open(f"Images_base/White-Line.png")
        height= int(round(self.chars_heigth * 0.0625))
        img3 = img3.resize((self.chars_width * 24, height))
        img3.save(f"Images/white-line-scaled.png")
        self.w_line_img = pygame.image.load(f"Images/white-line-scaled.png")

        # needle image
        img3 = Image.open(f"Images_base/Needle.png")
        img3 = img3.resize((self.chars_width, self.chars_heigth))
        img3.save(f"Images/Needle.png")
        self.needle_img = pygame.image.load(f"Images/Needle.png")


    def load_first_char(self, first_trial):
        """Loads the first text char from file 'Text/chr-round-evaluation.txt' to start the round with.
        args:
        first_trial: True if this round is the first one sice the start of the application"""


        #load round according to the present day ()
        if self.rm.day_int == 1:
            file_name = 'Performance/rounds/evaluation-rounds-day1.txt'
        else:
            file_name = 'Performance/rounds/evaluation-rounds-day2.txt'

        txt = open(file_name, 'r', encoding="utf8")
        line = txt.readline()
        #line= line[:-1]

        # set current round
        if first_trial:
            round_number=int(line)
            if round_number > 0:
                self.gm.round = round_number
                # set txt_start_idx
                self.txt_start_idx = (math.ceil(round_number / 2) - 1) % 4
        else:
            round_number = int(line)

            self.gm.next_round= round_number            # set txt_start_idx
            self.txt_start_idx = (math.ceil(round_number / 2) - 1) % 4

        #get hand and set the appropriate hand's text
        if round_number % 2 == 0 and self.gm.round != 0:
            self.hand_now = 0 # right hand
            hand_txt = self.initial_text[:4]
        else:
            self.hand_now = 1 # left hand
            hand_txt = self.initial_text[4:]

        #set text with the right index
        new_txt=""
        idx=0
        for i in range(4):
            idx= (i + self.txt_start_idx) % 4
            new_txt += hand_txt[idx]

        self.text = new_txt
        if first_trial == False:
            self.resize_text()



    def save_round(self):
        """Writes the round value in the appropriate files Performance/rounds/evaluation-rounds-day1 or day_2,
        according to training day."""

        # write next round in text file
        if self.rm.day_int == 1:
            file_name= 'Performance/rounds/evaluation-rounds-day1.txt'
        else:
            file_name = 'Performance/rounds/evaluation-rounds-day2.txt'

        txt = open(file_name, 'w', encoding="utf8")
        txt.truncate(0)
        txt.write(str(self.gm.round + 1))
        txt.close()

    def load_txt(self):
        """Loads the text for the test from path 'Text' at the beginning of rounds (self.gm.game_state 0), according to self.gm.mode
        (type of training - for the A.I. or evaluation)."""
        self.rm.get_day()
        if self.gm.mode == 0:
            file_name='Text/text.txt'
        else:
            file_name = 'Text/text-evaluation.txt'
        line = "0"
        txt_line = open(file_name, 'r', encoding="utf8")
        line_available = True
        while line_available:
            line = txt_line.readline()
            if line == "":
                line_available = False
            else:
                self.text += line

        temp_txt = self.text
        new_txt = temp_txt.replace("\n", " ")

        if self.gm.mode == 1:
            self.set_text_evaluation()
        else:
            self.text = new_txt

        txt_line.close()


    def resize_text(self):
        """Resizes self.text, so that it has a lenght of 96."""
        new_text = self.text
        new_text2 = ""

        # text shorter then 96 chars: repeat text up to 96 chars
        if len(new_text) < 96:
            for i in range(96):
                new_text += self.text
            self.text = new_text
        # text longer then 96 chars: take chars up to 96 chars
        if len(new_text) > 96:
            for i in range(96):
                new_text2 += new_text[i]
            self.text = new_text2

    def sort_letters(self, pressed_times_list):
        """Classifies letters that were typed during the test of self.gm.mode 0, in pairs, according to the speed
        that they were pressed, so that the training can be done with the weakest letter transitions performed during
        the test. The pairs are classified from the slowest to the fastest."""
        speeds_values = []
        temp_time_values = []
        for i in range(len(pressed_times_list) - 1):
            speed = pressed_times_list[i + 1] - pressed_times_list[i]

            # lists with corresponding indexes
            speeds_values.append(speed)
            temp_time_values.append((pressed_times_list[i], pressed_times_list[i + 1]))

        sorted_speeds = []

        sorted_speeds = self.quick_sort(speeds_values)

        for i in sorted_speeds:
            # get index of speed in sorted_speeds list to use in temp_time_values list
            idx = speeds_values.index(i)
            # get the 2 times related to that speed value (sorted_speeds[i])
            time1 = temp_time_values[idx][0]
            time2 = temp_time_values[idx][1]

            # get chars in self.text using the index of their associated pressed time
            idx = pressed_times_list.index(time1)

            # use index to get the right char
            self.text_classified += self.text[idx]
            self.text_classified += self.text[idx + 1]

        self.classified_chars = []
        for i in range(0, len(self.text_classified), 2):
            self.classified_chars.append([self.text_classified[i], self.text_classified[i + 1]])



        print("self.text_classified= ", self.text_classified)
        print("classified_chars= ", self.classified_chars)
        print("length= ", len(self.classified_chars))
        print("self.char_idx= ", self.char_idx)
        print("text= ", len(self.text))

        self.set_text(self.chr_pair_idx)

    def change_hand(self):
        """Changes the letters (self.text) at the beginning and during a round in self.gm.mode 1, so that the text
        one hand switches to the other. (adsf becomes ;klj and vice versa) """
        self.load_first_char(False)
        return


    def set_text_evaluation(self):
        """Sets the text of the evaluation mode 1 (self.gm.mode) for the test at the beginning of the training."""

        self.initial_text = self.text #first half of the text in text-evaluation.txt
        self.load_first_char(True)

    def set_text(self, idx):
        """
        Sets self.text in mode 0 (self.gm.mode) according to the classification of characters
        (slowest pressed delay to fastest) made during the test at the beginning of the round.
        :param idx: index for self.classified_chars list (self.chr_pair_idx)
        :return: nothing
        """
        if idx == len(self.classified_chars) or len(self.classified_chars) == 1:
            idx=0
            self.chr_pair_idx=0
        txt=""
        for i in range(48):
            txt+= self.classified_chars[idx][0]
            txt+= self.classified_chars[idx][1]
        self.text=txt
        print("self.text= ", len(self.text))

    # source: Thibaut - https://stackoverflow.com/questions/26858358/a-recursive-function-to-sort-a-list-of-ints
    def quick_sort(self, l):
        """Sorts values (floats or ints) from the biggest to the smallest."""
        if len(l) <= 1:
            return l
        else:
            return self.quick_sort([e for e in l[1:] if e >= l[0]]) + [l[0]] + \
                   self.quick_sort([e for e in l[1:] if e < l[0]])



