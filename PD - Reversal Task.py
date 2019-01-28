from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemandmulti')
#Config.set('graphics', 'fullscreen', '1')
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from win32api import GetSystemMetrics
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.core.audio import SoundLoader
from kivy.uix.vkeyboard import VKeyboard
from functools import partial
import random
import os
import time


class ImageButton(ButtonBehavior,Image):
    def __init__(self,**kwargs):
        super(ImageButton,self).__init__(**kwargs)

class Experiment_Staging(FloatLayout):
    def __init__(self,**kwargs):
        super(Experiment_Staging,self).__init__(**kwargs)
        self.monitor_x_dim = GetSystemMetrics(0)
        self.monitor_y_dim = GetSystemMetrics(1)
        self.size = (self.monitor_x_dim,self.monitor_y_dim)

        self.curr_dir = os.getcwd()
        self.trial_displayed = False
        self.data_dir = self.curr_dir + "\\Data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.presentation_delay_start = False
        self.image_on_screen = False
        self.feedback_displayed = False

        self.delay_length = 10

        self.max_trials = 72 # MAX Number of Trials / Session
        self.max_time = 3600 # Cutoff Time / Session (sec)

        self.time_elapsed = 0 # How long has elapsed during the protocol
        self.start_time = time.time() # Timer to track ITI/Stim Pres/etc
        self.start_iti_time = 0 # Start time for timer to track

        self.iti_time = 8 # Delay time between trials
        self.presentation_delay_time = 10 # Amount of time between start and presentation (Trial # 1)
        self.feedback_length = 2 # Amount of time Sound/Cue are Present


        self.image_list = ['left','right'] # Names of Files #
        self.image_pos = [-1,1] # Index position for Image Shift from Center

        #SELECT CORRECT IMAGE###########
        self.correct_image_index = 1 ## 0 = LEFT, 1 = RIGHT)

        # Set the incorrect based on correct
        if self.correct_image_index == 0:
            self.incorrect_image_index = 1
        elif self.correct_image_index == 1:
            self.incorrect_image_index = 0

        # Random # Generator to determine which side each stimuli goes to
        self.correct_image_pos = random.randint(0,1)
        if self.correct_image_pos == 0:
            self.incorrect_image_pos = 1
        elif self.correct_image_pos == 1:
            self.incorrect_image_pos = 0
        ###############################

        self.lat = 0 # Placeholder for Latency Time

        self.current_trial = 1 # Current Trial #
        self.current_correct = 0 # Is current trial a correct one?
        self.current_correction = 0 # Is current trial requiring correction?

        self.correct_sound_path = self.curr_dir + "\\Sounds\\Correct.wav" # Filepath to Correct Sound
        self.incorrect_sound_path = self.curr_dir + "\\Sounds\\Incorrect.wav" # Filepath to Incorrect Sound
        self.feedback_sound = SoundLoader.load(self.correct_sound_path) # Loads sound to placeholder
        self.feedback_sound.loop = True # Set Sound-Repeating Function

        self.delay_hold_button = ImageButton(source='%s\\Images\\white.png' % (self.curr_dir), allow_stretch=True) # Set Delay Button Filepath
        self.delay_hold_button.size_hint = (.25,.25) # Set Delay Button Size (relative to screen size)
        self.delay_hold_button.pos = ((self.center_x - (0.125 * self.monitor_x_dim)),(self.center_y - (0.125 * self.monitor_y_dim) - (0.4 * self.monitor_y_dim))) # Set Relative Position of Delay Button


        Clock.schedule_interval(self.clock_update, 0.001) # Run Timer Function Every 1000th of a second (Precision)
        self.id_entry() #Move to next stage to Enter Filename



    def id_entry(self):
        self.id_instruction = Label(text = 'Please enter a participant ID #:') # Text Label
        self.id_instruction.size_hint = (.5,.2) #Label Size Relative to Screen
        self.id_instruction.pos = ((self.center_x - (0.25 * self.monitor_x_dim)),(self.center_y - (0.1*self.monitor_y_dim) + (0.3*self.monitor_y_dim)))
        # Label Position Relative to Screen
        self.id_entry = TextInput(text='', multiline=False) #Input Field
        self.id_entry.size_hint = (.3,.1) #Input Fieled Size
        self.id_entry.pos = ((self.center_x - (0.15 * self.monitor_x_dim)),(self.center_y - (0.05*self.monitor_y_dim) + (-0.3*self.monitor_y_dim)))
        # Input Field Position

        self.id_button = Button(text='OK') # OK Buttom Initialization
        self.id_button.size_hint = (.1,.1) # OK Button Size Relative to Screen
        self.id_button.pos = ((self.center_x - (0.05 * self.monitor_x_dim)),(self.center_y - (0.05*self.monitor_y_dim) + (-0.4*self.monitor_y_dim)))
        # OK Button Position Relative to Screen
        self.id_button.bind(on_press = self.clear_id) # Bind function self.clear_id() to button press

        self.add_widget(self.id_instruction) # Put Label on Screen
        self.add_widget(self.id_entry) # Put Entry Field on Screen
        self.add_widget(self.id_button) # Put OK Button on Screen

    def clear_id(self,*args):
        self.id_no = self.id_entry.text # Filename moved to string variable
        self.id_entry.hide_keyboard() #If keyboard is present, force its removal

        self.participant_data_path = self.data_dir + '\\%s.csv' % (self.id_no) # Create Filepath for Data
        self.data_col_names = 'TrialNo,Correct,Correction Trial,Response Latency' #Set Column Names
        self.data_file = open(self.participant_data_path, "w+") #Create new csv file
        self.data_file.write(self.data_col_names) # Write column names to file
        self.data_file.close() #Close editing of file - ESSENTIAL

        self.remove_widget(self.id_instruction) # Remove Instructions
        self.remove_widget(self.id_entry) # Remove text-box
        self.remove_widget(self.id_button) # Remove Ok Button
        self.trial_initiation() # Start Trial Initiation


    def trial_initiation(self):
        self.initiation_image_wid = ImageButton(source='%s\\Images\\white.png' % (self.curr_dir), allow_stretch=True) # Initiation Button Filepath
        self.initiation_image_wid.size_hint = (.25,.25) #Initiation Button Size Relative to Screen
        self.initiation_image_wid.pos = ((self.center_x - (0.125 * self.monitor_x_dim)),(self.center_y - (0.125 * self.monitor_y_dim) - (0.4 * self.monitor_y_dim)))
        #Initiation Button Position Relative to Screen
        self.initiation_image_wid.bind(on_press= self.initiation_detected) #Bind self.initiation_detected() to press
        self.add_widget(self.initiation_image_wid) # Create Button
        self.initiation_start_time = time.time() # Set Start of Initiation

    def initiation_detected(self,*args):
        self.remove_widget(self.initiation_image_wid) # Remove Initaition Button
        #self.delay_hold_button.bind(on_release= self.premature_response) ## Disable Path for Dog
        #self.add_widget(self.delay_hold_button) # Replace with Delay Interval Button
        self.presentation_delay() # Start Presentation Delay

    def presentation_delay(self,*args):
        if self.presentation_delay_start == False: # check if first pass
            self.presentation_delay_start_time = time.time() # Delay Start
            Clock.schedule_interval(self.presentation_delay,0.01) # Repeat Function Every 100th/Second
            self.presentation_delay_start = True # Prevent Second Pass
        if (self.current_time - self.presentation_delay_start_time) >= self.presentation_delay_time: # If Delay Over
            Clock.unschedule(self.presentation_delay) # Stop Repeat
            #self.delay_hold_button.unbind(on_release=self.premature_response) # Prevent Premature
            self.presentation_delay_start = False # Reset Flag
            self.image_presentation() # Activate self.image_presentation() function

    def image_presentation(self,*args):
        if self.image_on_screen == False: #Ensure one pass
            self.delay_hold_button.unbind(on_release=self.premature_response) #Remove Function Call

            self.correct_image_wid = ImageButton(source='%s\\Images\\%s.png' % (self.curr_dir,self.image_list[self.correct_image_index]), allow_stretch=True)
            self.correct_image_wid.size_hint = (.5, .5)
            self.correct_image_wid.pos = (
            (self.center_x - (0.25 * self.monitor_x_dim) + (0.25 * self.image_pos[self.correct_image_pos] * self.monitor_x_dim)), (self.center_y - (0.25 * self.monitor_y_dim)))
            self.correct_image_wid.bind(on_press= self.response_correct)
            self.add_widget(self.correct_image_wid)
            # Create Correct Image (filepath,size,position,binding,activating)

            self.incorrect_image_wid = ImageButton(source='%s\\Images\\%s.png' % (self.curr_dir,self.image_list[self.incorrect_image_index]), allow_stretch=True)
            self.incorrect_image_wid.size_hint = (.5, .5)
            self.incorrect_image_wid.pos = (
            (self.center_x - (0.25 * self.monitor_x_dim) + (0.25 * self.image_pos[self.incorrect_image_pos] * self.monitor_x_dim)), (self.center_y - (0.25 * self.monitor_y_dim)))
            self.incorrect_image_wid.bind(on_press= self.response_incorrect)
            self.add_widget(self.incorrect_image_wid)
            # Create Incorrect Image (filepath,size,position,binding,activating)


            self.image_pres_time = time.time() # Start time for image presentation
            self.image_on_screen = True # Change Flag

    def response_correct(self, *args):
        self.image_touch_time = time.time() # End Time
        self.remove_widget(self.correct_image_wid) # Remove Correct
        self.remove_widget(self.incorrect_image_wid) # Remove Incorrect

        self.lat = self.image_touch_time - self.image_pres_time #Time to hit screen

        self.current_correct = 1 # Set trial state to correct
        self.correction_active = False # Set Correction Active to False
        self.feedback_sound = SoundLoader.load(self.correct_sound_path) # Set Sound Filepath

        self.record_data() # Activate Data Recorder
        self.set_new_trial_configuration() # Get New Trial Parameters
        self.feedback_report() # Activate Feedback System
        self.delay_hold_button.bind(on_press=self.start_iti) # Activate ITI Call
        self.add_widget(self.delay_hold_button) # Present Button

    def response_incorrect(self, *args):
        self.image_touch_time = time.time() # Get End Time
        self.remove_widget(self.correct_image_wid) # Remove Correct
        self.remove_widget(self.incorrect_image_wid) # Remove Incorrect

        self.lat = self.image_touch_time - self.image_pres_time # Get Latency to Respond

        self.correction_active = True #Set Correction Trial State to Active
        self.feedback_sound = SoundLoader.load(self.incorrect_sound_path) # Load Incorrect Soundpath

        self.current_correct = 0 # Set Flag to Incorrect
        self.record_data() # Activate Data Recorder
        self.feedback_report() # Activate Feedback System
        self.delay_hold_button.bind(on_press=self.start_iti) # Set Delay Button Call Function
        self.add_widget(self.delay_hold_button) # Create Delay Button

    def premature_response(self,*args):
        if self.image_on_screen == True:
            return None
        Clock.unschedule(self.end_iti)
        Clock.unschedule(self.presentation_delay)
        if self.feedback_displayed == True:
            self.remove_widget(self.feedback_wid)

        self.image_on_screen = False
        self.feedback_string = 'WAIT FOR IMAGE - PLEASE TRY AGAIN'
        self.correction_active = True
        self.current_correct = 2
        self.lat = ''
        self.delay_hold_button.bind(on_press=self.start_iti)
        self.record_data()
        self.feedback_report()

    def record_data(self):
        self.data_file = open(self.participant_data_path, "a") # Open/Append to CSV file for this session
        self.data_file.write("\n") # Start New Row
        self.data_file.write("%s,%s,%s,%s" % (self.current_trial,self.current_correct,self.current_correction,self.lat))
        ## Record: Current Trial #, Trial Correct (0-Incorrect, 1-Correct), Trial Correction (0-NonCorrection,1-Correction)
        ## Response Latency (Image Pres --> Screen Response)
        self.data_file.close() # Close File

        if self.current_correct == 0: #If Current Trial wrong, next will record as correction trial
            self.current_correction = 1
        if self.current_correct == 1:
            self.current_correction = 0

    def set_new_trial_configuration(self):
        # If Correct, New Configuration will set new parameters
        self.current_correction = 0 # Reset correction to false
        self.current_trial += 1 # Add to current trial #


        # Get New Position (Random)
        self.correct_image_pos = random.randint(0,1)
        if self.correct_image_pos == 0:
            self.incorrect_image_pos = 1
        elif self.correct_image_pos == 1:
            self.incorrect_image_pos = 0

    def feedback_report(self,*args):
        self.feedback_displayed = True
        self.iti_clock_trigger = False
        #self.feedback_wid = Label(text=self.feedback_string, font_size='50sp')
        #self.feedback_wid.size_hint = (.5,.3)
        #self.feedback_wid.pos = ((self.center_x - (0.25 * self.monitor_x_dim)),(self.center_y - (0.15*self.monitor_y_dim)))
        #self.add_widget(self.feedback_wid)

        self.feedback_sound.play()
        self.start_feedback_time = time.time()

    def start_iti(self,*args):
        self.delay_hold_button.unbind(on_press=self.start_iti) # Unbind Function
        #self.delay_hold_button.bind(on_release=self.premature_response) # Disable for now
        self.iti_clock_trigger = False # Set Flag
        self.image_on_screen = False # Set Flag
        self.remove_widget(self.delay_hold_button)  # Remove Delay Button
        self.end_iti() # Start end_iti() function

    def end_iti(self,*args):
        if self.iti_clock_trigger == False: # On First Pass
            Clock.schedule_interval(self.end_iti, 0.01) # Repeat Function every 100th/second
            self.start_iti_time = time.time() # Get ITI Start
            self.iti_clock_trigger = True # Set Flag
        if ((self.current_time - self.start_feedback_time) >= self.feedback_length) and (self.feedback_displayed == True): # When Feedback Time Ends
            #self.remove_widget(self.feedback_wid)
            self.feedback_sound.stop() # Stop Sound
            self.start_iti_time = time.time() # Modify ITI Time for post-feedback period
            self.feedback_displayed = False # Set Flag
        if ((self.current_time - self.start_iti_time) >= self.iti_time) and self.feedback_displayed == False: # When ITI is complete
            Clock.unschedule(self.end_iti) # Stop Repeat

            if self.current_trial > self.max_trials: #If current trial is greater than max, stop
                Experiment_App.stop()

            if self.time_elapsed < self.max_time: # If Time is below max, continue
                self.image_presentation()
            elif self.time_elapsed >= self.max_time: # If Time is above or equal to max, stop
                Experiment_App.stop()



    def clock_update(self,*args):
        self.current_time = time.time()
        self.time_elapsed = time.time() - self.start_time

class Experiment_App(App):
    def build(self):
        experiment = Experiment_Staging()
        return experiment

if __name__ == '__main__':
    monitor_x_dim = GetSystemMetrics(0)
    monitor_y_dim = GetSystemMetrics(1)
    Window.size = (monitor_x_dim,monitor_y_dim)
    Window.fullscreen = True
    Experiment_App().run()