#-*- coding: utf-8 - *-
"""
Garden Planner Tracker; main.py
by : jahascow

Module About:
    This file is for processing of plant specific data.
    Need to fix log entry text display upon successful entry as it's text is too long
    for plant log add column for unit type eg each, ounce, pound
    for plant edit form, there is an error that needs fixing, try to adjust the tomato from fruit to vegetable category and it currently fails
    make button to show harvest logs or on splant specific show harvest logs?
    Or make button plant specific that opens form with a current value field that then has a 
        button to hit calculate so you can get the value of the produce? maybe date range?
    8 barrels: math.ceil((((math.pi*28)+4)*8)/12) = 62 feet
"""
# Native
import os
import os.path
import pandas as pd
import subprocess
from datetime import datetime

# 3rd-Party
from tkinter import *
from tkinter import Tk,ttk
from tkcalendar import DateEntry
from functools import partial # used to pass commands to tkinter functions
from PIL import Image, ImageTk
import fpdf

color_pallet_dict = {
    1: '#e6ffe6',
    2: '#ebd9c6',
    3: '#f8f2ec',
    4: [247, 247, 247], # string rgb color for greyish
    5: [255, 255, 255], # string rgb color for white
    6: [42,158,255], # string rgb color for blue
    7: '#71A57B', # in place of green
    8: '#ffffff' # in place of white
}
example_log_entry_dict = {
    # 'Log index', 'Plant index', 'Topic', 'Date', 'Where', 'Quantity', 'Notes'
    'Log index': [''], # create log entry index id
    'Plant index': [''], # the index of the plant referenced for log entry or blank for general log entry
    'Topic': [''], # short entry for grouping topics freeform eg, transplant, direct sow, learning, informational
    'Date': [''], # specify a date for this log entry
    'Where': [''], # way to differentiate where an action for this log entry refers to; eg main garden, wicking tub
    'Quantity': [''], # if tracking of an amount of something done like planting of a tomato you can track how many
    'Notes': [''] # open text for any information you want to log for future refrerence
}
example_plant_entry_dict = {
    'Plant category': ['Examples'],
    'Plant name': ['Broccoli'], # 'Broccoli'
    'Plant variety': ['Waltham 29'], # 'Waltham 29'
    'Germination start': [10], # 0
    'Germination end': [21], # 1
    'Maturity start': [0], # 0
    'Maturity end': [74], # 1
    'Genetics 1': ['Heirloom'], #  'Heirloom','Hybrid', 'Unknown'
    'Genetics 2': ['Annual'], # 'Annual', 'Perennial', 'Unknown
    'Genetics 3': ['Full Sun'], # 'Full Sun'
    'Plant depth min': [0], # .25
    'Plant depth max': [.25], # .5
    'Plant spacing min': [16], # 12
    'Plant spacing max': [16], # 18
    'Number of plants per space': [1], # 1
    'Other notes': [''] # eg determinate or whatever
}
# index of data columns for storageof plant data for item index reference
plant_config_dict = {
    0: 'Plant category', # Vegetables, Fruits
    1: 'Plant name', # 'Broccoli'
    2: 'Plant variety', # 'Waltham 29'
    3: 'Germination start', # 0
    4: 'Germination end', # 1
    5: 'Maturity start', # 0
    6: 'Maturity end', # 1
    7: 'Genetics 1', #  'Heirloom','Hybrid', 'Unknown'
    8: 'Genetics 2', # 'Annual', 'Perennial', 'Unknown
    9: 'Genetics 3', # 'Full Sun'
    10: 'Plant depth min', # .25
    11: 'Plant depth max', # .5
    12: 'Plant spacing min', # 12
    13: 'Plant spacing max', # 18
    14: 'Number of plants per space', # 1
    15: 'Other notes' # eg determinate or whatever
}
class Plants():
    def refresh_plant_object(self) -> None:
        """
        Refreshes the plant DataFrame from the CSV file.

        Reloads the plant data from the CSV file and updates the current plant index.

        Parameters:
            None

        Returns:
            None

        Attributes:
            plant_df_file (str): Path to the plant CSV file.
            plant_df (pd.DataFrame): DataFrame holding the plant data.
            plant_df_cur_index (int): Current maximum index in the plant DataFrame.
        """
        # Setup plant dataframes / file checks
        self.plant_df_file = os.path.join(os.path.dirname(__file__), 'df', str('plants.csv'))
        self.file_check = os.path.isfile(self.plant_df_file)
        
        if not self.file_check:  # File does not exist, create DataFrame with test data
            self.plant_df = pd.DataFrame(example_plant_entry_dict)
            print('No plant entries currently exist.')
            self.plant_df_cur_index = 0
        else:  # File exists, load as a DataFrame
            self.plant_df = pd.read_csv(self.plant_df_file)
            try:
                self.plant_df_cur_index = self.plant_df['Plant index'].max()
            except KeyError:
                print("Error: 'Plant index' column not found in plants.csv")
                self.plant_df_cur_index = 0
    def refresh_log_object(self) -> None:
        """
        Refreshes the log DataFrame from the CSV file.

        Sets up the log dataframes and checks if the log CSV file exists.
        If the file doesn't exist, it creates a new DataFrame with example log entries.
        If the file exists, it loads the data into a DataFrame and updates the current log index.

        Attributes:
            log_df_file (str): Path to the log CSV file.
            log_file_check (bool): Flag indicating if the log CSV file exists.
            log_df (pd.DataFrame): DataFrame holding the log data.
            log_df_cur_index (int): Current maximum index in the log DataFrame.
        """
        # Setup log dataframes / file checks
        self.log_df_file = os.path.join(os.path.dirname(__file__), 'df', str('log.csv'))
        self.log_file_check = os.path.isfile(self.log_df_file)
        if not self.log_file_check:  # File does not exist, create DataFrame with test data
            self.log_df = pd.DataFrame(example_log_entry_dict)
            print('No log entries currently exist.')
            self.log_df_cur_index = 0
        else:  # File exists, load as a DataFrame
            self.log_df = pd.read_csv(self.log_df_file, encoding='utf-8')
            try:
                self.log_df_cur_index = self.log_df['Log index'].max()
            except KeyError:
                print("Error: 'Log index' column not found in log.csv")
                self.log_df_cur_index = 0
    def __init__(self):
        """
        Initialize the Plants object.

        This method is used to initialize the Plants object. It sets up the plant and log dataframes and checks if the files exist.
        If the files do not exist, it creates a new dataframe with test data. If the files exist, it loads the data into a dataframe and updates the current index.
        """
        # Setup plant and log dataframes / file checks
        self.plant_df_file = os.path.join(os.path.dirname(__file__), 'df', str('plants.csv'))
        self.file_check = os.path.isfile(self.plant_df_file)
        self.log_df_file = os.path.join(os.path.dirname(__file__), 'df', str('log.csv'))
        self.log_file_check = os.path.isfile(self.log_df_file)
        # Establish dataframes from csv or example data
        if not self.file_check:  # File does not exist, create dataframe with test data
            self.plant_df = pd.DataFrame(example_plant_entry_dict)
            print('No plants currently defined.')
            self.plant_df_cur_index = 0
        else:  # File exists, load as a dataframe
            self.plant_df = pd.read_csv(self.plant_df_file)
            self.plant_df_cur_index = self.plant_df['Plant index'].max()
        if not self.log_file_check:  # File does not exist, create dataframe with test data
            self.log_df = pd.DataFrame(example_log_entry_dict)
            print('No log entries currently exist.')
            self.log_df_cur_index = 0
        else:  # File exists, load as a dataframe
            self.log_df = pd.read_csv(self.log_df_file, encoding='utf-8') #sep=',', engine='python')
            self.log_df_cur_index = self.log_df['Log index'].max()
    def __str__(self):
        """
        Return a string representation of the object.

        The string representation will be in the form of:
        'Plants Object: Example -> <plant name>'

        :return: A string representation of the object
        """
        try:
            return 'Plants Object: Example -> ' + str(self.plant_df['Plant name'][0])
        except IndexError:
            return 'Plants Object: No plants currently defined.'
    def create_plant_log_pdf(self, plantsummary: str, plantindex: str) -> None:
        """
        Create a PDF file with log entries for the specified plant index.

        This method creates a PDF file with log entries for the specified plant index.
        The PDF will have a header with the plant summary and log entries.
        Each log entry will have the date, topic, where, quantity, and notes.

        :param plantsummary: The summary of the plant to be printed (str)
        :param plantindex: The index of the plant to be printed (str)
        :return: None
        """
        pdf_file = os.path.join(os.path.dirname(__file__), str('plant_log_index.pdf'))
        pdf = fpdf.FPDF()
        pdf.add_page()
        # Set the font
        pdf.set_font("Times", size=14, style="B")
        # Define the table data
        if plantindex != 'all':
            # plant selected created subset
            subset = plants_obj.log_df[plants_obj.log_df['Plant index'] == int(plantindex)]
        else:
            subset = plants_obj.log_df
        data = subset[['Date', 'Topic', 'Where', 'Quantity', 'Notes']]
        # Calculate the effective page width
        epw = pdf.w - 2 * pdf.l_margin
        # Text height is the same as current font size
        th = pdf.font_size
        # Draw the table headers
        pdf.set_fill_color(color_pallet_dict[6][0], color_pallet_dict[6][1], color_pallet_dict[6][2])  # Set the fill color to blue
        pdf.set_text_color(color_pallet_dict[5][0], color_pallet_dict[5][1], color_pallet_dict[5][2])  # Set text color to white
        # Setup scope level variables
        col_width = 0
        col_width2 = 0
        col_width3 = 0
        col_width4 = 0
        col_width5 = 75
        #for row in data.itertuples(): print(str(row))
        
        def get_col_width(key,column):
            # 0Log index,1Plant index,2Topic,3Date,4Where,5Quantity,6Notes
            # data is a subset which does not include Log index or Plant index
            # using itertuples applies an additional index column which we 
            # need to account for by adding 1 
            key+=1        
            # Calculate the column width for the specified column
            width = max(pdf.get_string_width(str(row[key])) for row in data.itertuples()) + 5
            width = max(width,pdf.get_string_width(column)+5) # we need to also account for the heading being max width need and subsequent padding.
            #for row in data.itertuples(): print(str(row))
            col_width = min(width, (epw - col_width5) / 4)  # Ensure the column width doesn't exceed 1/4 of the page width remaining after column 5 width
            return col_width
        for key, row in enumerate(data):
            #print('all: ', key, row)
            if key == 0: # Date
                #col_width = 20  # 27
                col_width = get_col_width(key, row)
                pdf.cell(col_width, th, str(row), border=1, fill=True)
            elif key == 1: # Topic
                #col_width2 = int((epw - 15) / 4) - 10
                col_width2 = get_col_width(key, row)
                pdf.cell(col_width2, th, str(row), border=1, fill=True)
            elif key == 2: # Where
                #col_width3 = int((epw - 15) / 4) - 15
                col_width3 = get_col_width(key, row)
                pdf.cell(col_width3, th, str(row), border=1, fill=True)
            elif key == 3: # Quantity
                #col_width4 = int((epw - 15) / 4) - 22
                col_width4 = get_col_width(key, row)
                pdf.cell(col_width4, th, str(row), border=1, fill=True)
            elif key == 4: # Notes
                pdf.cell(col_width5, th, str(row), border=1, fill=True)
        # Create new line after header
        pdf.ln(th)

        # Iterating over rows to populate table data
        pdf.set_font("Times", size=12)
        th = pdf.font_size
        pdf.set_text_color(0, 0, 0)  # Set text color to black
        for index, row in data.iterrows():
            if plantindex == 'all':
                pdf.set_fill_color(color_pallet_dict[4][0], color_pallet_dict[4][1], color_pallet_dict[4][2])  # Set the fill color to greyish
                # Conditionally selecting a cell value
                plant_name = plants_obj.plant_df.loc[plants_obj.plant_df['Plant index'] == plants_obj.log_df['Plant index'][index]]['Plant name']
                plant_variety = plants_obj.plant_df.loc[plants_obj.plant_df['Plant index'] == plants_obj.log_df['Plant index'][index]]['Plant variety']
                pdf.cell(col_width, th, '', border=0, fill=True)
                pdf.cell(col_width2, th, '', border=0, fill=True)
                pdf.cell(col_width3, th, '', border=0, fill=True)
                pdf.cell(col_width4, th, str(plant_name.values[0]), border=0, fill=True)
                pdf.multi_cell(col_width5 - 5, 6, str('Variety: ')+str(plant_variety.values[0]), border=0, fill=True)
                pdf.set_fill_color(color_pallet_dict[5][0], color_pallet_dict[5][1], color_pallet_dict[5][2])  # Set the fill color to white

            
            else: # need to just alternate row colors for each entry
                if index % 2 != 0:
                    pdf.set_fill_color(color_pallet_dict[4][0], color_pallet_dict[4][1], color_pallet_dict[4][2])  # Set the fill color to greyish
                else:
                    pdf.set_fill_color(color_pallet_dict[5][0], color_pallet_dict[5][1], color_pallet_dict[5][2])  # Set the fill color to white

            pdf.cell(col_width, th, str(row['Date']), border=0, fill=True)
            pdf.cell(col_width2, th, str(row['Topic']), border=0, fill=True)
            pdf.cell(col_width3, th, str(row['Where']), border=0, fill=True)
            pdf.cell(col_width4, th, str(row['Quantity']), border=0, fill=True)
            # pdf.cell(col_width4,th,str(row['Notes']),border=0, fill=True)
            pdf.multi_cell(col_width5 - 5, 6, str(row['Notes']), border=0, fill=True)
            pdf.ln(th)
        pdf.ln(th)
        pdf.set_y(0)
        pdf.cell(0, 10, f'Garden Planner & Tracker by Jahascow: "{plantsummary}" Log Entries', 0, 0, 'C')
        pdf.output(pdf_file, 'F')
        subprocess.Popen([pdf_file], shell=True)
    def create_pdf(self):
        pdf_file = os.path.join(os.path.dirname(__file__), str('plant_index.pdf'))
        pdf = fpdf.FPDF()
        pdf.add_page()        
        # Set the font
        pdf.set_font("Times", size=14, style="B")
        # Define the table data
        data = plants_obj.plant_df[['Plant index','Plant category','Plant name','Plant variety',]]
        # Calculate the effective page width
        epw = pdf.w - 2 * pdf.l_margin
        # Text height is the same as current font size
        th = pdf.font_size
        # Draw the table headers
        pdf.set_fill_color(color_pallet_dict[6][0],color_pallet_dict[6][1],color_pallet_dict[6][2])  # Set the fill color to blue
        pdf.set_text_color(color_pallet_dict[5][0],color_pallet_dict[5][1],color_pallet_dict[5][2])  # Set text color to white
        # Setup scope level variables
        col_width = 0
        col_width2 = 0
        col_width3 = 0
        col_width4 = 0
        for key,row in enumerate(data):
            if key == 0:
                col_width = 27
                pdf.cell(col_width, th, str(row), border=1, fill=True)
            elif key == 1:
                col_width2=int((epw - 27)/3)-20
                pdf.cell(col_width2, th, str(row), border=1, fill=True)
            elif key == 2:
                col_width3=col_width4=int((epw - 27)/3)+10
                pdf.cell(col_width3, th, str(row), border=1, fill=True)                
            else:
                col_width3=col_width4=int((epw - 27)/3)+10
                pdf.cell(col_width4, th, str(row), border=1, fill=True)             
        #Create new line after header
        pdf.ln(th)

        # Iterating over rows to populate table data
        pdf.set_font("Times", size=12)
        th=pdf.font_size
        pdf.set_text_color(0, 0, 0)  # Set text color to 
        for index, row in data.iterrows():
            if index % 2 != 0:
                pdf.set_fill_color(color_pallet_dict[4][0],color_pallet_dict[4][1],color_pallet_dict[4][2])  # Set the fill color to greyish
            else:
                pdf.set_fill_color(color_pallet_dict[5][0],color_pallet_dict[5][1],color_pallet_dict[5][2])  # Set the fill color to white
            
            pdf.cell(col_width,th,str(row['Plant index']),border=0, fill=True)
            pdf.cell(col_width2,th,str(row['Plant category']),border=0, fill=True)
            pdf.cell(col_width3,th,str(row['Plant name']),border=0, fill=True)
            pdf.cell(col_width4,th,str(row['Plant variety']),border=0, fill=True)
            pdf.ln(th)
        pdf.ln(th)
        pdf.set_y(0)
        pdf.cell(0, 10, 'Garden Planner & Tracker by Jahascow', 0, 0, 'C')
        pdf.output(pdf_file, 'F')
        subprocess.Popen([pdf_file],shell=True) 
    def plant_csv_insert(self):
        if self.file_check == True:
            # Append the new data to the existing DataFrame
            self.plant_df = pd.concat([self.plant_df, self.plant_df_new], ignore_index=False)
            # Write the updated DataFrame back to the CSV file
            self.plant_df.to_csv(self.plant_df_file, index=False)
        else:
            self.plant_df_new.to_csv(self.plant_df_file, index=False)
    def log_csv_insert(self):
        if self.log_file_check == True:
            # Append the new data to the existing DataFrame
            self.log_df = pd.concat([self.log_df, self.log_df_new], ignore_index=False)
            # Write the updated DataFrame back to the CSV file
            self.log_df.to_csv(self.log_df_file, index=False)
        else:
            self.log_df_new.to_csv(self.log_df_file, index=False)
    def make_plant_df(self,plant_index,submit_results):
        data_temp = {
            'Plant index': [plant_index],
            'Plant category': [submit_results[0]], # 'Vegetables', 'Flowers'
            'Plant name': [submit_results[1]], # 'Broccoli'
            'Plant variety': [submit_results[2]], # 'Waltham 29'
            'Germination start': [submit_results[3]], # 0
            'Germination end': [submit_results[4]], # 1
            'Maturity start': [submit_results[5]], # 0
            'Maturity end': [submit_results[6]], # 1
            'Genetics 1': [submit_results[7]], #  'Heirloom','Hybrid', 'Unknown'
            'Genetics 2': [submit_results[8]], # 'Annual', 'Perennial', 'Unknown
            'Genetics 3': [submit_results[9]], # 'Full Sun'
            'Plant depth start': [submit_results[10]], # .25
            'Plant depth end': [submit_results[11]], # .5
            'Plant spacing start': [submit_results[12]], # 12
            'Plant spacing end': [submit_results[13]], # 18
            'Number of plants per space': [submit_results[14]], # 1
            'Other notes': [submit_results[15]] # eg determinate
        }
        self.plant_df_new = pd.DataFrame(data_temp)
    def make_log_df(self,submit_results):
        data_temp = {
            # 'Log index', 'Plant index', 'Topic', 'Date', 'Where', 'Quantity', 'Notes'
            'Log index': [submit_results[0]], # create log entry index id
            'Plant index': [submit_results[1]], # ( may be off by one need to verify, the index of the plant referenced for log entry or blank for general log entry
            'Topic': [submit_results[2]], # short entry for grouping topics freeform eg, transplant, direct sow, learning, informational
            'Date': [submit_results[3]], # specify a date for this log entry
            'Where': [submit_results[4]], # way to differentiate where an action for this log entry refers to; eg main garden, wicking tub
            'Quantity': [submit_results[5]], # if tracking of an amount of something done like planting of a tomato you can track how many
            'Notes': [submit_results[6]] # open text for any information you want to log for future refrerence

        }
        self.log_df_new = pd.DataFrame(data_temp)
    def plant_update(self,submit_results):
        # Update record of the existing DataFrame
        data = self.plant_df
        data.loc[data['Plant index'] == int(submit_results[0])] = submit_results
        self.plant_df = data
        # Write the updated DataFrame back to the CSV file
        self.plant_df.to_csv(self.plant_df_file, index=False)
        # refresh plant object
        self.refresh_plant_object()        
    def plant_entry(self,submit_results):
        # now we need to build a dataframe dictionary with these variables 
        #print(self.plant_df_cur_index+1,submit_results)
        self.make_plant_df(self.plant_df_cur_index+1,submit_results)
        # now we need to save / append to existing data & datafile
        self.plant_csv_insert()
        # refresh plant object
        self.refresh_plant_object()
    def log_entry(self,submit_results):
        # now we need to build a dataframe dictionary with these variables 
        #print(submit_results)
        self.make_log_df(submit_results)
        # now we need to save / append to existing data & datafile
        self.log_csv_insert()
        # refresh plant object
        self.refresh_log_object()
        
