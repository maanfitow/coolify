# This code streams on a tkinter window the video from the OAK-D camera.

import depthai as dai
import cv2 as cv
import tkinter as tk
import PIL.Image, PIL.ImageTk
from tkinter import ttk
import customtkinter as ctk
import subprocess
import datetime
import os
import sqlite3
import datetime
import sqlite3
import datetime
import random

last_id = 0
ph_on_stage = False

class NumberEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(validate="key")
        self.configure(validatecommand=(self.register(self.validate_input), "%P"))

    def validate_input(self, new_value):
        if new_value == "":
            return True
        try:
            float(new_value)
            return True
        except ValueError:
            return False

def open_db_window():
    subprocess.Popen(["python", "pyqlite.py"])
    
def clear_all_entries():
    heiEnt.delete(0, "end")
    widEnt.delete(0, "end")
    volEnt.delete(0, "end")
    
    # Disable the saveBtn button
    saveBtn.config(state="disabled")
    
def capture():
    # This function takes a photo and shows it in a pop-up window with two options: save or discard.
    # If the user chooses to save the photo, the photo is saved in "C:\Users\Mauricio\Desktop\Jetson\RDMO-Mobile\Interface\RGB" with the name "photo_{date}_{hour}.jpg".
    # If the user chooses to discard the photo, the photo is deleted.
    global last_id
    global ph_on_stage
    
    if ph_on_stage:
        # Delete the previous photos
        os.remove(f"..//RGB/rgb_{last_id}.png")
        os.remove(f"..//MLeft/lef_{last_id}.png")
        os.remove(f"..//MRight/rig_{last_id}.png")
    
    last_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    photo_name = f"rgb_{last_id}.png"
    left_photo_name = f"lef_{last_id}.png"
    right_photo_name = f"rig_{last_id}.png"
    photo_path = "..//RGB/"
    left_photo_path = "..//MLeft/"
    right_photo_path = "..//MRight/"
    
    # Take the photos
    frame = qRgb.get()
    left_frame = qLeft.get()
    right_frame = qRight.get()
    photo = frame.getCvFrame()
    left_photo = left_frame.getCvFrame()
    right_photo = right_frame.getCvFrame()

    # Save the photos in the specified folders
    cv.imwrite(f"{photo_path}/{photo_name}", photo)
    cv.imwrite(f"{left_photo_path}/{left_photo_name}", left_photo)
    cv.imwrite(f"{right_photo_path}/{right_photo_name}", right_photo)

    # Show the photo in a pop-up window
    popup = tk.Toplevel()
    popup.title("Photo")

    # Load the photo into a PIL.Image object
    image = PIL.Image.fromarray(cv.cvtColor(photo, cv.COLOR_BGR2RGB))

    # Create a PhotoImage object from the PIL.Image object
    photo_image = PIL.ImageTk.PhotoImage(image=image)

    # Display the photo in a ttk.Label object
    photo_label = ttk.Label(popup, image=photo_image)
    photo_label.image = photo_image  # Store a reference to prevent garbage collection
    photo_label.pack()
    
    # Function to save the photos
    def save_photos():
        global ph_on_stage
        # Save the photos in the specified folders
        cv.imwrite(f"{photo_path}/{photo_name}", photo)
        cv.imwrite(f"{left_photo_path}/{left_photo_name}", left_photo)
        cv.imwrite(f"{right_photo_path}/{right_photo_name}", right_photo)
        # Enable the saveBtn button
        saveBtn.config(state="normal")
        ph_on_stage = True
        popup.destroy()

    # Function to discard the photos
    def discard_photos():
        global ph_on_stage
        # Delete the photos
        os.remove(f"{photo_path}/{photo_name}")
        os.remove(f"{left_photo_path}/{left_photo_name}")
        os.remove(f"{right_photo_path}/{right_photo_name}")
        ph_on_stage = False
        popup.destroy()

    # Button to save the photo
    save_button = ttk.Button(popup, text="Save", command=save_photos)
    save_button.pack(side="left", padx=10, pady=10)

    # Button to discard the photo
    discard_button = ttk.Button(popup, text="Discard", command=discard_photos)
    discard_button.pack(side="right", padx=10, pady=10)

