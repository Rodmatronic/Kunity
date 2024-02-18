import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter import ttk
from tkinter import *
from PIL import Image, ImageTk
from pyopengltk import OpenGLFrame
from OpenGL import GL, GLU
import os
import glob

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
            item_path = os.path.join(node, item)
            if os.path.isdir(item_path):
                populate_tree(tree, item_path, parent=parent_id)
            else:
                with open(item_path, "r") as file:
                    first_line = file.readline().strip()
                    if first_line == "[Kunity object]":
                        second_line = file.readline().strip()
                        if second_line.startswith("[Type: Poly]"):
                            tree.insert(parent_id, "end", text=item, tags=("kasset",))
                        else:
                            tree.insert(parent_id, "end", text=item)
                    else:
                        tree.insert(parent_id, "end", text=item)
    else:
        tree.insert(parent, "end", text=os.path.basename(node))


def compileandrun():
    logwrite("Play")

def stopplay():
    logwrite("Stop")
def Cube():
    # Find all .kasset files in the specified directory
    asset_files = glob.glob("./scene/Assets/*.kasset")
    
    # Iterate over each .kasset file
    for asset_file in asset_files:
        # Initialize lists to store data read from the asset file
        vertices = []
        edges = []
        face_colors = []  # Separate list for face colors
        surfaces = []

        # Read data from the asset file
        with open(asset_file, "r") as file:
            for line in file:
                if line.startswith("Vertices:"):
                    vertices_data = line.split(":")[1].strip().split(",")
                    vertices = [tuple(map(float, vertex.split())) for vertex in vertices_data]
                    print("Vertices:", vertices)  # Print vertices for debugging
                elif line.startswith("Edges:"):
                    edges_data = line.split(":")[1].strip().split(",")
                    edges = [tuple(map(int, edge.split())) for edge in edges_data]
                elif line.startswith("Colors:"):
                    colors_data = line.split(":")[1].strip().split(",")
                    face_colors = [tuple(map(float, color.split())) for color in colors_data]  # Store face colors separately
                elif line.startswith("Surfaces:"):
                    surfaces_data = line.split(":")[1].strip().split(",")
                    surfaces = [tuple(map(int, surface.split())) for surface in surfaces_data]

        # Check if all necessary data has been read
        if not vertices or not edges or not face_colors or not surfaces:
            logwrite(f"Incomplete data in the asset file: {asset_file}")
            continue  # Move to the next asset file
        
        # Render the object using the data from the asset file
        GL.glBegin(GL.GL_QUADS)
        for surface, color in zip(surfaces, face_colors):  # Iterate over surfaces and corresponding colors
            for vertex in surface:
                GL.glColor3fv(color)  # Set color for the current face
                if vertex < len(vertices):
                    GL.glVertex3fv(vertices[vertex])
                else:
                    print(f"Index {vertex} is out of range for vertices list with length {len(vertices)}")
        GL.glEnd()

    # Draw the ground
    render_floor()


def render_floor():
    color = (0.5, 0.5, 0.5)  # Grey
    GL.glColor3fv(color)
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
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_z = -5.0
        self.view_angle_x = 0.0
        self.view_angle_y = 0.0

    def redraw(self):
        GL.glLoadIdentity()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
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
        print("Attempting to create file:", object_name)
        if object_name:
            # Create a new file with the given name and the ".kasset" extension
            with open(f"./scene/Assets/{object_name}.kasset", "w") as file:
                print("Created file:", object_name)
                file.write("[Kunity object]\nObject:")

            # Refresh the file view
            tree.delete(*tree.get_children())
            populate_tree(tree, "./scene")

    def delete_selected():
        # Get selected items from the Treeview
        selected_items = tree.selection()
        for item in selected_items:
            file_name = tree.item(item, "text")
            file_path = os.path.join("./scene/Assets/", file_name)
            print("Attempting to delete file:", file_path)
            try:
                # Remove the file from the file system
                os.remove(file_path)
                # Delete the item from the Treeview
                tree.delete(item)
                print("File deleted successfully.")
            except FileNotFoundError:
                print("File not found:", file_path)

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

    # Add a "Delete" button next to the Treeview
    delete_button = ttk.Button(left_frame, text="Delete", command=delete_selected)
    delete_button.pack(side=tk.LEFT, padx=5, pady=3)

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
