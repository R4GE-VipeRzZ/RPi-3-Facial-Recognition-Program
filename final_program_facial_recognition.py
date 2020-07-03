# Facial recognition program
# Written by Benjamin Thompson
# Python 3.4.2

import sys
import os
from tkinter import *
from time import sleep
import numpy as np
from PIL import Image
from subprocess import Popen
import sqlite3
from datetime import date
import RPi.GPIO as GPIO
import subprocess


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

sys.path.append('/usr/local/lib/python3.4/site-packages')   #Needed so that python can find cv2

import cv2

Popen(['sudo', 'modprobe', 'bcm2835-v4l2'])     #Needs to be run for cv2.cvtcolor to work, if an error occurs with cvtcolor then the camera most likely isn't plugged in right

root = Tk()

forename_input = StringVar()        #Used to store forename input before it is saved into temp table
surname_input = StringVar()         #Used to store surname input before it is saved into temp table
date_of_birth_input = StringVar()   #Used to store date of birth input before it is saved into temp table
job_title_input = StringVar()       #Used to store job title input before it is saved into temp table
remove_user_id_input = StringVar()  #Used to store the id that the user inputs for delete user by id before the user is deleted 

conn = sqlite3.connect("user_database.db")
c = conn.cursor()

def quit_program():     #This stops both tkinter and python
    conn.commit()
    conn.close()
    root.destroy()
    sys.exit()

def camera_not_plugged_in_window():
    no_camera_text = Label(root, text="No camera is plugged in, please shutdown your Raspberry Pi,\n plug a camera in and turn the Raspberry Pi back on")
    no_camera_text.grid(row=0, column=0, pady=10)
    ok_button = Button(root, text="Ok", command = quit_program)
    ok_button.grid(row=1, column=0, pady=4)

def is_camera_plugged_in():
    camera = subprocess.check_output(["vcgencmd","get_camera"])

    camera = list(str(camera))
    camera = camera[23]

    if camera == "1":
        add_user_or_recognise_face()
    elif camera == "0":
        camera_not_plugged_in_window()

def error_check_date_of_birth():
    count = True  #Stops a year lower than 1899 been put in

    word = date_of_birth_input.get()
    word_array = list(word)
        
    if len(word) != 10:     #If the date of birth isn't 10 charcters then it will prompt the user to try again
        count = True
    elif len(word) == 10:   #If the date of birth is 10 characters then this will run
        x = int(0)
        validation = [0,0,0,0,0,0,0,0,0,0]  #This creates the array to store the amount of forward slashes in the user input
        date_of_birth_layout = [-1, -1, 0, -1, -1, 0, -1, -1, -1, -1]   #If the validation array looks like this then the forward slashes are in the correct place

        for i in range (0, 10):     #This needs to repeated 10 times as the user inputs ten characters
            answer = word_array[x].find("/")    #If the array finds a forward slash in the array then a 0 is stored in that loction, if a forward slash isn't found then a -1 is stored in that location
            validation[x] = answer      #This saves the result of each back slash check into the validation array
            x = x+1

        if validation == date_of_birth_layout:      #If this is true then the back slashes are in the correct place
            count = False
            x = int(0)
            for i in range (0,10):
                if x == 2 or x == 5:    #This stops the forward slashes been checked as if the input gets to this point then forward slashes have been put in the correct place
                    x = x + 1
                else:
                    if word_array[x] == "0" or word_array[x] == "1" or word_array[x] == "2" or word_array[x] == "3" or word_array[x] == "4" or word_array[x] == "5" or word_array[x] == "6" or word_array[x] == "7" or word_array[x] == "8" or word_array[x] == "9":    #This checks that the data of birth is numbers not letters
                        x = x + 1
                    elif word_array[x] != "0" or word_array[x] != "1" or word_array[x] != "2" or word_array[x] != "3" or word_array[x] != "4" or word_array[x] != "5" or word_array[x] != "6" or word_array[x] != "7" or word_array[x] != "8" or word_array[x] != "9":  #This make count True if the date has a latter in it
                        x = x + 1
                        count = True
        elif validation != date_of_birth_layout:
            count = True

    if count == False:  #This test if the year is valid
        if word_array[6] != "1" and word_array[6] != "2":
            count = True
        elif word_array[6] == "1":
            count = False
            if word_array[7] != "8" and word_array[7] != "9":
                count = True
            elif word_array[7] == "8":
                if word_array[8] != "9" or word_array[9] != "9":
                    count = True
                elif word_array[8] == "9" or word_array[9] == "9":      #Add to stop any earlier than 29/11/1899
                    if word_array[3] != "1":
                        count = True
                    elif word_array[3] == "1":
                        if word_array[4] != "1" and word_array[4] != "2":
                            count = True
                        elif word_array[4] == "1" or word_array[4] == "2":
                            if word_array[4] == "1":
                                if word_array[0] == "2":
                                    if word_array[1] != "9":
                                        count = True
                                    elif word_array[1] == "9":
                                        count = False
                                elif word_array[0] == "3":
                                    if word_array[1] != "0":
                                        count = True
                                    elif word_array[0] == "0":
                                        count = False
                            
                        
                            
            elif word_array[7] == "9":
                count = False
        elif word_array[6] == "2":
            if word_array[7] != "0":
                count = True
            elif word_array[7] == "0":
                if word_array[8] != "0" and word_array[8] != "1":
                    count = True
                elif word_array[8] == "0":
                    count = False
                elif word_array[8] == "1":
                    if word_array[9] == "8" or word_array[9] == "9":
                        count = True
                    elif word_array[9] != "8" or word_array[9] != "9":
                        count = False
                            
    if count == False:      #This test for a valid month
        if word_array[3] == "1":
            if word_array[4] == "0" or word_array[4] == "1" or word_array[4] == "2":
                count = False
            elif word_array[4] != "0" or word_array[4] != "1" or word_array[4] != "2":
                count = True
        elif word_array[3] == "0":
            if word_array[4] == "0":
                count = True
            elif word_array[4] != "0":
                count = False
        elif word_array[3] != "0" and word_array[3] != "1":
            count = True
                    
    if count == False:      #This test for a valid day
        if word_array[0] == "0" and word_array[1] == "0":
            count = True
        else:
            if word_array[3] == "0" and word_array[4] == "1" or word_array[3] == "0" and word_array[4] == "3" or word_array[3] == "0" and word_array[4] == "5" or word_array[3] == "0" and word_array[4] == "7" or word_array[3] == "0" and word_array[4] == "8" or word_array[3] == "1" and word_array[4] == "0" or word_array[3] == "1" and word_array[4] == "2":     #So it only runs on months with 31 days
                if word_array[0] != "0" and word_array[0] != "1" and word_array[0] != "2" and word_array[0] != "3":
                    count = True
                elif word_array[0] == "3":
                    if word_array[1] != "0" and word_array[1] != "1":
                        count = True
                    elif word_array[1] == "0" or word_array[1] == "1":
                        count = False
                else:
                    count = False
            elif word_array[3] == "0" and word_array[4] == "4" or word_array[3] == "0" and word_array[4] == "6" or word_array[3] == "0" and word_array[4] == "9" or word_array[3] == "1" and word_array[4] == "1":
                if word_array[0] != "0" and word_array[0] != "1" and word_array[0] != "2" and word_array[0] != "3":
                    count = True
                elif word_array[0] == "3":
                    if word_array[1] != "0":
                        count = True
                    elif word_array[1] == "0":
                        count = False
                    else:
                        count = False
            elif word_array[3] == "0" and word_array[4] == "2":           #Febuary
                year = (word_array[6], word_array[7], word_array[8], word_array[9])
                year = ''.join(year)
                year = int(year)

                year = year/4

                year = str(year)
                year_array = list(year)
                    
                if year_array[4] != "0":
                    if word_array[0] != "0" and word_array[0] != "1" and word_array[0] != "2":
                        count = True
                    elif word_array[0] == "0" and word_array[0] == "1":
                        count = False
                    elif word_array[0] == "2":
                        if word_array[1] == "9":
                            count = True
                        elif word_array[1] != "9":
                            count = False
                elif year_array[4] == "0":
                    if word_array[0] != "0" and word_array[0] != "1" and word_array[0] != "2":
                        count = True
                    elif word_array[0] == "0" and word_array[0] == "1" and word_array[0] == "2":
                        count = False
                    else:
                        count = False
            else:
                count = False 
        
    if count == False:
        date_valid = True
    else:
        date_valid = False
     
    return date_valid