def save_changes():
    
    # Connect to the database
    conn = sqlite3.connect('RDMO.db')
    cursor = conn.cursor()
    
    # Get the current date and time
    global last_id
    global ph_on_stage

    # Save the values to the database
    id = last_id
    latitude = round(random.uniform(-100.000, 100.000), 3)
    longitude = round(random.uniform(-100.000, 100.000), 3)
    rgb_ph = "../RGB/rgb_" + str(id) + ".png"
    left_ph = "../MLeft/lef_" + str(id) + ".png"
    right_ph = "../MRight/rig_" + str(id) + ".png"
    volume = volEnt.get()
    width = widEnt.get()
    height = heiEnt.get()
    water = int(watRb.get() == "Yes")

    # Insert the values into the table
    cursor.execute("INSERT INTO Pothole (id, latitude, longitude, rgb_ph, left_ph, right_ph, volume, width, height, water) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (id, latitude, longitude, rgb_ph, left_ph, right_ph, volume, width, height, water))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    ph_on_stage = False
    clear_all_entries()

# Create pipeline

pipeline = dai.Pipeline()

# Define sources and outputs

RgbCam = pipeline.createColorCamera()
RgbCam.setPreviewSize(600, 480)
RgbCam.setInterleaved(False)
RgbCam.setBoardSocket(dai.CameraBoardSocket.CAM_A)

LeftCam = pipeline.createMonoCamera()
LeftCam.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
LeftCam.setBoardSocket(dai.CameraBoardSocket.CAM_B)

RightCam = pipeline.createMonoCamera()
RightCam.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
RightCam.setBoardSocket(dai.CameraBoardSocket.CAM_C)

# Create outputs

RgbOutput = pipeline.createXLinkOut()
RgbOutput.setStreamName("rgb")
RgbCam.preview.link(RgbOutput.input)

LeftOutput = pipeline.createXLinkOut()
LeftOutput.setStreamName("left")
LeftCam.out.link(LeftOutput.input)

RightOutput = pipeline.createXLinkOut()
RightOutput.setStreamName("right")
RightCam.out.link(RightOutput.input)

# Create and start the pipeline

with dai.Device(pipeline) as device:
    # Output queues will be used to get the rgb frames from the output defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    qLeft = device.getOutputQueue(name="left", maxSize=4, blocking=False)
    qRight = device.getOutputQueue(name="right", maxSize=4, blocking=False)

    # Create a tkinter window
    root = tk.Tk()
    #root.attributes("-fullscreen", True)
    
    style = ttk.Style(root)
    root.tk.call("source", "forest-dark.tcl")
    style.theme_use("forest-dark")
    root.title("OAK-D RGB Camera")
    
    # Create a frame
    
    app = ttk.Frame(root)
    app.pack()
    
    # Create a frame for the widgets
    
    widg = ttk.LabelFrame(app)
    widg.grid(row=0, column=0)
    
    title = tk.PhotoImage(file=r"C:\Users\Mauricio\Desktop\Jetson\RDMO-Mobile\Interface\Tkinter\logo16_9.png")
    titleLbl = ttk.Label(widg, image=title)
    titleLbl.grid(row=0, column=0, columnspan=3, pady=10)
    
    # Height
    
    lbl0 = ttk.Label(widg, text="Height")
    lbl0.grid(row=1, column=0)
    
    heiEnt = NumberEntry(widg)
    heiEnt.grid(row=1, column=1, pady=10)
    
    heiEnt.insert(0, "Intert the Height")
    heiEnt.bind("<FocusIn>", lambda e: heiEnt.delete('0', 'end'))
    
    # Width
    
    lbl1 = ttk.Label(widg, text="Width")
    lbl1.grid(row=2, column=0)
    
    widEnt = NumberEntry(widg)
    widEnt.grid(row=2, column=1, pady=10)
    
    widEnt.insert(0, "Intert the Width")
    widEnt.bind("<FocusIn>", lambda e: widEnt.delete('0', 'end'))
    
    # Volume
    
    lbl2 = ttk.Label(widg, text="Volume")
    lbl2.grid(row=3, column=0)
    
    volEnt = NumberEntry(widg)
    volEnt.grid(row=3, column=1, pady=10)
    
    volEnt.insert(0, "Intert the Volume")
    volEnt.bind("<FocusIn>", lambda e: volEnt.delete('0', 'end'))
    
    # Water
    # This is a group of two radiobuttons with yes and no options separated by a "/"
    
    lbl3 = ttk.Label(widg, text="Water")
    lbl3.grid(row=4, column=0)
    
    # Create a frame for the radio buttons
    
    radioFrame = ttk.LabelFrame(widg)
    radioFrame.grid(row=4, column=1, pady=5)

    # This is a group of two radiobuttons with yes and no options separated by a "/"
    
    watRb = tk.StringVar()
    watRb.set("Yes/No")
    watRb1 = ttk.Radiobutton(radioFrame, text="Yes", variable=watRb, value="Yes/No")
    watRb1.grid(row=0, column=0)
    slashLbl = ttk.Label(radioFrame, text="/")
    slashLbl.grid(row=0, column=1, padx=5)
    watRb2 = ttk.Radiobutton(radioFrame, text="No", variable=watRb, value="No/Yes")
    watRb2.grid(row=0, column=2)
    
    # Capture
    
    capBtn = ttk.Button(widg, text="Capture", width=10, command=capture)
    capBtn.grid(row=5, column=0, pady=10, padx=10)
    
    # Clear All
    
    clrBtn = ttk.Button(widg, text="Clear All", command=clear_all_entries)
    clrBtn.grid(row=5, column=1, padx=10, pady=10)
    
    # Save
    
    # Create the button using the custom style
    # Create a custom style for the button
    
    saveBtn = ttk.Button(widg, text="Save", width=10, state="disabled")
    saveBtn.grid(row=5, column=2, pady=10, padx=10)
    saveBtn.configure(command=save_changes)
    
    # Right Frame
    
    rigF = ttk.LabelFrame(app)
    rigF.grid(row=0, column=1)
    
    # Windows Frame
    
    winF = ttk.LabelFrame(rigF)
    winF.grid(row=0, column=0)
    
    # Form window
    
    formBtn = ttk.Button(winF, text="Form")
    formBtn.grid(row=0, column=0, padx=50, pady=10)
    
    # Database window
    
    dbBtn = ttk.Button(winF, text="Database", command=open_db_window)
    dbBtn.grid(row=0, column=1, pady=10)
    
    # Detection window
    
    detBtn = ttk.Button(winF, text="Detection")
    detBtn.grid(row=0, column=2, padx=50, pady=10)
    
    # Create a label in the frame for the video
    
    lmain = ttk.Label(rigF)
    lmain.grid(row=1, column=0, padx=10, pady=10)
    
    # Function for video streaming
    
    def video_stream():
        try:
            
            inRgb = qRgb.get()
            cvimage = cv.cvtColor(inRgb.getCvFrame(), cv.COLOR_BGR2RGBA)
            
            img = PIL.Image.fromarray(cvimage)
            imgtk = PIL.ImageTk.PhotoImage(image=img)
            
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
            lmain.after(1, video_stream)
            
        except:
            
            lmain.after(1, video_stream)
            
    # Call the function to start video streaming
    
    video_stream()
    
    # Start the mainloop
    
    root.mainloop()
