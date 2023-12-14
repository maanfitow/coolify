import tkinter as tk
from tkinter import ttk
import sqlite3 as sql
import os
from tkinter import messagebox
from PIL import Image, ImageTk

index = 0

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

'''
Functions
'''

# This function opens a new window with the photos of the selected row
# The photos are diaplayed in a canvas with two buttons: next and previous
# The photos are displayed in the order: rgb, left, right
# The photos are displayed in the size 640x480
# The photos have their location in the 2nd, 3rd and 4th column of the selected row
def openImages():
    global index
    index = 0
    # This function displays the next photo
    def nextImage():
        # Increment the index by 1
        global index
        index
        index += 1
        # If the index exceeds the last index, wrap around to the first index
        if index >= 3:
            index = 0
        # Update the image_path variable with the new image path
        image_path = image_paths[index]
        # Display the photo
        displayImage(image_path)
        print(index)
        print(image_path)
    
    # This function displays the photo with the specified path
    def displayImage(image_path):
        global index
        index
        # Delete the existing image
        canvas.delete("all")
        # Load the image into a PIL.Image object
        try:
            image = Image.open(image_path)
        except FileNotFoundError:
            canvas.create_text(320, 240, text="Image not found")
            return
        # Resize the image to 640x480
        image = image.resize((640, 480))
        # Create a PhotoImage object from the PIL.Image object
        photo_image = ImageTk.PhotoImage(image=image)
        # Display the image in the canvas
        canvas.create_image(0, 0, image=photo_image, anchor="nw")
        # Store a reference to prevent garbage collection
        canvas.image = photo_image
        # Display the label of the image
        if index == 0:
            canvas.create_rectangle(0, 0, 640, 40, fill="black")
            canvas.create_text(320, 20, text="RGB", font=("TkDefaultFont", 16), fill="white")
        elif index == 1:
            canvas.create_rectangle(0, 0, 640, 40, fill="black")
            canvas.create_text(320, 20, text="Left", font=("TkDefaultFont", 16), fill="white")
        elif index == 2:
            canvas.create_rectangle(0, 0, 640, 40, fill="black")
            canvas.create_text(320, 20, text="Right", font=("TkDefaultFont", 16), fill="white")
    
    def previousImage():
        # Get the current photo index
        global index
        index
        # Decrement the index by 1
        index -= 1
        # If the index is less than 0, wrap around to the last index
        if index < 0:
            index = 2
        # Update the image_path variable with the new image path
        image_path = image_paths[index]
        # Display the photo
        displayImage(image_path)
        print(index)
        print(image_path)
    
    selected = tree.focus()
    values = tree.item(selected, "values")
    image_paths = [path.replace('/', '//') for path in values[1:4]]
    print(image_paths)
    
    # Create a new window for the photos
    images_window = tk.Toplevel(root)
    images_window.title("Images")
    
    # Create a canvas to display the photos
    canvas = tk.Canvas(images_window, width=640, height=480)
    canvas.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    
    # Create the next button
    next_button = ttk.Button(images_window, text="Next", command=nextImage)
    next_button.grid(row=1, column=1, padx=10, pady=10)
    
    # Create the previous button
    previous_button = ttk.Button(images_window, text="Previous", command=previousImage)
    previous_button.grid(row=1, column=0, padx=10, pady=10)
    
    # Display the first photo
    image_path = image_paths[0]
    displayImage(image_path)
    
    # Loop the window
    images_window.mainloop()

# This function refreshes the data in the treeview
def refreshDb():
    # Clear the existing items in the treeview
    tree.delete(*tree.get_children())
    # Fetch the updated data from the database
    cursor.execute("SELECT * FROM Pothole")
    data = cursor.fetchall()
    # Insert the updated data rows
    for row in data:
        tree.insert("", "end", values=row)

# This function deletes the selected row
def delRow():
    # Get the selected row
    selected = tree.focus()
    # Get the values of the selected row
    values = tree.item(selected, "values")
    # Get the id of the selected row
    id = values[0]
    
    # Ask if the user is sure to delete the item with id
    if messagebox.askyesno("Delete item", "Are you sure you want to delete the row and photos with ID:" + str(id) + "?"):
        rgb_path = "..//RGB/rgb_" + str(id) + ".png"
        
        # Delete the photo if it exists
        if os.path.exists(rgb_path):
            os.remove(rgb_path)
        
        # Delete the row from the database
        cursor.execute("DELETE FROM Pothole WHERE id=?", (id,))
        # Commit the changes
        conn.commit()
        # Delete the row from the treeview
        tree.delete(selected)