def find_user_id():
    try:        #The try is needed incase the database is empty
        path = "/home/pi/Desktop/facial_recognition/data_set"      #Path of the user database
        dirs = os.listdir(path)     #stores all the file names in an array

        all_numbers = []        #This stores all the user ids stored in the user database even if there are more than one image of the same user so user numbers may be repated
        numbers = []        #This array is used to stored all the user ids in the database without any repeated numbers

        for file in dirs:       #This seperates the user id number from the file name and stores all the user ids in the all_numbers array
            file = file.split(".")
            all_numbers.append(file[1])

        for i in all_numbers:       #This saves one of each user id in the numbers array so that there are no repeated numbers
            if i not in numbers:
                numbers.append(i)

        numbers.sort()      #This rearanges the array from smallest to largest number

        largest_number = numbers[(len(numbers)-1)]  #This finds the biggest number in the array and stores the largest_number variable
        largest_number = int(largest_number) + 1    #This adds 1 onto the largest number in the array as that is the next avaliable one

        numbers = ",".join(numbers)     #This converts the numbers array to a string

        int_list = [int(x) for x in numbers.split(',')]     #This splits up the numbers in the string

        missing_number = []
        for i in range(1, max(int_list)):   #This finds if there is a missing number in the number list, it will stop when it finds a missing number
            if not i in int_list:
                missing_number.append(i)

        if len(missing_number) != 0:    #This will occur if there is a missing number in a number range (eg. 1, 2, 3, 5   4 would be the missing_number)
            user_id = missing_number[0]     #Sets the user id to the missing number
        elif len(missing_number) == 0:  #This will occur if there isn't a missing number
            user_id = largest_number        #Sets the user id to the next number (eg.1, 2, 3, 4, 5   6 would be the largest_number
    except IndexError:
        user_id = 1         #This will occur if the image database is empty, if the image database is empty then you want the user_id to be 1
    return user_id

def calculate_age():        #This calculates the age of a user using the date of birth and current date
    date_of_birth = date_of_birth_input.get()
    date_of_birth = date_of_birth.split("/")

    today = (str(date.today())).split('-')      #This splits the current date into an array today[0] = year   today[1] = day   today[2] = month


    if (int(today[1]) - int(date_of_birth[1])) > 0:     #This calculates the age and then stores it in the age variable
        age = int(today[0]) - int(date_of_birth[2])
    elif (int(today[1]) - int(date_of_birth[1])) < 0:
        age = (int(today[0]) - int(date_of_birth[2]))-1
    elif (int(today[1]) - int(date_of_birth[1])) == 0:
        if (int(today[2]) - int(date_of_birth[0])) < 0:
            age = (int(today[0]) - int(date_of_birth[2])) - 1
        elif (int(today[2]) - int(date_of_birth[0])) >= 0:
            age = (int(today[0]) - int(date_of_birth[2]))
    return age


def create_worker_table():
    c.execute("CREATE TABLE IF NOT EXISTS worker_table(user_id INTEGER, forename TEXT, surname TEXT, age TEXT, job_title TEXT)")    #Creates the worker table

def create_guest_adult_table():
    c.execute("CREATE TABLE IF NOT EXISTS guest_adult_table(user_id INTEGER, forename TEXT, surname TEXT, age TEXT)")    #Creates the guest adult table

def create_guest_child_table():
    c.execute("CREATE TABLE IF NOT EXISTS guest_child_table(user_id INTEGER, forename TEXT, surname TEXT, age TEXT)")    #Creates the guest child table

def create_temp_table():
    c.execute("CREATE TABLE IF NOT EXISTS temp.temp_table(user_id INTEGER, forename TEXT, surname TEXT, age TEXT, job_title TEXT)")      #Create temp table


def temp_table_data_entry_worker():     #This enters the worker information in to the temp table
    user_id = find_user_id()
    forename = forename_input.get()
    surname = surname_input.get()
    age = calculate_age()
    job_title = job_title_input.get()
    
    c.execute("INSERT INTO temp_table (user_id, forename, surname, age, job_title) VALUES (?, ?, ?, ?, ?)",
              (user_id, forename, surname, age, job_title))    #The variable that are been input
    conn.commit()

def temp_table_data_entry_guest():      #This enters the guest information in to the temp table 
    user_id = find_user_id()
    forename = forename_input.get()
    surname = surname_input.get()
    age = calculate_age()
    job_title = None
    
    c.execute("INSERT INTO temp_table (user_id, forename, surname, age, job_title) VALUES (?, ?, ?, ?, ?)",
              (user_id, forename, surname, age, job_title))    #The variable that are been input
    conn.commit()

