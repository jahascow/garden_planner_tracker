#-*- coding: utf-8 - *-
"""
plants.py
by : jahascow

Module About:
    This file is for processing of plant specific data.
    next to add is data entry form for logs with option selector for plant (optional?)
    QC : Test entry of multiple, while moving from index 9 it repeated 9.  this
        happened after entering in same session, possible reload of object or refresh
        of object index is necessary upon csv update.
"""
# Native
import os
import os.path
import pandas as pd

# 3rd-Party
from tkinter import *
from tkinter import ttk,PhotoImage
#import pillow as PIL
from PIL import Image, ImageTk

# Proprietary
import j_lib
import j_lib.j_lib_user_input_handling



def log_entry(title,category_options,name_options,variety_options,size,image,image_resize):
    def log_entry_category_selected(selected):
        print(selected)
        return None
    def shutdown_app():
        print("Performing cleanup tasks...")
        root.quit()
        print("Closing application window...")
        root.destroy()
    # Create the default window 
    root = Tk() 
    root.title(title) 
    root.geometry(size) 
    root.configure(background='light green')
    # set ttk theme to "clam" which support the fieldbackground option
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview", background="light grey", 
            fieldbackground="light green", foreground="black")

    # Read the Image
    image = Image.open(image)
    resized_image = image.resize(image_resize)
    # Convert the resized image for Tkinter
    img = ImageTk.PhotoImage(resized_image)

    # Create a label and assign image
    label2 = Label(image=img)
    label2.image = img  # Keep a reference to avoid garbage collection
    label2.grid(row=0,columnspan=3)
    def get_value_inside():
        selected_category = category_value.get()
        selected_name = name_value.get()
        selected_variety = variety_value.get()
        #menu_option_selected(selected)  
    # Variable to keep track of the option 
    # selected in OptionMenu 
    category_value = StringVar(root) 
    name_value = StringVar(root) 
    variety_value = StringVar(root) 
    # Set the default value of the variable 
    category_value.set("Select Category") 
    category_menu = OptionMenu(root, category_value, *category_options) 
    category_menu.grid(row=4, column=1, pady=15, sticky='e') 
    name_value.set("Select Name") 
    name_menu = OptionMenu(root, name_value, *name_options) 
    name_menu.grid(row=5, column=1, pady=15, sticky='e') 
    variety_value.set("Select Variety") 
    variety_menu = OptionMenu(root, variety_value, *variety_options) 
    variety_menu.grid(row=6, column=1, pady=15, sticky='e') 
    
    # Submit button for selected option
    submit_button = Button(root, text='Run Selected',
                           command=get_value_inside) #,anchor='w', justify='left',
    submit_button.grid(row=7, column=2, pady=15, padx=10, sticky='w') 
    
    
    # Button for closing
    Button(root, text="Exit", bg='green', fg='white', command=shutdown_app).grid(row=8, columnspan=3, pady=25)
    root.mainloop() 

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

def plants_display():
    def shutdown_app():
        print("Performing cleanup tasks...")
        root.quit()
        print("Closing application window...")
        root.destroy()
    # Creating the tkinter Window
    root = Tk()
    root.configure(background='light green')
    root.title('Garden Planner & Tracker\nPlants: by jahascow')
    #root.geometry("800x600")
    # set ttk theme to "clam" which support the fieldbackground option
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview", background="light grey", 
            fieldbackground="light green", foreground="black")
    
    display_df = plants_obj.plant_df.drop(columns=['Plant category', 'Genetics 1'])
    # Create a Treeview widget
    tree = ttk.Treeview(root, columns=list(display_df.columns), show='headings')
    for col in display_df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)  # Adjust column width as needed

    # Insert DataFrame rows into the Treeview
    for index, row in display_df.iterrows():
        tree.insert('', END, values=list(row))

    tree.pack()

    # Button for closing
    exit_button = Button(root, text="Exit", bg='green', fg='white', command=shutdown_app)
    exit_button.pack(pady=20)

    root.mainloop()