def menu_select(size,image,image_resize):
    global display_df
    '''Main menu for app'''
    def shutdown_app():
        print("Performing cleanup tasks...")
        root.quit()
        print("Closing application window...")
        root.destroy()
    def clearFrame():
        # destroy all widgets from contentframe1
        for widget in contentframe1.winfo_children():
            widget.destroy()
        contentframe1.pack_forget()
    def log_selected_entry(plant,**kwargs):
        clearFrame()
        form_update_verbose = kwargs.get('success')
        if form_update_verbose == None:
            form_update_verbose = ''
         # Buttoms frame for content frame 
        contentframe1_buttons_frame = Frame(contentframe1, bg=color_pallet_dict[3], width=550, height=100)
        
        '''Configure contentframe1 grid layout'''
        contentframe1.grid(row=0,column=1,padx=0,pady=0)
        contentframe1.grid_columnconfigure(0, weight=0)
        contentframe1.grid_columnconfigure(1, weight=3)
        
        '''Configure contentframe1_buttons_frame layout'''
        contentframe1_buttons_frame.grid(column=0, columnspan=3, row=7, padx=0, pady=0, sticky='ESW')
        for i in range(6):
            contentframe1_buttons_frame.rowconfigure(i, weight=2)
        contentframe1_buttons_frame.rowconfigure(7, weight=1)
        contentframe1_buttons_frame.columnconfigure(1, weight=3)
        
        # add a select option for unit using these options: Each, Ounces, Pounds, Grams, Kilograms, Bunches
        unit_options = ['Each', 'Ounces', 'Pounds', 'Grams', 'Kilograms', 'Bunches']

        
        #print(plant)
        # declaring string variables for storing values of entry form
        # 'Log index', 'Plant index', 'Topic', 'Date', 'Where', 'Quantity', 'Notes'
        log_logindex = plants_obj.log_df_cur_index + 1
        var_log_topic = StringVar(contentframe1)
        var_log_date = StringVar(contentframe1)
        var_log_where = StringVar(contentframe1)
        var_log_quantity = StringVar(contentframe1)
        var_log_unit = StringVar(contentframe1)
        text_log_notes = StringVar(contentframe1)
        
        def populate_defaults():
            #plants_obj.refresh_log_object()
            log_selected_entry(plant,success=f'Successfully logged {plant[2]}.  Enter another for ')
        
        def submit():
            # form variables return values
            log_topic = var_log_topic.get()
            log_date = var_log_date.get_date().strftime('%Y/%m/%d')
            log_where = var_log_where.get()
            if not log_where:
                log_where = 'not specified'
            log_quantity = var_log_quantity.get()
            if not log_quantity:
                log_quantity = 0
            log_notes = text_log_notes.get('1.0',END) # differs from entry
            if not log_notes:
                log_notes = 'none'
            submit_results = [int(log_logindex),plant[0],str(log_topic),str(log_date),str(log_where),\
                int(log_quantity),str(log_notes)]
            plants_obj.log_entry(submit_results)
            populate_defaults()
        
        # Create a DateEntry widget
        var_log_date = DateEntry(contentframe1, width=12, background='darkblue', foreground='white', borderwidth=2)

        '''Create the widgets for the contentframe1'''
        # First all the labels
        label_log_plant_index = Label(contentframe1, text = f'{form_update_verbose}Log for {plant[2]}, variety {plant[3]}, Plant ID #({plant[0]}):', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        # Special settings for text wrapping of success label
        # Set the initial wraplength
        label_log_plant_index.configure(wraplength=contentframe1.winfo_width())   
        # Bind the <Configure> event to update the wraplength
        def update_wrap(event):
            label_log_plant_index.configure(wraplength=event.width)
        contentframe1.bind('<Configure>', update_wrap)
                
        label_log_date = Label(contentframe1, text = 'Select date for entry:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'normal'))
        label_log_topic = Label(contentframe1, text = 'Topic:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'normal'))
        label_log_where = Label(contentframe1, text = 'Location:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'normal'))
        label_log_quantity = Label(contentframe1, text = 'Quantity:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'normal'))
        label_log_unit = Label(contentframe1, text = 'Unit:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'normal'))
        
        label_log_notes = Label(contentframe1, text = 'Notes:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'normal'))
        # Entry labels
        entry_log_topic = Entry(contentframe1,textvariable=var_log_topic, width=65, font=("TkDefaultFont",10,'normal'))
        entry_log_where = Entry(contentframe1,textvariable=var_log_where, width=65, font=("TkDefaultFont",10,'normal'))
        entry_log_quantity = Entry(contentframe1,textvariable=var_log_quantity, width=65, font=("TkDefaultFont",10,'normal'))
        # text labels
        text_log_notes = Text(contentframe1, width=65, height=18, font=("TkDefaultFont",10,'normal'))
        
        '''Create the widgets for the contentframe1_buttons_frame'''  
        # Create a button to create log entry
        btn_submit = Button(contentframe1_buttons_frame,text = 'Create Log Entry', font=("TkDefaultFont",10,'bold'), background=color_pallet_dict[7], fg=color_pallet_dict[8], command = submit)

        '''Layout the widgets in the content1frame'''
        # label widgets
        label_log_plant_index.grid(row=0,column=0, columnspan=2, padx=5, pady=15, sticky='w')
        label_log_date.grid(row=1,column=0, padx=5, pady=15, sticky='e')
        label_log_topic.grid(row=2,column=0, padx=5, pady=5, sticky='ne')
        label_log_where.grid(row=3,column=0, padx=5, pady=5, sticky='ne')
        label_log_quantity.grid(row=4,column=0, padx=5, pady=5, sticky='ne')
        label_log_unit.grid(row=5,column=0, padx=5, pady=5, sticky='ne')
        label_log_notes.grid(row=6,column=0, padx=5, pady=5, sticky='ne')
        # date entry widget
        var_log_date.grid(row=1,column=1, padx=5, pady=15, sticky='w')
        # entry widgets      
        entry_log_topic.grid(row=2,column=1, padx=5, pady=5, sticky='nw')
        entry_log_where.grid(row=3,column=1, padx=5, pady=5, sticky='nw')
        entry_log_quantity.grid(row=4,column=1, padx=5, pady=5, sticky='nw')
        # Option widgets
        var_log_unit.set(unit_options[0])  # default value
        option_log_unit = OptionMenu(contentframe1, var_log_unit, *unit_options)
        option_log_unit.grid(row=5,column=1, padx=5, pady=5, sticky='nw')        
        # text widgets
        text_log_notes.grid(row=6,column=1, padx=5, pady=5, sticky='nw')

        '''Layout the widgets in the content buttons frame'''
        btn_submit.grid(row=7,column=1,columnspan=2,pady=20,sticky='s')
        
        '''Tooltips Configuration'''
        tooltips = {
            'log_topic': "Log topic is a generalization of what action with plant was done:\neg; Direct sow, Transplant, Store bought transplant",
            'log_where': "Where can be any area where this event or plant occured:\neg; Main garden, Wicking bucket, Raised bed",
            'log_quantity': "Track how many plants where affected, or 0 for none"
        }
        tip = ttk.Label(contentframe1, text='', background='light yellow')
        def show_tooltip(event, key):
            tip.config(text=tooltips[key])
            tip.place(anchor='nw', relx=0.215, rely=.11 + .045 * list(tooltips.keys()).index(key))
            tip.lift(aboveThis=None)
        def hide_tooltip(event):
            tip.place_forget()
        
        for key, label in [('log_topic', label_log_topic), ('log_where', label_log_where), ('log_quantity', label_log_quantity)]:
            label.bind("<Enter>", lambda event, key=key: show_tooltip(event, key))
            label.bind("<Leave>", hide_tooltip)
    def view_plant_entry(plant):
        clearFrame()
        # declaring string variables for storing values of entry form
        vars = [StringVar(contentframe1) for _ in range(15)]
        (
            var_plant_category,
            var_plant_name,
            var_plant_variety,
            var_germination_start,
            var_germination_end,
            var_maturity_start,
            var_maturity_end,
            var_genetics_1,
            var_genetics_2,
            var_genetics_3,
            var_plant_depth_min,
            var_plant_depth_max,
            var_plant_spacing_min,
            var_plant_spacing_max,
            var_number_of_plants_per_space,
        ) = vars
        text_other_notes = StringVar(contentframe1)
        def submit():
            # form variables return values
            (
                plant_category,
                plant_name,
                plant_variety,
                germination_start,
                germination_end,
                maturity_start,
                maturity_end,
                genetics_1,
                genetics_2,
                genetics_3,
                plant_depth_min,
                plant_depth_max,
                plant_spacing_min,
                plant_spacing_max,
                number_of_plants_per_space,
            ) = [var.get() for var in vars]
            other_notes = text_other_notes.get('1.0',END) # differs from entry
            if len(other_notes) < 2:
                other_notes = 'none'
            print(plant[0],type(plant_category),type(plant_name),type(plant_variety),\
                type(germination_start),type(germination_end),type(maturity_start),\
                type(maturity_end),type(genetics_1),type(genetics_2),type(genetics_3),\
                type(plant_depth_min),type(plant_depth_max),type(plant_spacing_min),\
                type(plant_spacing_max),type(number_of_plants_per_space),type(other_notes))
            print(plant[0],plant_category,plant_name,plant_variety,germination_start,germination_end,maturity_start,\
                maturity_end,genetics_1,genetics_2,genetics_3,plant_depth_min,plant_depth_max,plant_spacing_min,\
                plant_spacing_max,number_of_plants_per_space,other_notes)
            submit_results = [plant[0],str(plant_category),str(plant_name),str(plant_variety),\
                int(germination_start),int(germination_end),int(maturity_start),\
                int(maturity_end),str(genetics_1),str(genetics_2),str(genetics_3),\
                float(plant_depth_min),float(plant_depth_max),float(plant_spacing_min),\
                float(plant_spacing_max),float(number_of_plants_per_space),str(other_notes)]
            plants_obj.plant_update(submit_results=submit_results)
        def populate_defaults():
            # ways to repopulate form values after submit if desired
            for var, val in zip(vars, plant[1:]):
                #this shortens defining each plant[index# to each variable set in initiatal string var setup of vars]
                var.set(val)
            text_other_notes.insert('1.0', plant[16], END)
        '''Create the widgets for the contentframe1'''
        # First all the labels
        label_plant_category = Label(contentframe1, text = 'Plant category:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_name = Label(contentframe1, text = 'Plant name:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_variety = Label(contentframe1, text = 'Plant variety:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_germination_start = Label(contentframe1, text = 'Germination start:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_germination_end = Label(contentframe1, text = 'Germination end:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_maturity_start = Label(contentframe1, text = 'Maturity start:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_maturity_end = Label(contentframe1, text = 'Maturity end:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_genetics_1 = Label(contentframe1, text = 'Genetics 1:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_genetics_2 = Label(contentframe1, text = 'Genetics 2:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_genetics_3 = Label(contentframe1, text = 'Genetics 3:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_depth_min = Label(contentframe1, text = 'Plant depth min:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_depth_max = Label(contentframe1, text = 'Plant depth max:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_spacing_min = Label(contentframe1, text = 'Plant spacing min:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_spacing_max = Label(contentframe1, text = 'Plant spacing max:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_number_of_plants_per_space = Label(contentframe1, text = 'Number of plants per space:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_other_notes = Label(contentframe1, text = 'Other notes:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        
        # Next all the entry fields
        entry_plant_category = Entry(contentframe1,textvariable=var_plant_category, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_name = Entry(contentframe1,textvariable=var_plant_name, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_variety = Entry(contentframe1,textvariable=var_plant_variety, width=70, font=("TkDefaultFont",10,'normal'))
        entry_germination_start = Entry(contentframe1,textvariable=var_germination_start, width=70, font=("TkDefaultFont",10,'normal'))
        entry_germination_end = Entry(contentframe1,textvariable=var_germination_end, width=70, font=("TkDefaultFont",10,'normal'))
        entry_maturity_start = Entry(contentframe1,textvariable=var_maturity_start, width=70, font=("TkDefaultFont",10,'normal'))
        entry_maturity_end = Entry(contentframe1,textvariable=var_maturity_end, width=70, font=("TkDefaultFont",10,'normal'))
        entry_genetics_1 = Entry(contentframe1,textvariable=var_genetics_1, width=70, font=("TkDefaultFont",10,'normal'))
        entry_genetics_2 = Entry(contentframe1,textvariable=var_genetics_2, width=70, font=("TkDefaultFont",10,'normal'))
        entry_genetics_3 = Entry(contentframe1,textvariable=var_genetics_3, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_depth_min = Entry(contentframe1,textvariable=var_plant_depth_min, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_depth_max = Entry(contentframe1,textvariable=var_plant_depth_max, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_spacing_min = Entry(contentframe1,textvariable=var_plant_spacing_min, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_spacing_max = Entry(contentframe1,textvariable=var_plant_spacing_max, width=70, font=("TkDefaultFont",10,'normal'))
        entry_number_of_plants_per_space = Entry(contentframe1,textvariable=var_number_of_plants_per_space, width=70, font=("TkDefaultFont",10,'normal'))
        text_other_notes = Text(contentframe1, width=70, height=3, font=("TkDefaultFont",10,'normal'))
        
        # Submit Plant Button
        btn_submit = Button(contentframe1,text = f'Update Plant Entry, plant index #{plant[0]}', font=("TkDefaultFont",10,'bold'), background=color_pallet_dict[7], fg=color_pallet_dict[8], command = submit)
        
        '''Layout the widgets in the buttonsframe'''
        contentframe1.grid(row=0,column=1,padx=0,pady=0)
        contentframe1.grid_columnconfigure(0, weight=0)
        contentframe1.grid_columnconfigure(1, weight=3)
        
        '''Layout the widgets in the content1frame'''
        # label widgets
        label_plant_category.grid(row=0,column=0, padx=5, pady=5, sticky='e')
        label_plant_name.grid(row=1,column=0, padx=5, pady=5, sticky='e')
        label_plant_variety.grid(row=2,column=0, padx=5, pady=5, sticky='e')   
        label_germination_start.grid(row=3,column=0, padx=5, pady=5, sticky='e') 
        label_germination_end.grid(row=4,column=0, padx=5, pady=5, sticky='e') 
        label_maturity_start.grid(row=5,column=0, padx=5, pady=5, sticky='e') 
        label_maturity_end.grid(row=6,column=0, padx=5, pady=5, sticky='e') 
        label_genetics_1.grid(row=7,column=0, padx=5, pady=5, sticky='e') 
        label_genetics_2.grid(row=8,column=0, padx=5, pady=5, sticky='e') 
        label_genetics_3.grid(row=9,column=0, padx=5, pady=5, sticky='e') 
        label_plant_depth_min.grid(row=10,column=0, padx=5, pady=5, sticky='e') 
        label_plant_depth_max.grid(row=11,column=0, padx=5, pady=5, sticky='e') 
        label_plant_spacing_min.grid(row=12,column=0, padx=5, pady=5, sticky='e') 
        label_plant_spacing_max.grid(row=13,column=0, padx=5, pady=5, sticky='e') 
        label_number_of_plants_per_space.grid(row=14,column=0, padx=5, pady=5, sticky='e') 
        label_other_notes.grid(row=15,column=0, padx=5, pady=5, sticky='ne') 
        # entry widgets      
        entry_plant_category.grid(row=0,column=1, padx=5, pady=5)
        entry_plant_name.grid(row=1,column=1, padx=5, pady=5)
        entry_plant_variety.grid(row=2,column=1, padx=5, pady=5)
        entry_germination_start.grid(row=3,column=1, padx=5, pady=5)
        entry_germination_end.grid(row=4,column=1, padx=5, pady=5)
        entry_maturity_start.grid(row=5,column=1, padx=5, pady=5)
        entry_maturity_end.grid(row=6,column=1, padx=5, pady=5)
        entry_genetics_1.grid(row=7,column=1, padx=5, pady=5)
        entry_genetics_2.grid(row=8,column=1, padx=5, pady=5)
        entry_genetics_3.grid(row=9,column=1, padx=5, pady=5)
        entry_plant_depth_min.grid(row=10,column=1, padx=5, pady=5)
        entry_plant_depth_max.grid(row=11,column=1, padx=5, pady=5)
        entry_plant_spacing_min.grid(row=12,column=1, padx=5, pady=5)
        entry_plant_spacing_max.grid(row=13,column=1, padx=5, pady=5)
        entry_number_of_plants_per_space.grid(row=14,column=1, padx=5, pady=5)
        text_other_notes.grid(row=15,column=1, padx=5, pady=5)
        
        '''Tooltips Configuration'''
        # Each tip seems to require its own functions and variables as
        # I do not know a way to handle a function inside a window that
        # must be passed as an object for the purpose of tkinter.
        
        # tooltip labels
        tip_plant_category = ttk.Label(contentframe1, text="Enter plant category:\neg; Vegetables, Fruits", background='light yellow')
        tip_plant_name = ttk.Label(contentframe1, text="Enter plant name:\neg; Broccoli, Carrot, Marigold", background='light yellow')
        tip_plant_variety = ttk.Label(contentframe1, text="Enter plant variety:\neg; Waltham 29, Baxter Bush", background='light yellow')
        tip_plant_depth_min = ttk.Label(contentframe1, text="Unit in inches floating decimal", background='light yellow')
        tip_plant_depth_max = ttk.Label(contentframe1, text="Unit in inches floating decimal", background='light yellow')
        tip_plant_spacing_min = ttk.Label(contentframe1, text="Unit in inches floating decimal", background='light yellow')
        tip_plant_spacing_max = ttk.Label(contentframe1, text="Unit in inches floating decimal", background='light yellow')

        # tooltip show functions     
        def show_tooltip_plant_category(event): 
            tip_plant_category.place(anchor='nw', relx=0.2, rely=0.0)
            tip_plant_category.lift(aboveThis=None)
        def show_tooltip_plant_name(event): 
            tip_plant_name.place(anchor='nw', relx=0.2, rely=0.03)#, width=400, height=200)#(x=root.winfo_pointerx(), y=root.winfo_pointery()) # need relative numbers though not exact returns
            tip_plant_name.lift(aboveThis=None)            
        def show_tooltip_plant_variety(event): 
            tip_plant_variety.place(anchor='nw', relx=0.2, rely=0.06)
            tip_plant_variety.lift(aboveThis=None)
        def show_tooltip_plant_depth_min(event): 
            tip_plant_depth_min.place(anchor='nw', relx=0.2, rely=0.30)
            tip_plant_depth_min.lift(aboveThis=None)
        def show_tooltip_plant_depth_max(event): 
            tip_plant_depth_max.place(anchor='nw', relx=0.2, rely=0.33)
            tip_plant_depth_max.lift(aboveThis=None)
        def show_tooltip_plant_spacing_min(event): 
            tip_plant_spacing_min.place(anchor='nw', relx=0.2, rely=0.36)
            tip_plant_spacing_min.lift(aboveThis=None)
        def show_tooltip_plant_spacing_max(event): 
            tip_plant_spacing_max.place(anchor='nw', relx=0.2, rely=0.39)
            tip_plant_spacing_max.lift(aboveThis=None)
                        
        # tooltip hide functions
        def hide_tooltip_plant_category(event): 
            tip_plant_category.place_forget()
        def hide_tooltip_plant_name(event): 
            tip_plant_name.place_forget()
        def hide_tooltip_plant_variety(event): 
            tip_plant_variety.place_forget()
        def hide_tooltip_plant_depth_min(event): 
            tip_plant_depth_min.place_forget()
        def hide_tooltip_plant_depth_max(event): 
            tip_plant_depth_max.place_forget()
        def hide_tooltip_plant_spacing_min(event): 
            tip_plant_spacing_min.place_forget()
        def hide_tooltip_plant_spacing_max(event): 
            tip_plant_spacing_max.place_forget()

        # tooltip <Enter> label bindings
        label_plant_name.bind("<Enter>", show_tooltip_plant_name)
        label_plant_category.bind("<Enter>", show_tooltip_plant_category)
        label_plant_variety.bind("<Enter>", show_tooltip_plant_variety)
        label_plant_depth_min.bind("<Enter>", show_tooltip_plant_depth_min)
        label_plant_depth_max.bind("<Enter>", show_tooltip_plant_depth_max)
        label_plant_spacing_min.bind("<Enter>", show_tooltip_plant_spacing_min)
        label_plant_spacing_max.bind("<Enter>", show_tooltip_plant_spacing_max)

        # tooltip <Leave> label bindings
        label_plant_name.bind("<Leave>", hide_tooltip_plant_name)
        label_plant_category.bind("<Leave>", hide_tooltip_plant_category)
        label_plant_variety.bind("<Leave>", hide_tooltip_plant_variety)        
        label_plant_depth_min.bind("<Leave>", hide_tooltip_plant_depth_min)
        label_plant_depth_max.bind("<Leave>", hide_tooltip_plant_depth_max)
        label_plant_spacing_min.bind("<Leave>", hide_tooltip_plant_spacing_min)
        label_plant_spacing_max.bind("<Leave>", hide_tooltip_plant_spacing_max)
        
        '''Form Submission'''
        btn_submit.grid(row=16,column=0,columnspan=2,pady=20,sticky='s')
        
        populate_defaults()
    def show_plants():
        clearFrame() # clear out contentframe1 contents
        def view_selected():
            # Get the currently selected item
            selected_item = trv.selection()
            if selected_item:
                # Get the values of the selected item
                view_plant_entry(trv.item(selected_item, 'values'))
            else:
                print("No row selected")
        def log_selected():
            # Get the currently selected item
            selected_item = trv.selection()
            if selected_item:
                # Get the values of the selected item
                log_selected_entry(trv.item(selected_item, 'values'))
            else:
                print("No row selected")
        def pdf_log_selected():
            # Get the currently selected item
            selected_item = trv.selection()
            if selected_item:
                # Get the values of the selected item
                plants_obj.create_plant_log_pdf(trv.item(selected_item, 'values')[2]+', '+trv.item(selected_item, 'values')[3],trv.item(selected_item, 'values')[0])
            else:
                print("No row selected, showing all logs")
                plants_obj.create_plant_log_pdf('All Plants','all')
        display_df = plants_obj.plant_df.sort_values(by=['Plant category', 'Plant name', 'Plant variety', 'Plant index'], ascending=[True, True, True, True])#.drop(columns=['Plant category', 'Genetics 1'])
        #display_df = display_df.sort_values(by=['Plant index ', 'Plant variety'], ascending=[True, False])

        # Buttoms frame for content frame 
        contentframe1_buttons_frame = Frame(contentframe1, bg=color_pallet_dict[3], width=550, height=100)
        # Content Frame
        '''Create the widgets for the contentframe1'''
        # Create a Treeview widget
        column_list = [r for r in display_df]
        trv = ttk.Treeview(contentframe1, selectmode='browse', columns=column_list, show='headings',height=18)
        # Add Some Style
        style = ttk.Style() 
        # Change Selected Color
        style.map('Treeview', background=[('selected', color_pallet_dict[7])]) 
        # Configure the Treeview Colors
        style.configure("Treeview",
            background=color_pallet_dict[1],
            foreground="black",
            rowheight=25,
            fieldbackground=color_pallet_dict[1])
        btn_select_record = Button(contentframe1_buttons_frame, text="View Plant Detail", font=("TkDefaultFont",10,'bold'), background=color_pallet_dict[7], fg=color_pallet_dict[8], command=view_selected)
        btn_log_selected = Button(contentframe1_buttons_frame, text="Plant Log Entry", font=("TkDefaultFont",10,'bold'), background=color_pallet_dict[7], fg=color_pallet_dict[8], command=log_selected)
        btn_create_plant_log_pdf = Button(contentframe1_buttons_frame, text="Display Plants Log", font=("TkDefaultFont",10,'bold'), background=color_pallet_dict[7], fg=color_pallet_dict[8], command=pdf_log_selected)

        '''Layout the widgets in the content frame'''
        contentframe1_buttons_frame.grid(column=1, columnspan=3, row=3, padx=0, pady=0, sticky='ESW')
        contentframe1_buttons_frame.rowconfigure(1,weight=1)
        contentframe1_buttons_frame.columnconfigure(1,weight=3)
        trv.grid(row=1,column=1,padx=20,pady=20)
        # Vertical scrollbar widget layout
        vs = ttk.Scrollbar(contentframe1,orient='vertical',command=trv.yview)
        trv.configure(yscrollcommand=vs.set)
        vs.grid(row=1, column=2, sticky='NS')
        # Horizantal scrollbar widgetlayout
        hs = ttk.Scrollbar(contentframe1,orient='horizontal',command=trv.xview)
        trv.configure(xscrollcommand=hs.set)
        hs.grid(row=2, column=1, sticky='ew')
        df_colsizes = [75,100,150,150,100,100,100,100,100,100,100,140,140,140,140,175,250]
        col_alignment = ['c','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w']
        i = 0
        for col in column_list:
            #print(df_colsizes[i],col)
            trv.column(col, anchor=col_alignment[i], width=df_colsizes[i], minwidth=df_colsizes[i], stretch=NO)
            trv.heading(col, text=col)
            i+=1

        df_len = len(tuple(display_df.columns))
        df_list = []
        # Create Striped Row Tags
        trv.tag_configure('oddrow', background="#ebfeeb")
        trv.tag_configure('evenrow', background="#f3fff3")

        for row in display_df.iterrows():
            for i in range(df_len):
                df_list.append(row[1].values[i])
            if row[0] % 2 == 0:
                trv.insert("", END, iid=row[0], text=row[1], values=df_list, tags=('evenrow',))
            else:
                trv.insert("", END, iid=row[0], text=row[1], values=df_list, tags=('oddrow',))
            df_list = []
        btn_select_record.grid(row=3, column=0, padx=20, pady=20, sticky='se')
        btn_log_selected.grid(row=3, column=1, padx=20, pady=20, sticky='s')
        btn_create_plant_log_pdf.grid(row=3, column=2, padx=20, pady=20, sticky='s')
        if plants_obj.log_file_check == False:
            btn_create_plant_log_pdf.config(state='disabled')
    def add_plant():
        clearFrame() # clear out contentframe1 contents
        # declaring string variables for storing values of entry form
        var_plant_category = StringVar(contentframe1)
        var_plant_name = StringVar(contentframe1)
        var_plant_variety = StringVar(contentframe1)
        var_germination_start = StringVar(contentframe1)
        var_germination_end = StringVar(contentframe1)
        var_maturity_start = StringVar(contentframe1)
        var_maturity_end = StringVar(contentframe1)
        var_genetics_1 = StringVar(contentframe1)
        var_genetics_2 = StringVar(contentframe1)
        var_genetics_3 = StringVar(contentframe1)
        var_plant_depth_min = StringVar(contentframe1)
        var_plant_depth_max = StringVar(contentframe1)
        var_plant_spacing_min = StringVar(contentframe1)
        var_plant_spacing_max = StringVar(contentframe1)
        var_number_of_plants_per_space = StringVar(contentframe1)
        text_other_notes = StringVar(contentframe1)
        def submit():
            # form variables return values
            plant_category = var_plant_category.get()
            plant_name = var_plant_name.get()
            plant_variety = var_plant_variety.get()
            germination_start = var_germination_start.get()
            germination_end = var_germination_end.get()
            maturity_start = var_maturity_start.get()
            maturity_end = var_maturity_end.get()
            genetics_1 = var_genetics_1.get()
            genetics_2 = var_genetics_2.get()
            genetics_3 = var_genetics_3.get()
            plant_depth_min = var_plant_depth_min.get()
            plant_depth_max = var_plant_depth_max.get()
            plant_spacing_min = var_plant_spacing_min.get()
            plant_spacing_max = var_plant_spacing_max.get()
            number_of_plants_per_space = var_number_of_plants_per_space.get()
            other_notes = text_other_notes.get('1.0',END) # differs from entry
            if len(other_notes) < 2:
                other_notes = 'none'
            submit_results = [str(plant_category),str(plant_name),str(plant_variety),\
                int(germination_start),int(germination_end),int(maturity_start),\
                int(maturity_end),str(genetics_1),str(genetics_2),str(genetics_3),\
                float(plant_depth_min),float(plant_depth_max),float(plant_spacing_min),\
                float(plant_spacing_max),int(number_of_plants_per_space),str(other_notes)]
            plants_obj.plant_entry(submit_results=submit_results)
            # use below to populate default values for the form vs past results
            populate_defaults()
        def populate_defaults():
            # ways to repopulate form values after submit if desired
            #var_plant_category.set("jenga")
            #var_plant_name.set("")
            #var_plant_variety.set(plant_variety)
            var_plant_category.set('Vegetables')
            var_plant_name.set('')
            var_plant_variety.set('')
            var_germination_start.set('0')
            var_germination_end.set('')
            var_maturity_start.set('0')
            var_maturity_end.set('')
            var_genetics_1.set('Heirloom')
            var_genetics_2.set('Annual')
            var_genetics_3.set('Full Sun')
            var_plant_depth_min.set('.25')
            var_plant_depth_max.set('.50')
            var_plant_spacing_min.set('')
            var_plant_spacing_max.set('')
            var_number_of_plants_per_space.set('1')
            text_other_notes.delete('1.0', END)
        '''Create the widgets for the contentframe1'''
        # First all the labels
        label_plant_category = Label(contentframe1, text = 'Plant category:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_name = Label(contentframe1, text = 'Plant name:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_variety = Label(contentframe1, text = 'Plant variety:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_germination_start = Label(contentframe1, text = 'Germination start:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_germination_end = Label(contentframe1, text = 'Germination end:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_maturity_start = Label(contentframe1, text = 'Maturity start:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_maturity_end = Label(contentframe1, text = 'Maturity end:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_genetics_1 = Label(contentframe1, text = 'Genetics 1:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_genetics_2 = Label(contentframe1, text = 'Genetics 2:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_genetics_3 = Label(contentframe1, text = 'Genetics 3:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_depth_min = Label(contentframe1, text = 'Plant depth min:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_depth_max = Label(contentframe1, text = 'Plant depth max:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_spacing_min = Label(contentframe1, text = 'Plant spacing min:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_plant_spacing_max = Label(contentframe1, text = 'Plant spacing max:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_number_of_plants_per_space = Label(contentframe1, text = 'Number of plants per space:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        label_other_notes = Label(contentframe1, text = 'Other notes:', background=color_pallet_dict[3], font=("TkDefaultFont",10,'bold'))
        
        # Next all the entry fields
        entry_plant_category = Entry(contentframe1,textvariable=var_plant_category, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_name = Entry(contentframe1,textvariable=var_plant_name, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_variety = Entry(contentframe1,textvariable=var_plant_variety, width=70, font=("TkDefaultFont",10,'normal'))
        entry_germination_start = Entry(contentframe1,textvariable=var_germination_start, width=70, font=("TkDefaultFont",10,'normal'))
        entry_germination_end = Entry(contentframe1,textvariable=var_germination_end, width=70, font=("TkDefaultFont",10,'normal'))
        entry_maturity_start = Entry(contentframe1,textvariable=var_maturity_start, width=70, font=("TkDefaultFont",10,'normal'))
        entry_maturity_end = Entry(contentframe1,textvariable=var_maturity_end, width=70, font=("TkDefaultFont",10,'normal'))
        entry_genetics_1 = Entry(contentframe1,textvariable=var_genetics_1, width=70, font=("TkDefaultFont",10,'normal'))
        entry_genetics_2 = Entry(contentframe1,textvariable=var_genetics_2, width=70, font=("TkDefaultFont",10,'normal'))
        entry_genetics_3 = Entry(contentframe1,textvariable=var_genetics_3, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_depth_min = Entry(contentframe1,textvariable=var_plant_depth_min, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_depth_max = Entry(contentframe1,textvariable=var_plant_depth_max, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_spacing_min = Entry(contentframe1,textvariable=var_plant_spacing_min, width=70, font=("TkDefaultFont",10,'normal'))
        entry_plant_spacing_max = Entry(contentframe1,textvariable=var_plant_spacing_max, width=70, font=("TkDefaultFont",10,'normal'))
        entry_number_of_plants_per_space = Entry(contentframe1,textvariable=var_number_of_plants_per_space, width=70, font=("TkDefaultFont",10,'normal'))
        text_other_notes = Text(contentframe1, width=70, height=3, font=("TkDefaultFont",10,'normal'))
        
        # Submit Plant Button
        btn_submit = Button(contentframe1,text = 'Submit Plant Entry', font=("TkDefaultFont",10,'bold'), background=color_pallet_dict[7], fg=color_pallet_dict[8], command = submit)
        
        '''Configure contentframe1 grid layout'''
        contentframe1.grid(row=0,column=1,padx=0,pady=0)
        contentframe1.grid_columnconfigure(0, weight=0)
        contentframe1.grid_columnconfigure(1, weight=3)
        
        '''Layout the widgets in the content1frame'''
        # label widgets
        label_plant_category.grid(row=0,column=0, padx=5, pady=5, sticky='e')
        label_plant_name.grid(row=1,column=0, padx=5, pady=5, sticky='e')
        label_plant_variety.grid(row=2,column=0, padx=5, pady=5, sticky='e')   
        label_germination_start.grid(row=3,column=0, padx=5, pady=5, sticky='e') 
        label_germination_end.grid(row=4,column=0, padx=5, pady=5, sticky='e') 
        label_maturity_start.grid(row=5,column=0, padx=5, pady=5, sticky='e') 
        label_maturity_end.grid(row=6,column=0, padx=5, pady=5, sticky='e') 
        label_genetics_1.grid(row=7,column=0, padx=5, pady=5, sticky='e') 
        label_genetics_2.grid(row=8,column=0, padx=5, pady=5, sticky='e') 
        label_genetics_3.grid(row=9,column=0, padx=5, pady=5, sticky='e') 
        label_plant_depth_min.grid(row=10,column=0, padx=5, pady=5, sticky='e') 
        label_plant_depth_max.grid(row=11,column=0, padx=5, pady=5, sticky='e') 
        label_plant_spacing_min.grid(row=12,column=0, padx=5, pady=5, sticky='e') 
        label_plant_spacing_max.grid(row=13,column=0, padx=5, pady=5, sticky='e') 
        label_number_of_plants_per_space.grid(row=14,column=0, padx=5, pady=5, sticky='e') 
        label_other_notes.grid(row=15,column=0, padx=5, pady=5, sticky='ne') 
        # entry widgets      
        entry_plant_category.grid(row=0,column=1, padx=5, pady=5)
        entry_plant_name.grid(row=1,column=1, padx=5, pady=5)
        entry_plant_variety.grid(row=2,column=1, padx=5, pady=5)
        entry_germination_start.grid(row=3,column=1, padx=5, pady=5)
        entry_germination_end.grid(row=4,column=1, padx=5, pady=5)
        entry_maturity_start.grid(row=5,column=1, padx=5, pady=5)
        entry_maturity_end.grid(row=6,column=1, padx=5, pady=5)
        entry_genetics_1.grid(row=7,column=1, padx=5, pady=5)
        entry_genetics_2.grid(row=8,column=1, padx=5, pady=5)
        entry_genetics_3.grid(row=9,column=1, padx=5, pady=5)
        entry_plant_depth_min.grid(row=10,column=1, padx=5, pady=5)
        entry_plant_depth_max.grid(row=11,column=1, padx=5, pady=5)
        entry_plant_spacing_min.grid(row=12,column=1, padx=5, pady=5)
        entry_plant_spacing_max.grid(row=13,column=1, padx=5, pady=5)
        entry_number_of_plants_per_space.grid(row=14,column=1, padx=5, pady=5)
        text_other_notes.grid(row=15,column=1, padx=5, pady=5)
        
        '''Tooltips Configuration'''
        # Each tip seems to require its own functions and variables as
        # I do not know a way to handle a function inside a window that
        # must be passed as an object for the purpose of tkinter.
        
        # tooltip labels
        tip_plant_category = ttk.Label(contentframe1, text="Enter plant category:\neg; Vegetables, Fruits", background='light yellow')
        tip_plant_name = ttk.Label(contentframe1, text="Enter plant name:\neg; Broccoli, Carrot, Marigold", background='light yellow')
        tip_plant_variety = ttk.Label(contentframe1, text="Enter plant variety:\neg; Waltham 29, Baxter Bush", background='light yellow')
        tip_plant_depth_min = ttk.Label(contentframe1, text="Unit in inches floating decimal", background='light yellow')
        tip_plant_depth_max = ttk.Label(contentframe1, text="Unit in inches floating decimal", background='light yellow')
        tip_plant_spacing_min = ttk.Label(contentframe1, text="Unit in inches floating decimal", background='light yellow')
        tip_plant_spacing_max = ttk.Label(contentframe1, text="Unit in inches floating decimal", background='light yellow')

        # tooltip show functions     
        def show_tooltip_plant_category(event): 
            tip_plant_category.place(anchor='nw', relx=0.2, rely=0.0)
            tip_plant_category.lift(aboveThis=None)
        def show_tooltip_plant_name(event): 
            tip_plant_name.place(anchor='nw', relx=0.2, rely=0.03)#, width=400, height=200)#(x=root.winfo_pointerx(), y=root.winfo_pointery()) # need relative numbers though not exact returns
            tip_plant_name.lift(aboveThis=None)            
        def show_tooltip_plant_variety(event): 
            tip_plant_variety.place(anchor='nw', relx=0.2, rely=0.06)
            tip_plant_variety.lift(aboveThis=None)
        def show_tooltip_plant_depth_min(event): 
            tip_plant_depth_min.place(anchor='nw', relx=0.2, rely=0.30)
            tip_plant_depth_min.lift(aboveThis=None)
        def show_tooltip_plant_depth_max(event): 
            tip_plant_depth_max.place(anchor='nw', relx=0.2, rely=0.33)
            tip_plant_depth_max.lift(aboveThis=None)
        def show_tooltip_plant_spacing_min(event): 
            tip_plant_spacing_min.place(anchor='nw', relx=0.2, rely=0.36)
            tip_plant_spacing_min.lift(aboveThis=None)
        def show_tooltip_plant_spacing_max(event): 
            tip_plant_spacing_max.place(anchor='nw', relx=0.2, rely=0.39)
            tip_plant_spacing_max.lift(aboveThis=None)
                        
        # tooltip hide functions
        def hide_tooltip_plant_category(event): 
            tip_plant_category.place_forget()
        def hide_tooltip_plant_name(event): 
            tip_plant_name.place_forget()
        def hide_tooltip_plant_variety(event): 
            tip_plant_variety.place_forget()
        def hide_tooltip_plant_depth_min(event): 
            tip_plant_depth_min.place_forget()
        def hide_tooltip_plant_depth_max(event): 
            tip_plant_depth_max.place_forget()
        def hide_tooltip_plant_spacing_min(event): 
            tip_plant_spacing_min.place_forget()
        def hide_tooltip_plant_spacing_max(event): 
            tip_plant_spacing_max.place_forget()

        # tooltip <Enter> label bindings
        label_plant_name.bind("<Enter>", show_tooltip_plant_name)
        label_plant_category.bind("<Enter>", show_tooltip_plant_category)
        label_plant_variety.bind("<Enter>", show_tooltip_plant_variety)
        label_plant_depth_min.bind("<Enter>", show_tooltip_plant_depth_min)
        label_plant_depth_max.bind("<Enter>", show_tooltip_plant_depth_max)
        label_plant_spacing_min.bind("<Enter>", show_tooltip_plant_spacing_min)
        label_plant_spacing_max.bind("<Enter>", show_tooltip_plant_spacing_max)

        # tooltip <Leave> label bindings
        label_plant_name.bind("<Leave>", hide_tooltip_plant_name)
        label_plant_category.bind("<Leave>", hide_tooltip_plant_category)
        label_plant_variety.bind("<Leave>", hide_tooltip_plant_variety)        
        label_plant_depth_min.bind("<Leave>", hide_tooltip_plant_depth_min)
        label_plant_depth_max.bind("<Leave>", hide_tooltip_plant_depth_max)
        label_plant_spacing_min.bind("<Leave>", hide_tooltip_plant_spacing_min)
        label_plant_spacing_max.bind("<Leave>", hide_tooltip_plant_spacing_max)
        
        '''Form Submission'''
        btn_submit.grid(row=16,column=0,columnspan=2,pady=20,sticky='s')
        
        populate_defaults()
    # Create the default window 
    root = Tk() 
    root.title('Garden Planner & Tracker:: Main Menu: by jahascow') 
    root.geometry(size)
    root.configure(background=color_pallet_dict[1])

    '''Create all of the main containers'''
    buttonsframe= Frame(root, bg=color_pallet_dict[2], width=145, height=600)
    contentframe1 = Frame(root, bg=color_pallet_dict[3], width=550, height=600)#)

    '''Layout all of the main containers'''
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=3)
    buttonsframe.grid(column=0, row=0, sticky='NESW')
    buttonsframe.columnconfigure(0, weight=2)
    contentframe1.grid(column=1, row=0, rowspan=4, padx=0, pady=0, sticky='NESW')
    contentframe1.columnconfigure(1,weight=3)
   
    '''Create the widgets for the buttonsframe'''
    #Image widget
    image = Image.open(image)
    resized_image = image.resize(image_resize)
    img = ImageTk.PhotoImage(resized_image) # Convert the resized image for Tkinter
    image_label = Label(buttonsframe, image=img, background=color_pallet_dict[2]) # Create a label and assign image
    image_label.image = img  # Keep a reference to avoid garbage collection
    # Show plants widget
    showplants_button = Button(buttonsframe, text='Show Plants', font=("TkDefaultFont",10,'bold'), 
                               bg=color_pallet_dict[7], fg=color_pallet_dict[8], command=show_plants) #,anchor='w', justify='left',  
    # Add plant widget 
    addplant_button = Button(buttonsframe, text='Add Plant', font=("TkDefaultFont",10,'bold'),
                           bg=color_pallet_dict[7], fg=color_pallet_dict[8], command=add_plant) #,anchor='w', justify='left',
    # Plant pdf widget
    btn_create_plant_pdf = Button(buttonsframe, text="Plants Index Card", font=("TkDefaultFont",10,'bold'), background=color_pallet_dict[7], fg=color_pallet_dict[8], command=plants_obj.create_pdf) 

    # Plant Log widget
    btn_create_plant_log = Button(buttonsframe, text="All Plant Logs", font=("TkDefaultFont",10,'bold'), background=color_pallet_dict[7], fg=color_pallet_dict[8], command=partial(plants_obj.create_plant_log_pdf,'All Plants','all'))

    # Exit widget
    exit_button = Button(buttonsframe, text="Exit", font=("TkDefaultFont",10,'bold'), bg=color_pallet_dict[7], fg=color_pallet_dict[8], command=shutdown_app)    
    
    '''Layout the widgets in the buttonsframe'''
    image_label.grid(row=0, column=0)
    showplants_button.grid(row=1, column=0, padx=15, pady=15, sticky='ew') 
    addplant_button.grid(row=2, column=0, padx=15, sticky='ew') 
    btn_create_plant_pdf.grid(row=3, column=0, padx=15, pady=15, sticky='ew')
    btn_create_plant_log.grid(row=4, column=0, padx=15, sticky='ew')
    exit_button.grid(row=5, column=0, sticky='s', pady=290)
    
    if plants_obj.file_check == False:
        # The below buttons are disabled for a clean install
        showplants_button.config(state='disabled')
        btn_create_plant_pdf.config(state='disabled')
        btn_create_plant_log.config(state='disabled')
    elif plants_obj.log_file_check == False:
        btn_create_plant_log.config(state='disabled')
        root.after_idle(show_plants) #start with show plants function being displayed                
    else:
        root.after_idle(show_plants) #start with show plants function being displayed
    root.mainloop() 

if __name__ == '__main__':
    plants_obj = Plants()
    menu_select('800x600',os.path.join(os.path.dirname(__file__), 
                'assets', str('plants_bg.png')),(143,75))