def submit_users_to_database():
    def train_program():
        recognizer = cv2.face.createLBPHFaceRecognizer()
        path = "/home/pi/Desktop/facial_recognition/data_set"
        
        def get_images_with_id(path):      #This function trains the program about what faces should be recognised
            image_paths= [os.path.join(path, f) for f in os.listdir(path)]       #This gets all the images from the image database
            faces = []
            IDs = []
            for image_path in image_paths:
                face_img = Image.open(image_path).convert("L")    #This converts every image to a PIL image
                face_np = np.array(face_img, "uint8")             #This assigns the unit8 data type to the PIL image array
                ID = int(os.path.split(image_path) [-1].split(".")[1])       #This gets the ID from the image file name
                faces.append(face_np)        #This appends every numpy image array to the faces array
                IDs.append(ID)              #This appends all the user id's to the IDs arraay
                cv2.imshow("Training... ", face_np)      #This cause the images that are been used to train the program to appear
                cv2.waitKey(1)      #Causes the program to wait a millisecond before to trains the program with the next image
            return IDs, faces

        Ids, faces = get_images_with_id(path)
        recognizer.train(faces, np.array(Ids))
        recognizer.save("/home/pi/Desktop/facial_recognition/recognizer/traning_data.yml")      #This saves the traning of the program so that it can be read every time you want to recognise a user instead of traning the program every time
        cv2.destroyAllWindows()     #Removes all the cv2 windows
        
    count = True

    while count == True:
        try:
            c.execute("SELECT * FROM temp_table")       #This causes the first line of the
            data = c.fetchone()                         #temp table to be selected
            user_id = data[0]

            if data[4] == None:     #This is used to decided if the user is a worker of guest, if this is true then the user is a guest
                forename = data[1]
                surname = data[2]
                age = data[3]

                if int(data[3]) >= 18:      #If this is true then the user is a adult guest
                    count = True
                    
                    c.execute("INSERT INTO guest_adult_table(user_id, forename, surname, age) VALUES(?, ?, ?, ?)",      #This inserts the user into the guest_adult_table
                             (user_id, forename, surname, age))
                    conn.commit()

                    
                    c.execute("SELECT * FROM temp_table")
                    c.execute("DELETE FROM temp_table WHERE user_id =(?)", (user_id,))      #This deletes the user from the temp table once they have been saved into the guest_adult_table
                    conn.commit()
                elif int(data[3]) < 18:     #If this is true then the user is a child guest
                    count = True
                    
                    c.execute("INSERT INTO guest_child_table(user_id, forename, surname, age) VALUES(?, ?, ?, ?)",      #This inserts the user into the guest_child_table
                             (user_id, forename, surname, age))
                    conn.commit()

                    
                    c.execute("SELECT * FROM temp_table")
                    c.execute("DELETE FROM temp_table WHERE user_id =(?)", (user_id,))      #This deletes the user from the temp table once they have been saved into the guest_child_table
                    conn.commit()

            elif data[4] != None:       #This is used to decided if the user is a worker of guest, if this is true then the user is a worker
                count = True
                
                
                forename = data[1]
                surname = data[2]
                age = data[3]
                job_title = data[4]

                c.execute("INSERT INTO worker_table (user_id, forename, surname, age, job_title) VALUES (?, ?, ?, ?, ?)",       #This inserts the user into the worker_table
                         (user_id, forename, surname, age, job_title))
                conn.commit()
                
                c.execute("SELECT * FROM temp_table")
                c.execute("DELETE FROM temp_table WHERE user_id =(?)", (user_id,))      #This deletes the user from the temp table once they have been saved into the worker_table
                conn.commit()
        except TypeError:
            count = False       #This will occur when the temp table is empty, change the count to false cause the program to drop out of the while loop

    train_program()
    add_user_or_recognise_face()

def add_user_to_dataset():          
    face_cascade = cv2.CascadeClassifier("/home/pi/Desktop/facial_recognition/haarcascade_frontalface_default.xml")     #This variable contains the haarcascade used to detect a face

    cam = cv2.VideoCapture(0)       #This variable stores the images captured by the camera

    user_id = find_user_id()
    sampleNum = 0

    while True:
        ret, img = cam.read()       #This reads the image captured by the camera
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)        #This converts the image to gray scale
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)     #This decideds how the haarcascade detects a face
        for (x,y,w,h) in faces:
            sampleNum = sampleNum + 1
            cv2.imwrite("/home/pi/Desktop/facial_recognition/data_set/User."+str(user_id)+"."+str(sampleNum)+".jpg", gray[y: y+h, x: x+w])  #This stores the image taken of the users face
            cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 2)     #This overlays the rectangle around the detected users face
            cv2.waitKey(1)      #Causes the program to wait a millisecond before it adds another image to the dataset
        cv2.imshow("Faces", img)    #This shows the image that is been added to the dataset
        cv2.waitKey(1)      #Causes the program to wait a millisecond

        if sampleNum > 19:  #This decides the number of pictures that are taken of a person
            break

    cam.release()       #The stops the images captured by the camera been stored in cam
    cv2.destroyAllWindows()     #This deletes all cv2 windows 
    add_more_users_or_submit()

def add_user_image_to_database():   #This will make the window appear after the user has submitted there information
    def delete_add_user_window():
        ok_button.grid_remove()
        instructions_text.grid_remove()
        face_recognition_instructions.grid_remove()
        add_user_to_dataset()
    instructions_text = Label(root, text="Instructions")
    instructions_text.grid(row=0, column=0)
    face_recognition_instructions = Label(root, text="Press the Ok button to start taking pictures of the\n users face, once you click the Ok button please look\n directly at the camera then slight to the left\n and then slightly to the right")
    face_recognition_instructions.grid(row=1, column=0, sticky=W, pady= 20)
    ok_button = Button(root, text="Ok", command = delete_add_user_window)
    ok_button.grid(row=2, column=0, pady=4)