class Plants():
    # s_names = sniper_assist, 
    def __init__(self):
        self.plant_df_file = os.path.join(os.path.dirname(__file__), 'df', str('plants.csv'))
        self.file_check = os.path.isfile(self.plant_df_file)
        if self.file_check == False: # File does not exist, create dataframe with test data
            self.plant_df = pd.DataFrame(example_plant_entry_dict)
            print('No plants defined.')
            self.plant_df_cur_index = 0
        else: # File exists load as a dataframe
            self.plant_df = pd.read_csv(self.plant_df_file)
            self.plant_df_cur_index = self.plant_df['Plant index'].max()
            
    def __str__(self):
        return 'Plants Object: Example -> ' + str(self.plant_df['Plant name'][0])
    def make_plant_df(self,z,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p):
        data_temp = {
            'Plant index': [z],
            'Plant category': [a], # 'Vegetables', 'Flowers'
            'Plant name': [b], # 'Broccoli'
            'Plant variety': [c], # 'Waltham 29'
            'Germination start': [d], # 0
            'Germination end': [e], # 1
            'Maturity start': [f], # 0
            'Maturity end': [g], # 1
            'Genetics 1': [h], #  'Heirloom','Hybrid', 'Unknown'
            'Genetics 2': [i], # 'Annual', 'Perennial', 'Unknown
            'Genetics 3': [j], # 'Full Sun'
            'Plant depth start': [k], # .25
            'Plant depth end': [l], # .5
            'Plant spacing start': [m], # 12
            'Plant spacing end': [n], # 18
            'Number of plants per space': [o], # 1
            'Other notes': [p] # eg determinate
        }
    def plant_csv_update(self):
        if self.file_check == True:
            # Append the new data to the existing DataFrame
            self.plant_df = pd.concat([self.plant_df, self.plant_df_new], ignore_index=False)
            # Write the updated DataFrame back to the CSV file
            self.plant_df.to_csv(self.plant_df_file, index=False)
        else:
            self.plant_df_new.to_csv(self.plant_df_file, index=False)
    def garden_entry(self):
        return self.plant_df
    def plant_entry(self):
        # Multiselection box 
        conf_msg_list = ['Plant category:\n example Vegetables', \
            'Plant name:', \
            'Plant variety:', \
            'Germination start:', \
            'Germination end:', \
            'Maturity start:', \
            'Maturity end:', \
            'Genetics 1 \n example Heirloom:', \
            'Genetics 2 \n example Annual:', \
            'Genetics 3 \n example Full Sun:', \
            'Plant depth min (in inches):', \
            'Plant depth max (in inches):', \
            'Plant spacing min (in inches):', \
            'Plant spacing max (in inches):', \
            'Number of plants per space:', \
            'Other Notes']
        msg_list = []
        for i in range(len(conf_msg_list)):
            #User input on run_time settings with respective config updates
            msg_list.append(f'{conf_msg_list[i]}:')
        catch_cancel = 0
        try:
            gbg_config_list = j_lib.j_lib_user_input_handling.multi_enter_box(msg_list, ['Vegetables','','','0','1',\
                '0','1','Heirloom','Perennial','Full Sun','.25','.25','1','1','1','none'], 'Garden Planner & Tracker\nNew plant entry form: by jahascow')
        except:
            catch_cancel = 1
        if catch_cancel == 0: # error handling for user who exits the entry form
            print("here: ",gbg_config_list)
            #for i in range(14):# to print index and alpha index of df
            #    print(f'{chr(97+i)}{i} = {gbg_config_list[i]}')
            # using list comprehension to assign variables from list element
            d,e,f,g,o = [int(gbg_config_list[z]) for z in (3,4,5,6,14)] 
            k,l,m,n = [float(gbg_config_list[z]) for z in (10,11,12,13)] 
            a,b,c,h,i,j,p = [str(gbg_config_list[z]) for z in (0,1,2,7,8,9,15)] 
            # now we need to build a dataframe dictionary with these variables 
            self.make_plant_df(self.plant_df_cur_index+1,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p)
            # now we need to save / append to existing data & datafile
            self.plant_csv_update()



def menu_select(title,options,size,image,image_resize):
    def shutdown_app():
        print("Performing cleanup tasks...")
        root.quit()
        print("Closing application window...")
        root.destroy()
    def menu_option_selected(selected):
        if selected == 'Enter New Plant':
            plants_obj.plant_entry()
        elif selected == 'View Plants':
            plants_display()
        elif selected == 'Log Garden Activity': #title,options,size,image,image_resize
            shutdown_app()
            # Plant category Plant name	Plant variety
            category_list = list(set(plants_obj.plant_df['Plant category'].values.tolist()))
            name_list = list(set(plants_obj.plant_df['Plant name'].values.tolist()))
            variety_list = list(set(plants_obj.plant_df['Plant variety'].values.tolist()))
            log_entry('Garden Planner & Tracker:: Log Entry: by jahascow',
                category_list, name_list, variety_list, '450x550',os.path.join(os.path.dirname(__file__), 
                'assets', str('plants_bg2.png')),(450, 225))
        else:
            return None
        return None
    # Create the default window 
    root = Tk() 
    root.title(title) 
    root.geometry(size) 
    root.configure(background='light green')
    # set ttk theme to "clam" which support the fieldbackground option
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview", background="light grey", 
            fieldbackground="light green", foreground="black")
    # Read the Image
    image = Image.open(image)
    resized_image = image.resize(image_resize)
    # Convert the resized image for Tkinter
    img = ImageTk.PhotoImage(resized_image)

    # Create a label and assign image
    label = Label(image=img)
    label.image = img  # Keep a reference to avoid garbage collection
    label.grid(row=0,columnspan=3)
    
    def get_value_inside():
        selected = value_inside.get()
        menu_option_selected(selected)  
    # Create the list of options 
    options_list = options 
    # Variable to keep track of the option 
    # selected in OptionMenu 
    value_inside = StringVar(root) 
    # Set the default value of the variable 
    value_inside.set("Select Option") 
    question_menu = OptionMenu(root, value_inside, *options_list) 
    question_menu.grid(row=1, column=1, pady=15, sticky='e') 
    
    # Submit button for selected option
    submit_button = Button(root, text='Run Selected',
                           command=get_value_inside) #,anchor='w', justify='left',
    submit_button.grid(row=1, column=2, pady=15, padx=10, sticky='w') 
    
    
    # Button for closing
    Button(root, text="Exit", bg='green', fg='white', command=shutdown_app).grid(row=2, columnspan=3, pady=25)
    root.mainloop() 


if __name__ == '__main__':
    
    plants_obj = Plants()
    menu_select('Garden Planner & Tracker:: Main Menu: by jahascow',
                ['View Plants', 'Enter New Plant', 'Log Garden Activity'],
                '450x350',os.path.join(os.path.dirname(__file__), 
                'assets', str('plants_bg.png')),(450, 225))