# This function edits the selected row displaying the data in a new window and showing two buttons to save or cancel the changes
def editRow():
    # Get the selected row
    selected = tree.focus()
    # Get the values of the selected row
    values = tree.item(selected, "values")
    # Get the id of the selected row
    id = values[0]

    # Create a new window for editing
    edit_window = tk.Toplevel(root)

    # Create labels and entry fields for each column
    labels = []
    entries = []
    for i, column in enumerate(tree["columns"]):
        label = ttk.Label(edit_window, text=column)
        label.grid(row=i, column=0, padx=5, pady=5)
        if column in ["ID", "Latitude", "Longitude", "Volume", "Width", "Height", "Water"]:
            # Create a NumberEntry for the specified columns
            entry = NumberEntry(edit_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, values[i])
            entries.append(entry)
        else:
            entry = ttk.Entry(edit_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, values[i])
            entries.append(entry)
        labels.append(label)

    # Save changes function
    def saveChanges():
        # Get the updated values from the entry fields
        updated_values = [entry.get() if isinstance(entry, ttk.Entry) else entry.get() for entry in entries]
        # Update the row in the database
        cursor.execute("UPDATE Pothole SET rgb_ph=?, left_ph=?, right_ph=?, latitude=?, longitude=?, volume=?, width=?, height=?, water=? WHERE id=?", (*updated_values[1:], id))
        # Commit the changes
        conn.commit()
        refreshDb()
        # Close the edit window
        edit_window.destroy()

    # Cancel changes function
    def cancelChanges():
        # Close the edit window without saving changes
        edit_window.destroy()

    # Create save and cancel buttons
    save_button = ttk.Button(edit_window, text="Save", command=saveChanges)
    save_button.grid(row=len(tree["columns"]), column=0, padx=10, pady=10)

    cancel_button = ttk.Button(edit_window, text="Cancel", command=cancelChanges)
    cancel_button.grid(row=len(tree["columns"]), column=1, padx=10, pady=10)

root = tk.Tk()
style = ttk.Style(root)
root.tk.call("source", "forest-dark.tcl")
style.theme_use("forest-dark")

'''
Control panel to manage the data
'''

# Control panel
panel = ttk.LabelFrame(root)
panel.grid(row=0, column=0)

# Refresh button
refreshBtn = ttk.Button(panel, text="Refresh")
refreshBtn.grid(row=0, column=0, padx=20, pady=10)
refreshBtn.configure(command=refreshDb)

# Delete row button
delBtn = ttk.Button(panel, text="Delete row")
delBtn.grid(row=0, column=1, padx=20, pady=10)
delBtn.configure(command=delRow)

# Edit row button
# This button will open a new window with the data of the selected row
editBtn = ttk.Button(panel, text="Edit row")
editBtn.grid(row=0, column=2, padx=20, pady=10)
editBtn.configure(command=editRow)

# Show images button
imagesBtn = ttk.Button(panel, text="Show images")
imagesBtn.grid(row=0, column=3, padx=20, pady=10)
imagesBtn.configure(command=openImages)

'''
Visualize the data in a table
'''

tree = ttk.Treeview(root)
tree.grid(row=1, column=0, padx=10, pady=10)

# Create a vertical scrollbar
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
# Configure the treeview to use the scrollbar
tree.configure(yscrollcommand=scrollbar.set)
# Place the scrollbar on the right side of the treeview
scrollbar.grid(row=1, column=1, padx=(0,10), sticky="ns")

conn = sql.connect('RDMO.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM Pothole")

# After executing the SELECT statement and fetching the data
data = cursor.fetchall()

# Clear any existing items in the treeview
tree.delete(*tree.get_children())

# Insert the column headers
tree["columns"] = ("ID", "RGB", "Left", "Right", "Latitude", "Longitude", "Volume", "Width", "Height", "Water")

for column in tree["columns"]:
    tree.heading(column, text=column)
    tree.column(column, width=70, anchor="center")

# Insert the data rows
for row in data:
    tree.insert("", "end", values=row)

# Remove the blank column at the beginning
tree["show"] = "headings"

root.mainloop()