def worker_input_form():    #This will make the worker input window and form appear
    def validate_worker_input():        #Checks that the data that is put into the worker form is valid       
        forename = forename_input.get()
        surname = surname_input.get()
        job_title = job_title_input.get()

        def display_error_message():
            global error_text_worker
            error_text_worker = Label(root, text=error_message, fg="red")
            error_text_worker.grid(row=4, column=1)

        date_valid = error_check_date_of_birth()

        if len(forename) == 0:      #Tests to see if the forename is empty 
            error_message = "                                                                      "
            display_error_message()
            error_message = "First Name is empty, please fill it in"
            display_error_message()
        elif len(forename) == 1:    #Tests to see if the forename is only one character
            error_message = "                                                                      "
            display_error_message()
            error_message = "First Name isn't long enough, please fill it in"
            display_error_message()
        elif len(forename) > 25:    #Tests to see if the forename is longer than 25 characters
            error_message = "                                                                      "
            display_error_message()
            error_message = "First Name is too long, please try again"
            display_error_message()
        elif list(forename)[0].isupper() == False:      #Checks to see if the forename starts with a capital letter
            error_message = "                                                                      "
            display_error_message()
            error_message = "First Name must start with a capital letter"
            display_error_message()
        elif " " in forename:   #Checks that no spaces are in forename
            error_message = "                                                                      "
            display_error_message()
            error_message = "First Name must not contain spaces"
            display_error_message()
        else:
            if len(surname) == 0:       #Tests to see if the surname is empty 
                error_message = "                                                                      "
                display_error_message()
                error_message = "Last Name is empty, please fill it in"
                display_error_message()
            elif len(surname) == 1:     #Tests to see if the surname is only on character
                error_message = "                                                                      "
                display_error_message()
                error_message = "Last Name isn't long enough, please fill it in"
                display_error_message()
            elif len(surname) > 25:     #Tests to see if the surname is longer than 25 characters
                error_message = "                                                                      "
                display_error_message()
                error_message = "Last Name is too long, please try again"
                display_error_message()
            elif list(surname)[0].isupper() == False:       #Tests to see if the surname starts with a capital letter
                error_message = "                                                                      "
                display_error_message()
                error_message = "Last Name must start with a capital letter"
                display_error_message()
            elif " " in surname:   #Checks that no spaces are in surname
                error_message = "                                                                      "
                display_error_message()
                error_message = "Last Name must not contain spaces"
                display_error_message()
            else:
                if date_valid != True:      #Tests to see if the date entered is valid
                    error_message = "                                                                      "
                    display_error_message()
                    error_message = "Date Of Birth incorrect please try again"
                    display_error_message()
                else:
                    if len(job_title) == 0:     #Tests to see if the job title is empty 
                        error_message = "                                                                      "
                        display_error_message()
                        error_message = "Job Title is empty, please fill it in"
                        display_error_message()
                    elif len(job_title) == 1 or len(job_title) == 2:        #Tests to if the job title is only one or two characters
                        error_message = "                                                                      "
                        display_error_message()
                        error_message = "Job Title isn't long enough, please fill it in"
                        display_error_message()
                    elif len(job_title) > 35:       #Tests to see if the job title is longer than 35 characters 
                        error_message = "                                                                      "
                        display_error_message()
                        error_message = "Job Title is too long, please try again"
                        display_error_message()
                    elif list(job_title)[0].isupper() == False:     #Tests to see if the job title starts with a capital letter 
                        error_message = "                                                                      "
                        display_error_message()
                        error_message = "Job Title must start with a capital letter"
                        display_error_message()
                    else:
                        first_name_text.grid_remove()
                        last_name_text.grid_remove()
                        date_of_birth_text.grid_remove()
                        job_title_text.grid_remove()
                        error_text_worker.grid_remove()
                        first_name_entry.grid_remove()
                        last_name_entry.grid_remove()
                        date_of_birth_entry.grid_remove()
                        job_title_entry.grid_remove()
                        quit_button.grid_remove()
                        ok_button.grid_remove()
                        temp_table_data_entry_worker()
                        add_user_image_to_database()

    global error_text_worker
    error_message = "Please fill in the form"
    error_text_worker = Label(root, text=error_message, fg="red")
    error_text_worker.grid(row=4, column=1)
            
    first_name_text = Label(root, text="First Name")
    first_name_text.grid(row=0)
    last_name_text = Label(root, text="Last Name")
    last_name_text.grid(row=1)
    date_of_birth_text = Label(root, text="Date Of Birth")
    date_of_birth_text.grid(row=2)
    job_title_text = Label(root, text="Job Title")
    job_title_text.grid(row=3)

    first_name_entry = Entry(root, textvariable = forename_input)
    last_name_entry = Entry(root, textvariable = surname_input)
    date_of_birth_entry = Entry(root, textvariable = date_of_birth_input)
    job_title_entry = Entry(root, textvariable = job_title_input)

    first_name_entry.delete(0, 'end')         #Needed to ensure that the Fore Name box is empty
    last_name_entry.delete(0, 'end')         #Needed to ensure that the Last Name box is empty
    date_of_birth_entry.delete(0, 'end')         #Needed to ensure that the entry box is empty before the example date layout is input
    date_of_birth_entry.insert(1, "dd/mm/yyyy")
    job_title_entry.delete(0, 'end')         #Needed to ensure the job title box is empty

    first_name_entry.grid(row=0, column=1)
    last_name_entry.grid(row=1, column=1)
    date_of_birth_entry.grid(row=2, column=1)
    job_title_entry.grid(row=3, column=1)

    quit_button = Button(root, text="Quit", command = quit_program)
    quit_button.grid(row=5, column=0, sticky=W, pady=4)
    ok_button = Button(root, text="Ok", command = validate_worker_input)
    ok_button.grid(row=5, column=1, sticky=W, pady=4)

