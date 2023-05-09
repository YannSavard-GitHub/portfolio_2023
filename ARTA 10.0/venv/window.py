"""
Project: Adaptive Rhythmic Training Application (ARTA)
File   : window.py
Date   : 21/01/2022
Author : Yann Savard

This code is open source, except for some parts that were taken
from external sources and their sources are mentioned in the code.

History: programmed from september 2021 to february 2022 as part of my bachelor project:
"Conception and Evaluation of New Rhythm-Based Dexterity Training Methods with Adaptive Game Mechanics and AI"
"""

import time
import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk
from tkinter.ttk import *

import time
import pyautogui

class PgWindow():
    def __init__(self, game_manager):
        self.gm= game_manager
        self.tk_window= None
        self.interuptions = 0
        self.tech_probs = 0
        self.entry= None #entry in tk window (set in method self.create_tkwindow())
                         # and used in method self.send_data()
        self.B1=None
        self.C1=None
        self.C2=None

        self.should_reset_vars=False

        self.file_saved= False #True if round's performance file has been saved.



    def show_validation_tkwindow(self):
        """
        Shows a dialogue window that manages the saving of the performance data.
        """

        #source of structure: https://www.tutorialspoint.com/python/tk_entry.htm
        if self.should_reset_vars:
            self.reset_vars()
            self.should_reset_vars=False

        self.tk_window = Tk()
        self.tk_window.title("Training Validation")
        frame= tk.Frame(self.tk_window)
        frame.pack(side= TOP)
        frame.grid_columnconfigure(0, minsize=200)
        frame.grid_columnconfigure(1, minsize=200)
        frame.grid_columnconfigure(2, minsize=180)
        L0 = Label(frame, text="")
        L0.grid(row=0, column=0, padx=2, pady=2)
        L1 = Label(frame, text="Pseudonym:                           ", anchor= "w")
        L1.grid(row=1, column=0, padx=2, pady=2)
        L2 = Label(frame, text="   During the training, were there:",  anchor= "w")
        L2.grid(row=2, column=0, padx=2, pady=2)
        L3 = Label(frame, text="- interuptions?            ", anchor= "w")
        L3.grid(row=3, column=2, padx=3, pady=2)
        L4 = Label(frame, text="- technical problems?", anchor= "w")
        L4.grid(row=4, column=2, padx=4, pady=2)
        self.entry = Entry(frame)
        self.entry.grid(row=1, column=2, padx=2, pady=2, ipadx=20)


        # checkboxes
        self.interuptions = tk.IntVar()
        self.interuptions.set(0)
        self.tech_probs = tk.IntVar()
        self.tech_probs.set(0)

        self.C1 = Checkbutton(frame, text="", variable=self.interuptions, \
                         onvalue=1, offvalue=0)
        self.C2 = Checkbutton(frame, text="", variable=self.tech_probs, \
                         onvalue=1, offvalue=0)
        self.C1.grid(row=3, column=3, padx=2, pady=2)
        self.C2.grid(row=4, column=3, padx=2, pady=2)

        self.B1 = Button(frame, text='Save and send results', command= self.save_data)
        self.B1.grid(row=5, column=1, padx=2, pady=2, ipadx=58)

        self.tk_window.protocol("WM_DELETE_WINDOW", self.on_close)

        #position
        sw, sh = pyautogui.size()
        graph_dimX = sw * 0.333333
        graph_dimY = sh / self.gm.tot_graphs * 0.5

        self.tk_window.geometry('%dx%d+%d+%d' % (graph_dimX, graph_dimY, graph_dimX * 1.58, graph_dimY * 0.4))

        #set window and destroy it before note 23,
        # when the first graph is saves in file
        # (otherwise, the window has a problem) - TODO: find exactlywhy!
        if self.gm.notes[-1] == 0:
            count=0
            while True:
                if count == 1:
                    self.tk_window.quit()
                    self.tk_window.withdraw()
                    self.should_reset_vars = True
                    break
                count += 1

                self.tk_window.update_idletasks()
                self.tk_window.update()
        else:
            self.tk_window.mainloop()


    def reset_vars(self):
        """Resets attributes for the next time that the validation window will be shown to manage the performance data."""
        self.tk_window.destroy()
        self.tk_window = None
        self.entry = None
        self.B1 = None
        self.C1 = None
        self.C2 = None
        self.interuptions = None
        self.tech_probs = None

    def on_close(self):
        """Closes the dialogue window and starts a counts down of 3 seconds for the next round."""
        self.tk_window.quit()
        self.tk_window.withdraw()
        self.should_reset_vars=True

        self.gm.rhythm_manager.play_sound(0)
        time.sleep(1.0)
        self.gm.rhythm_manager.play_sound(0)
        time.sleep(1.0)
        self.gm.rhythm_manager.play_sound(0)
        time.sleep(1.0)

        #focus on pygame window and reposition the mouse cursor
        self.gm.focus_on_window()


        self.file_saved=False


    def save_data(self):
        """
        Manages the saving of the performance data and all related dialogue windows.
        """
        if self.gm.perf_manager.data_valid == True:
            self.gm.perf_manager.data_valid = False
        valid=False

        # verify entry input
        text = self.entry.get()
        if text != '':
            valid = True
        else:
            tk.messagebox.showerror(title=None, message="Please enter a pseudonym (not a blank space)")
            return

        # data is valid
        if valid== True and self.interuptions.get() == 0 and self.tech_probs.get() == 0:

            if self.file_saved == False:
                self.gm.perf_manager.data_valid = valid
                # set pseudo_name
                self.gm.perf_manager.pseudo_name = text
                #save data
                self.gm.perf_manager.save_output_data()


                if self.gm.mode == 1 or self.gm.mode == 2:
                    # save round
                    self.gm.grid_manager.save_round()
                    self.file_saved=True
                    # change text for the other hand
                    self.gm.grid_manager.change_hand()


                #continue training
                result= tk.messagebox.askyesno(title="Confirmation", message="Results were saved. Do you want to continue your training?")
            else:
                tk.messagebox.showinfo("Confirmation",
                                       "The file is already saved! You can Close the Validation window to continue your training.")

        # data is invalid
        else:
            valid = False
            result= tk.messagebox.askyesno(title="Cancellation", message="This round's results will not be saved. Do you want to continue your training?")

        if result:
            tk.messagebox.showinfo("Counter",
                                   "Training starts in 3 seconds after you close the Training Validation window!")
            self.gm.perf_manager.continue_training = True

        else:
            tk.messagebox.showinfo(title="Exit program",
                                   message="Ok! Thank you for your interest for this project, have a nice day!")
            self.tk_window.quit()
            self.tk_window.withdraw()
            self.gm.finalize_play()



