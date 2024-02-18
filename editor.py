import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter import ttk
from tkinter import *
from PIL import Image, ImageTk
from pyopengltk import OpenGLFrame
from OpenGL import GL, GLU
import os

global_ver = "0.1"
global_year = "2024"

# The default object
verticies = ((1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
             (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1))

edges = ((0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7),
         (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7))

root = tk.Tk()
root.geometry("1100x600")
root.title("New Scene - " + "Kunity " + global_year + " " + global_ver)
root.iconbitmap("logo.ico")

try:
    os.remove("Kunity.logfile.txt") 
except:
    print("No previous logfile! Nothing to remove")

def logwrite(log):
    print(log)
    logfile = open("Kunity.logfile.txt", "a")
    logfile.write(log + "\n")
    logfile.close()

def safe_exit():
    logwrite("Exit")
    exit()

logwrite("KUNITY logfile --- \\/\n---------------------")

def populate_tree(tree, node, parent=""):
    if os.path.isdir(node):
        if parent:
            parent_id = tree.insert(parent, "end", text=os.path.basename(node), open=True)
        else:
            parent_id = tree.insert("", "end", text=os.path.basename(node), open=True)
        for item in os.listdir(node):
            populate_tree(tree, os.path.join(node, item), parent=parent_id)
    else:
        tree.insert(parent, "end", text=os.path.basename(node))

def compileandrun():
    logwrite("Play")

def stopplay():
    logwrite("Stop")

def Cube():
    GL.glBegin(GL.GL_LINES)
    for edge in edges:
        for vertex in edge:
            GL.glVertex3fv(verticies[vertex])
    GL.glEnd()

    # Draw the ground
    GL.glBegin(GL.GL_LINES)
    for x in range(-5, 6):
        GL.glVertex3f(x, -1, -5)
        GL.glVertex3f(x, -1, 5)
    for z in range(-5, 6):
        GL.glVertex3f(-5, -1, z)
        GL.glVertex3f(5, -1, z) 
    GL.glEnd()

class editorenv(OpenGLFrame):
    def initgl(self):
        GL.glLoadIdentity()
        GLU.gluPerspective(45, (self.width / self.height), 0.1, 50.0)
        GL.glTranslatef(0.0, 0.0, -5)
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_z = -5.0
        self.view_angle_x = 0.0
        self.view_angle_y = 0.0

    def redraw(self):
        GL.glLoadIdentity()
        GLU.gluPerspective(45, (self.width / self.height), 0.1, 50.0)
        GL.glTranslatef(self.camera_x, self.camera_y, self.camera_z)
        GL.glRotatef(self.view_angle_x, 1, 0, 0)
        GL.glRotatef(self.view_angle_y, 0, 1, 0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        Cube()

    def move_camera(self, direction):
        step = 0.1
        if direction == "up":
            self.camera_y -= step
        elif direction == "down":
            self.camera_y += step
        elif direction == "left":
            self.camera_x -= step
        elif direction == "right":
            self.camera_x += step
        elif direction == "forward":
            self.camera_z += step
        elif direction == "backward":
            self.camera_z -= step
        elif direction == "sideways_left":
            self.camera_x -= step
        elif direction == "sideways_right":
            self.camera_x += step

    def rotate_camera(self, direction):
        angle_step = 1.0
        if direction == "left_arrow":
            self.view_angle_y += angle_step
        elif direction == "right_arrow":
            self.view_angle_y -= angle_step
        elif direction == "up_arrow":
            self.view_angle_x += angle_step
        elif direction == "down_arrow":
            self.view_angle_x -= angle_step


def main():
    key_pressed = {}

    def on_key(event):
        if event.keysym not in key_pressed or not key_pressed[event.keysym]:
            key_pressed[event.keysym] = True
            move_camera(event.keysym)

    def on_key_release(event):
        key_pressed[event.keysym] = False

    def move_camera(direction):
        step = 0.01
        if direction == "w":
            frm.move_camera("forward")
        elif direction == "s":
            frm.move_camera("backward")
        elif direction == "a":
            frm.move_camera("sideways_right")
        elif direction == "d":
            frm.move_camera("sideways_left")
        elif direction == "Right":
            frm.rotate_camera("left_arrow")
        elif direction == "Left":
            frm.rotate_camera("right_arrow")
        elif direction == "Up":
            frm.rotate_camera("up_arrow")
        elif direction == "Down":
            frm.rotate_camera("down_arrow")
        
        if key_pressed.get(direction):
            root.after(15, lambda: move_camera(direction))

    root.bind("<KeyPress>", on_key)
    root.bind("<KeyRelease>", on_key_release)

    def donothing():
        print("Placeholder")

    def open_about():
        logwrite("About menu open")
        top = Toplevel(root)
        top.geometry("550x450")
        top.title("About Kunity")
        top.configure(bg="#333")
        top.resizable(False, False)  # Making the window unresizable

        # Setting the window as a tool window
        if os.name == 'nt':  # Check if the operating system is Windows
            top.wm_attributes("-toolwindow", 1)

        # Load the about image
        image = PhotoImage(file="./images/kunity.logo.png")
        image_label = Label(top, image=image, bg="#333")
        image_label.image = image  # Keep a reference to the image to prevent it from being garbage collected
        image_label.place(x=20, y=20)

        # Load the python image
        pyimage = PhotoImage(file="./images/python.logo.png")
        image_label = Label(top, image=pyimage, bg="#333")
        image_label.image = pyimage  # Keep a reference to the image to prevent it from being garbage collected
        image_label.place(x=50, y=240)

        # Load the python image
        openglimage = PhotoImage(file="./images/opengl.logo.png")
        image_label = Label(top, image=openglimage, bg="#333")
        image_label.image = openglimage  # Keep a reference to the image to prevent it from being garbage collected
        image_label.place(x=180, y=240)

        Label(top, text="Powered by:", bg="#333", fg="White",font=('Mistral 10 bold')).place(x=42, y=180)


        Label(top, text="Ver " + global_ver + " " + global_year, bg="#333", fg="White",font=('Mistral 10 bold')).place(x=22, y=145)

    def create_kasset():
        # Get the name of the new object
        object_name = new_object_entry.get()

        # Check if the name is not empty
        if object_name:
            # Create a new file with the given name and the ".kasset" extension
            with open(f"./scene/Assets/{object_name}.kasset", "w") as file:
                file.write("[Kunity object]\nObject:")

            # Refresh the file view
            tree.delete(*tree.get_children())
            populate_tree(tree, "./scene")

    # Set dark mode theme
    style = ttk.Style()
    style.theme_use('clam')  # Use 'clam' theme as it's closer to dark mode
    style.configure("TFrame", background="#333")
    style.configure(".", background="#333", foreground="#ddd")  # Default background and foreground colors
    style.configure(".", bordercolor="#666")  # Default border color for all widgets

    # Configure style for Treeview
    style.configure("Treeview", background="#333", foreground="#ddd", fieldbackground="#333", bordercolor="#666")
    style.map("Treeview", background=[('selected', '#2c5d87')])

    # Configure style for buttons
    style.configure("TButton", background="#383838", foreground="white", bordercolor="#666")  # Normal state: light grey background, white text
    style.map("TButton", background=[('active', '#ddd')])  # Hover state: slightly lighter grey background
    style.map("TButton", background=[('pressed', '#000')])  # Pressed state: dark grey background
    style.map("TEntry", foreground="White", background="#333")  # Pressed state: dark grey background

    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=donothing)
    filemenu.add_command(label="Open", command=donothing)
    filemenu.add_command(label="Save", command=donothing)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=safe_exit)
    menubar.add_cascade(label="File", menu=filemenu)

    editmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=editmenu)

    preferencesmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Preferences", menu=preferencesmenu)

    windowmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Window", menu=windowmenu)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About...", command=open_about)
    menubar.add_cascade(label="Help", menu=helpmenu)

    root.config(menu=menubar)

    # Create a Frame for the second bar
    top_bar_frame = ttk.Frame(root)
    top_bar_frame.pack(fill=tk.X)

    play_button = ttk.Button(top_bar_frame, text="Play", command=compileandrun, width=5)
    play_button.config(padding=(5, 2))  # Adjust the padding to make the button less tall
    play_button.pack(side=tk.LEFT, pady=3)

    pause_button = ttk.Button(top_bar_frame, text="Pause", command=compileandrun, width=5)
    pause_button.config(padding=(5, 2))  # Adjust the padding to make the button less tall
    pause_button.pack(side=tk.LEFT, pady=3)

    stop_button = ttk.Button(top_bar_frame, text="Stop", command=stopplay, width=5)
    stop_button.config(padding=(5, 2))  # Adjust the padding to make the button less tall
    stop_button.pack(side=tk.LEFT, pady=3)

    paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    left_frame = ttk.Frame(paned_window, relief="flat", width=400, height=500)
    editor = ttk.Frame(paned_window, width=400, height=600)
    paned_window.add(left_frame)
    paned_window.add(editor)
    paned_window.pack(fill=tk.BOTH, expand=True)

    # Add a label at the top of the left_frame
    hierarchy_label = ttk.Label(left_frame, text="Hierarchy", background="#333", foreground="#FFFFFF")
    hierarchy_label.pack(padx=5, pady=2, side= TOP, anchor="w")

    # Create a Treeview widget
    tree = ttk.Treeview(left_frame)
    tree.pack(fill='both', expand=True)
    populate_tree(tree, "./scene")

    frm = editorenv(master=editor, height=600, width=400)
    frm.animate = 10
    frm.pack(fill=tk.BOTH, expand=True)

    # Add a "+" button to create a new ".kasset" object
    create_button = ttk.Button(left_frame, text="+", command=create_kasset)
    create_button.pack(side=tk.RIGHT, padx=5, pady=3)

    # Add an entry field to enter the name of the new object
    new_object_entry = ttk.Entry(left_frame)
    new_object_entry.pack(side=tk.RIGHT, padx=5, pady=3)
    new_object_entry.insert(0, "NewObject")

    root.bind("<Key>", on_key)
    return root.mainloop()

if __name__ == "__main__":
    main()