def guest_input_form():     #This will make the guest input window and form appear
    def validate_worker_input():        #Checks that the data that is put into the worker form is valid
        forename = forename_input.get()
        surname = surname_input.get()

        def display_error_message():
            global error_text_guest
            error_text_guest = Label(root, text=error_message, fg="red")
            error_text_guest.grid(row=4, column=1)

        date_valid = error_check_date_of_birth()
        

        if len(forename) == 0:      #Tests to see if forename is empty
            error_message = "                                                                      "
            display_error_message()
            error_message = "First Name is empty, please fill it in"
            display_error_message()
        elif len(forename) > 25:    #Tests to see if forename is longer than 25 characters
            error_message = "                                                                      "
            display_error_message()
            error_message = "First Name is too long, please try again"
            display_error_message()
        elif len(forename) == 1:    #Tests to see if the forename is only one character
            error_message = "                                                                      "
            display_error_message()
            error_message = "First Name isn't long enough, please fill it in"
            display_error_message()
        elif list(forename)[0].isupper() == False:  #Tests to see if the forename starts with a capital letter
            error_message = "                                                                      "
            display_error_message()
            error_message = "First Name must start with a capital letter"
            display_error_message()
        elif " " in forename:   #Checks that no spaces are in forename
            error_message = "                                                                      "
            display_error_message()
            error_message = "First Name must not contain spaces"
            display_error_message()
        else:
            if len(surname) == 0:   #Tests to see if surname is empty
                error_message = "                                                                      "
                display_error_message()
                error_message = "Last Name is empty, please fill it in"
                display_error_message()
            elif len(surname) == 1:     #Tests to see if the surname is only one character 
                error_message = "                                                                      "
                display_error_message()
                error_message = "Last Name isn't long enough, please fill it in"
                display_error_message()
            elif len(surname) > 25:     #Tests to see if surname is longer than 25 characters
                error_message = "                                                                      "
                display_error_message()
                error_message = "Last Name is too long, please try again"
                display_error_message()
            elif list(surname)[0].isupper() == False:   #Tests to see if the surname starts with a capital letter
                error_message = "                                                                      "
                display_error_message()
                error_message = "Last Name must start with a capital letter"
                display_error_message()
            elif " " in surname:    #Checks that no spaces are in surname
                error_message = "                                                                      "
                display_error_message()
                error_message = "Last Name must not contain spaces"
                display_error_message()
            else:
                if date_valid != True:      #Checks to see if the date entered is valid
                    error_message = "                                                                      "
                    display_error_message()
                    error_message = "Date Of Birth incorrect please try again"
                    display_error_message()
                else:
                    first_name_text.grid_remove()
                    last_name_text.grid_remove()
                    date_of_birth_text.grid_remove()
                    error_text_guest.grid_remove()
                    first_name_entry.grid_remove()
                    last_name_entry.grid_remove()
                    date_of_birth_entry.grid_remove()
                    quit_button.grid_remove()
                    ok_button.grid_remove()
                    temp_table_data_entry_guest()
                    add_user_image_to_database()

    global error_text_guest
    error_message = "Please fill in the form"
    error_text_guest = Label(root, text=error_message, fg="red")
    error_text_guest.grid(row=4, column=1)
            
    first_name_text = Label(root, text="First Name")
    first_name_text.grid(row=0)
    last_name_text = Label(root, text="Last Name")
    last_name_text.grid(row=1)
    date_of_birth_text = Label(root, text="Date Of Birth")
    date_of_birth_text.grid(row=2)

    first_name_entry = Entry(root, textvariable = forename_input)
    last_name_entry = Entry(root, textvariable = surname_input)
    date_of_birth_entry = Entry(root, textvariable = date_of_birth_input)


    first_name_entry.delete(0, 'end')         #Needed to ensure that the Fore Name box is empty
    last_name_entry.delete(0, 'end')         #Needed to ensure that the Last Name box is empty 
    date_of_birth_entry.delete(0, 'end')             #Needed to ensure that the entry box is empty before the example date layout is input
    date_of_birth_entry.insert(1, "dd/mm/yyyy")

    first_name_entry.grid(row=0, column=1)
    last_name_entry.grid(row=1, column=1)
    date_of_birth_entry.grid(row=2, column=1)

    quit_button = Button(root, text="Quit", command = quit_program)
    quit_button.grid(row=5, column=0, sticky=W, pady=4)
    ok_button = Button(root, text="Ok", command = validate_worker_input)
    ok_button.grid(row=5, column=1, sticky=W, pady=4)

def facial_recognition():       #This function contains that code need to recognise a face
    faceDetect = cv2.CascadeClassifier("/home/pi/Desktop/facial_recognition/haarcascade_frontalface_default.xml")

    cam = cv2.VideoCapture(0)       #This stores the images been captured by the camera
    rec = cv2.face.createLBPHFaceRecognizer()       #This loads the algorythm used for facial recognition into the rec variable
    rec.load("/home/pi/Desktop/facial_recognition/recognizer/traning_data.yml")     #This loads the traning performed when a user was added to the database
    user_id = 0
    font = cv2.FONT_HERSHEY_SIMPLEX     #This assigns the font that cv2 will use for the overlay to the font variable
    rectangle_colour = (0,0,255)        #This assigns the colour red to the rectangle could in RGB form

    while True:
        ret, img = cam.read()       #This reads the image captured by the camera
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)        #This converts the image to gray scale
        faces = faceDetect.detectMultiScale(gray, 1.1, 5)       #This decideds how the haarcascade detects a face
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w, y+h), (rectangle_colour), 2)    #This creates a rectangle around the detected face
            user_id, conf=rec.predict(gray[y: y+h, x: x+w])      #This what id the program thinks the person look at the camera has, conf is how confident the program is that the user is who it says the close to 0 conf is the more certain the program is that it recognises the face correctly

            if conf <= 70:      #The larger the number the more likely it is the program will incorrectly recognise a face 
                user_id_string = str(user_id)   #This section uses the id of the recognised user and then searches the user database for the id
                                                #once the user id is found the forename is then read from the database 
                count = True                    #The forename that is read from the database is then set as the user id 

                while count == True:
                    c.execute("SELECT user_id, forename FROM worker_table WHERE user_id = (?)", (user_id_string,))
                    data = c.fetchall()

                    if len(data) != 0:
                        count = False
                    elif len(data) == 0:
                        c.execute("SELECT user_id, forename FROM guest_child_table WHERE user_id = (?)", (user_id_string,))
                        data = c.fetchall()

                        if len(data) != 0:
                            count = False
                        elif len(data) == 0:
                            c.execute("SELECT user_id, forename FROM guest_adult_table WHERE user_id = (?)", (user_id_string,))
                            data = c.fetchall()

                            if len(data) != 0:
                                 count = False
                            elif len(data) == 0:
                                user_name = "Unknown"

                data_base_line = str(data)

                data_base_line = ((((((data_base_line.replace("(", "")).replace("[", "")).replace(")", "")).replace("]", "")).replace("'", ""))).replace(" ", "")

                id_of_user, user_name = data_base_line.split(",")

                user_id = user_name
                rectangle_colour = (0,255,0)        #This changes the colour of the rectangle to green
                GPIO.output(18,GPIO.HIGH)
            elif conf > 70:     #If the confidence is greater than 65 then the user isn't recognised and the user id is set as Unknown, the colour of the rectangle is change to red
                rectangle_colour = (0,0,255)
                GPIO.output(18,GPIO.LOW)
                user_id = "Unknown"
            else:
                GPIO.output(18,GPIO.LOW)
                    
                        
            cv2.putText(img, str(user_id), (x, y+h), font, 0.8,(255,255,255),2,cv2.LINE_AA)   #The LINE_AA just makes the text look better        This overlays the id of the user
        cv2.imshow("Face", img)     #This shows the view of the camera
        if cv2.waitKey(1) == ord("q"):      #This waits for the q button to be pressed 
            add_user_or_recognise_face()    #Once the q button is pressed it goes back to the gui and stops the facial recognition
            break

    cam.release()       #Stops the images from the camera been stored in cam    
    cv2.destroyAllWindows()     #This deletes all the open cv2 windows
    

def recognise_user_window():    #This creates the window that will appear when you click the recognise user button
    def ready_to_recognise_face():  #This function will delete all the elements in the window and start the facial recognition
        start_recognition_text.grid_remove()
        ok_button.grid_remove()
        facial_recognition()
        
    start_recognition_text = Label(root, text="Facial recognition ready to start, to close \nthe facial recognition press q")
    start_recognition_text.grid(row=0, column=0, pady=4)
    ok_button = Button(root, text="Ok", command = ready_to_recognise_face)
    ok_button.grid(row=1, column=0, pady=4)


def add_more_users_or_submit():     #This window will appear after a user has been added to the database
    def add_another_user():     #This function will delete all the elements in the window and then create the guest or worker window
        add_another_user_button.grid_remove()
        submit_added_users_button.grid_remove()
        what_to_do_text.grid_remove()
        warning_text.grid_remove()
        guest_or_worker()
    def submit_users():     #This function will delete all the elements in the window and then calls the function that sorts all the users out of the temporary table
        add_another_user_button.grid_remove()
        submit_added_users_button.grid_remove()
        what_to_do_text.grid_remove()
        warning_text.grid_remove()
        submit_users_to_database()
    what_to_do_text = Label(root, text="What would you like to do?")
    what_to_do_text.grid(row=0, column=0)
    warning_text = Label(root, text="WARNING: Closing the program without submitting \nthe added users will cause the newly added \nusers to not be saved to the database")
    warning_text.grid(row=1, column=0, pady=4)
    add_another_user_button = Button(root, text="Add Another User", command = add_another_user)
    add_another_user_button.grid(row=2, column=0, pady=4)
    submit_added_users_button = Button(root, text="Submit Added users to database", command = submit_users)
    submit_added_users_button.grid(row=3, column=0, pady=4)


def are_you_sure_single_user():     #This will cause the window to appear asking you if your sure you want to delete a single user 
    def yes_clear_single_user():    #This function will delete all elements in the window and will then remove the user that corrosponds to the user id entered
        yes_button.grid_remove()
        no_button.grid_remove()
        remove_user_warning_text.grid_remove()
        remove_single_user()
        
    def no_go_back():       #This function will delete all the elements in the window and will then create the remove user from database window
        yes_button.grid_remove()
        no_button.grid_remove()
        remove_user_warning_text.grid_remove()
        remove_user_from_database_window()

    users_id = remove_user_id_input.get()

    message_text = "Are you sure you want to remove user: " + str(users_id) + "?"
    
    remove_user_warning_text = Label(root, text= message_text , fg="red")
    remove_user_warning_text.grid(row=0, column=1, pady=4)
    yes_button = Button(root, text="Yes", command = yes_clear_single_user)
    yes_button.grid(row=1, column=0, pady=4)
    no_button = Button(root, text="No", command = no_go_back)
    no_button.grid(row=1, column=2, pady=4)


    try:
        users_id = int(users_id)
    except ValueError:
        no_go_back()
        

def remove_single_user():       #This function removes the user of the corrosponding id from the database and from the image database
    users_id = remove_user_id_input.get()
    users_id = int(users_id)

        
    
    c.execute("SELECT * FROM worker_table")
    c.execute("DELETE FROM worker_table WHERE user_id =(?)", (users_id,))
    conn.commit()

    c.execute("SELECT * FROM guest_adult_table")
    c.execute("DELETE FROM guest_adult_table WHERE user_id =(?)", (users_id,))
    conn.commit()

    c.execute("SELECT * FROM guest_child_table")
    c.execute("DELETE FROM guest_child_table WHERE user_id =(?)", (users_id,))
    conn.commit()

    directory = "/home/pi/Desktop/facial_recognition/data_set/"

    user_id_string = str(users_id)

    x = 1

    for i in range (0, 20):     #It does this 20 times as each person has 20 pictures taken of them self
        x_num = str(x)
        file_name = directory+"User."+user_id_string+"."+x_num+".jpg"
        os.remove(file_name)
        x = x + 1

    remove_user_from_database_window()
    

def remove_single_user_window():
    def remove_user_id():
        def display_error_message():
            global label7
            label7 = Label(root, text=error_message, fg="red")
            label7.grid(row=2, column=1)

        valid = False

                
        try:
            user_id = int(remove_user_id_input.get())

            path = "/home/pi/Desktop/facial_recognition/data_set"      #Path of the user database
            dirs = os.listdir(path)     #stores all the file names in an array

            all_numbers = []        #This stores all the user ids stored in the user database even if there are more than one image of the same user so user numbers may be repated
            numbers = []        #This array is used to stored all the user ids in the database without any repeated numbers

            for file in dirs:       #This seperates the user id number from the file name and stores all the user ids in the all_numbers array
                file = file.split(".")
                all_numbers.append(file[1])

            for i in all_numbers:       #This saves one of each user id in the numbers array so that there are no repeated numbers
                if i not in numbers:
                    numbers.append(i)

            numbers.sort()      #This rearanges the array from smallest to largest number

            x = 0

            for i in range (0, len(numbers)):
                if user_id != int(numbers[x]):
                    valid = False
                    x = x + 1
                elif user_id == int(numbers[x]):
                    valid = True

            if valid == True:
                enter_user_id_text.grid_remove()
                user_id_text.grid_remove()
                error_message_remove_single_text.grid_remove()
                remove_user_id_entry.grid_remove()
                ok_button.grid_remove()
                back_button.grid_remove()
                label7.grid_remove()
                are_you_sure_single_user()
            elif valid == False or len(user_id) == 0:
                error_message = "                                                                           "
                display_error_message()
                error_message = "No user in database of that id, please try again"
                display_error_message()
        except ValueError:
            error_message = "                                                                           "
            display_error_message()
            error_message = "No user in database of that id, please try again"
            display_error_message()



    def go_back():      #This function deletes all elements in the window and the creates the remove user from database window
        enter_user_id_text.grid_remove()
        user_id_text.grid_remove()
        error_message_remove_single_text.grid_remove()
        remove_user_id_entry.grid_remove()
        ok_button.grid_remove()
        back_button.grid_remove()
        label7.grid_remove()
        remove_user_from_database_window()

    global error_message_remove_single_text
    error_message = "                "
    error_message_remove_single_text = Label(root, text=error_message, fg="red")
    error_message_remove_single_text.grid(row=2, column=1)

    enter_user_id_text = Label(root, text="Enter the user id you want to deleted")
    enter_user_id_text.grid(row=0, column=1, pady=4)
    user_id_text = Label(root, text="User id")
    user_id_text.grid(row=1)
    remove_user_id_entry = Entry(root, textvariable = remove_user_id_input)
    remove_user_id_entry.grid(row=1, column=1)
    remove_user_id_entry.delete(0, 'end')
    ok_button = Button(root, text="Ok", command = remove_user_id)
    ok_button.grid(row=3, column=1, pady=4)
    back_button = Button(root, text="Back", command = go_back)
    back_button.grid(row=3, column=0, pady=4)

def are_you_sure_window_adult_tabel():      #This function creates the window that asks you if your sure you want to clear all the users from the guest adult table
    def yes_clear_guest_adult_table():      #This function deletes all the elements in the window and then clears the guest adult table
        yes_button.grid_remove()
        no_button.grid_remove()
        are_you_sure_text.grid_remove()
        delete_all_users_from_guest_adult()
        
    def no_go_back():   #This function deletes all the elements in the window and then creates the remove user from database window
        yes_button.grid_remove()
        no_button.grid_remove()
        are_you_sure_text.grid_remove()
        remove_user_from_database_window()
        
    are_you_sure_text = Label(root, text="Are you sure you want to clear the Guest Adult table?", fg="red")
    are_you_sure_text.grid(row=0, column=1, pady=4)
    yes_button = Button(root, text="Yes", command = yes_clear_guest_adult_table)
    yes_button.grid(row=1, column=0, pady=4)
    no_button = Button(root, text="No", command = no_go_back)
    no_button.grid(row=1, column=2, pady=4)

def delete_all_users_from_guest_adult(): #This deletes all the users from the guest adult table       
    count = True

    while count == True:
        try:
            c.execute("SELECT * FROM guest_adult_table")
            data = c.fetchone()
            user_id = data[0]


            c.execute("SELECT * FROM guest_adult_table")
            c.execute("DELETE FROM guest_adult_table WHERE user_id =(?)", (user_id,))
            conn.commit()
            
            directory = "/home/pi/Desktop/facial_recognition/data_set/"

            user_id_string = str(user_id)

            x = 1

            for i in range (0, 20):     #It does this 20 times as each person has 20 pictures taken of them self
                x_num = str(x)
                file_name = directory+"User."+user_id_string+"."+x_num+".jpg"
                os.remove(file_name)
                x = x + 1

        except TypeError:
            count = False
    remove_user_from_database_window()

def are_you_sure_window_child_tabel():      #This function creates the window that asks you if your sure you want to clear all the users from the guest child table
    def yes_clear_guest_child_table():      #This function deletes all the elements in the window and then clears the guest child table
        yes_button.grid_remove()
        no_button.grid_remove()
        are_you_sure_guest_text.grid_remove()
        delete_all_users_from_guest_child()
        
    def no_go_back():       #This function deltes all the elements in the window and then creates the remove user from datatbase window
        yes_button.grid_remove()
        no_button.grid_remove()
        are_you_sure_guest_text.grid_remove()
        remove_user_from_database_window()
        
    are_you_sure_guest_text = Label(root, text="Are you sure you want to clear the Guest Child table?", fg="red")
    are_you_sure_guest_text.grid(row=0, column=1, pady=4)
    yes_button = Button(root, text="Yes", command = yes_clear_guest_child_table)
    yes_button.grid(row=1, column=0, pady=4)
    no_button = Button(root, text="No", command = no_go_back)
    no_button.grid(row=1, column=2, pady=4)

def delete_all_users_from_guest_child():        #This function deletes all the users in the guest child table
    count = True

    while count == True:
        try:
            c.execute("SELECT * FROM guest_child_table")
            data = c.fetchone()
            user_id = data[0]


            c.execute("SELECT * FROM guest_child_table")
            c.execute("DELETE FROM guest_child_table WHERE user_id =(?)", (user_id,))
            conn.commit()
            
            directory = "/home/pi/Desktop/facial_recognition/data_set/"

            user_id_string = str(user_id)

            x = 1

            for i in range (0, 20):     #It does this 20 times as each person has 20 pictures taken of them self
                x_num = str(x)
                file_name = directory+"User."+user_id_string+"."+x_num+".jpg"
                os.remove(file_name)
                x = x + 1
                
        except TypeError:
            count = False
    remove_user_from_database_window()

def are_you_sure_window_worker_tabel():     #This function creates the window that asks you if your sure you want to clear all the users from the worker table
    def yes_clear_guest_worker_table():     #This function deletes all the elements in the window and then clears the worker table
        yes_button.grid_remove()
        no_button.grid_remove()
        are_you_sure_worker_text.grid_remove()
        delete_all_users_from_worker_table()
        
    def no_go_back():       #This function deltes all the elements in the window and then creates the remove user from datatbase window
        yes_button.grid_remove()
        no_button.grid_remove()
        are_you_sure_worker_text.grid_remove()
        remove_user_from_database_window()
        
    are_you_sure_worker_text = Label(root, text="Are you sure you want to clear the Guest Worker table?", fg="red")
    are_you_sure_worker_text.grid(row=0, column=1, pady=4)
    yes_button = Button(root, text="Yes", command = yes_clear_guest_worker_table)
    yes_button.grid(row=1, column=0, pady=4)
    no_button = Button(root, text="No", command = no_go_back)
    no_button.grid(row=1, column=2, pady=4)

def delete_all_users_from_worker_table():       #This function deletes all the users in the worker table
    count = True

    while count == True:
        try:
            c.execute("SELECT * FROM worker_table")
            data = c.fetchone()
            user_id = data[0]

            c.execute("SELECT * FROM worker_table")
            c.execute("DELETE FROM worker_table WHERE user_id =(?)", (user_id,))
            conn.commit()

            directory = "/home/pi/Desktop/facial_recognition/data_set/"

            user_id_string = str(user_id)

            x = 1

            for i in range (0, 20):     #It does this 20 times as each person has 20 pictures taken of them self
                x_num = str(x)
                file_name = directory+"User."+user_id_string+"."+x_num+".jpg"
                os.remove(file_name)
                x = x + 1

        except TypeError:
            count = False
    remove_user_from_database_window()

def remove_user_from_database_window():     #This function creates the remove user from database window
    def remove_user_by_id():        #This function deletes all the elements in the window and then removes the single user from the user database
        remove_user_by_id_button.grid_remove()
        clear_adult_table_button.grid_remove()
        clear_child_table_button.grid_remove()
        clear_worker_table_button.grid_remove()
        back_button.grid_remove()
        quit_button.grid_remove()
        what_would_you_like_text.grid_remove()
        table_warning_text.grid_remove()
        remove_single_user_window()
    def clear_guest_adult_table():      #This function deletes all the elements in the window and then asks you if your sure you want to clear the guest adult table
        remove_user_by_id_button.grid_remove()
        clear_adult_table_button.grid_remove()
        clear_child_table_button.grid_remove()
        clear_worker_table_button.grid_remove()
        back_button.grid_remove()
        quit_button.grid_remove()
        what_would_you_like_text.grid_remove()
        table_warning_text.grid_remove()
        are_you_sure_window_adult_tabel()
    def clear_guest_child_table():      #This function deletes all the elements in the window and then asks you if your sure you want to clear the guest child table
        remove_user_by_id_button.grid_remove()
        clear_adult_table_button.grid_remove()
        clear_child_table_button.grid_remove()
        clear_worker_table_button.grid_remove()
        back_button.grid_remove()
        quit_button.grid_remove()
        what_would_you_like_text.grid_remove()
        table_warning_text.grid_remove()
        are_you_sure_window_child_tabel()
    def clear_worker_table():       #This function deletes all the elements in the window and then asks you if you want to clear the worker table
        remove_user_by_id_button.grid_remove()
        clear_adult_table_button.grid_remove()
        clear_child_table_button.grid_remove()
        clear_worker_table_button.grid_remove()
        back_button.grid_remove()
        quit_button.grid_remove()
        what_would_you_like_text.grid_remove()
        table_warning_text.grid_remove()
        are_you_sure_window_worker_tabel()
    def go_back():      #This function deletes all the elements in the window and then creates the add user or recognise face window
        remove_user_by_id_button.grid_remove()
        clear_adult_table_button.grid_remove()
        clear_child_table_button.grid_remove()
        clear_worker_table_button.grid_remove()
        back_button.grid_remove()
        quit_button.grid_remove()
        what_would_you_like_text.grid_remove()
        table_warning_text.grid_remove()
        add_user_or_recognise_face()
        
    what_would_you_like_text = Label(root, text="What would you like to do?")
    what_would_you_like_text.grid(row=0, column=1)
    table_warning_text = Label(root, text="WARNING: Clearing a table will cause all \nusers in the table to be deleted", fg="red")
    table_warning_text.grid(row=1, column=1)
    remove_user_by_id_button = Button(root, text="Remove User By ID", command = remove_user_by_id)
    remove_user_by_id_button.grid(row=2, column=1, pady=4)
    clear_adult_table_button = Button(root, text="Clear Guest Adult Table", command = clear_guest_adult_table)
    clear_adult_table_button.grid(row=3, column=1, pady=4)
    clear_child_table_button = Button(root, text="Clear Guest Child Table", command = clear_guest_child_table)
    clear_child_table_button.grid(row=4, column=1, pady=4)
    clear_worker_table_button = Button(root, text="Clear Worker Table", command = clear_worker_table)
    clear_worker_table_button.grid(row=5, column=1, pady=4)
    back_button = Button(root, text="Back", command = go_back)
    back_button.grid(row=6, column=0, pady=4)
    quit_button = Button(root, text="Quit", command = quit_program)
    quit_button.grid(row=6, column=2, pady=4)


def guest_or_worker():      #This will make the window appear where you choose between a guest and a worker
    def go_to_worker_input():       #This function deletes all the elements in the window and creates the worker input form window
        worker_button.grid_remove()
        guest_button.grid_remove()
        back_button.grid_remove()
        quit_button.grid_remove()
        type_of_user_text.grid_remove()
        worker_input_form()
    def go_to_guest_input():        #This function deletes all the elements in the window and creates the guest input form window
        worker_button.grid_remove()
        guest_button.grid_remove()
        back_button.grid_remove()
        quit_button.grid_remove()
        type_of_user_text.grid_remove()
        guest_input_form()
    def go_back():          #This function deletes all the elements in the window and then creates the add user or recognise face window
        worker_button.grid_remove()
        guest_button.grid_remove()
        back_button.grid_remove()
        quit_button.grid_remove()
        type_of_user_text.grid_remove()
        add_user_or_recognise_face()
    type_of_user_text = Label(root, text="What type of user are you adding?")
    type_of_user_text.grid(row=0, column=1)
    worker_button = Button(root, text="Worker", command = go_to_worker_input)
    worker_button.grid(row=1, column=1, pady=4)
    guest_button = Button(root, text="Guest", command = go_to_guest_input)
    guest_button.grid(row=2, column=1, pady=4)
    back_button = Button(root, text="Back", command = go_back)
    back_button.grid(row=3, column=0, pady=4)
    quit_button = Button(root, text="Quit", command = quit_program)
    quit_button.grid(row=3, column=2, pady=4)

def add_user_or_recognise_face():   #This will make the window appear where you choose between adding a user to the database or recognising a face
    def add_user_to_database_button():      #This function deletes all the elements in the window and then creates the guest of worker window
        add_user_to_database_button.grid_remove()
        remove_users_from_database_button.grid_remove()
        recognise_user_button.grid_remove()
        quit_button.grid_remove()
        what_to_do_text.grid_remove()
        guest_or_worker()
    def recognise_user_button():    #This function deletes all the elements in the window and then creates the recognise user window
        add_user_to_database_button.grid_remove()
        remove_users_from_database_button.grid_remove()
        recognise_user_button.grid_remove()
        quit_button.grid_remove()
        what_to_do_text.grid_remove()
        recognise_user_window()
    def remove_users_from_database():       #This function deletes all the elements in the window and then creates the remove user from database window
        add_user_to_database_button.grid_remove()
        remove_users_from_database_button.grid_remove()
        recognise_user_button.grid_remove()
        quit_button.grid_remove()
        what_to_do_text.grid_remove()
        remove_user_from_database_window()

        
    what_to_do_text = Label(root, text="What would you like to do?")
    what_to_do_text.grid(row=0, column=0)
    add_user_to_database_button = Button(root, text="Add User To Database", command = add_user_to_database_button)
    add_user_to_database_button.grid(row=1, column=0, pady=4)
    remove_users_from_database_button = Button(root, text="Remove Users From Database", command = remove_users_from_database)
    remove_users_from_database_button.grid(row=2, column=0, pady=4)
    recognise_user_button = Button(root, text="Recognise User", command = recognise_user_button)
    recognise_user_button.grid(row=3, column=0, pady=4)
    quit_button = Button(root, text="Quit Program", command = quit_program)
    quit_button.grid(row=4, column=0, pady=4)
    
create_worker_table()           #Creates worker table
create_guest_adult_table()      #Creates guest table for the adults
create_guest_child_table()      #Creates guest table for the under 18's
create_temp_table()             #Creates the temporary that is used to bridge all the permanant tables
is_camera_plugged_in()          #Checks that the camera is plugged in

mainloop( )
conn.close()
c.close()
