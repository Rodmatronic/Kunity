import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter import ttk
from tkinter import *
from PIL import Image, ImageTk
from pyopengltk import OpenGLFrame
from OpenGL import GL, GLU
import os
import glob

# Some global configurations

global_ver = "0.12"
global_year = "2024"
global_scene_noshade_brightness = 3.0, 3.0, 3.0

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

def RenderAll():
    # Find all .kasset files in the specified directory
    asset_files = glob.glob("./scene/Assets/*.kasset")
    
    renderXYdepth()

    # Iterate over each .kasset file
    for asset_file in asset_files:
        # Initialize lists to store data read from the asset file
        vertices = []
        edges = []
        face_colors = []  # Separate list for face colors
        surfaces = []
        image_path = None  # Initialize image path variable

        # Read data from the asset file
        with open(asset_file, "r") as file:
            for line in file:
                if line.startswith("Vertices:"):
                    vertices_data = line.split(":")[1].strip().split(",")
                    vertices = [tuple(map(float, vertex.split())) for vertex in vertices_data]
                elif line.startswith("Edges:"):
                    edges_data = line.split(":")[1].strip().split(",")
                    edges = [tuple(map(int, edge.split())) for edge in edges_data]
                elif line.startswith("Colors:"):
                    colors_data = line.split(":")[1].strip().split(",")
                    face_colors = [tuple(map(float, color.split())) for color in colors_data]  # Store face colors separately
                elif line.startswith("Surfaces:"):
                    surfaces_data = line.split(":")[1].strip().split(",")
                    surfaces = [tuple(map(int, surface.split())) for surface in surfaces_data]
                elif line.startswith("Image:"):  # Check for image path flag
                    image_path = line.split(":")[1].strip()  # Extract image path

        # Check if all necessary data has been read
        if not vertices or not edges:
            logwrite(f"Incomplete data in the asset file: {asset_file}")
            continue  # Move to the next asset file
        
        # If image path is specified, draw textured quads
        if image_path:
            # Load the texture
            texture_id = load_texture(image_path)
            # Draw textured quad for each surface
            for surface in surfaces:
                draw_textured_quad(texture_id, vertices, surface)
        else:
            GL.glBegin(GL.GL_QUADS)
            for surface, color in zip(surfaces, face_colors): 
                for vertex in surface:
                    GL.glColor3fv(color)
                    if vertex < len(vertices):
                        GL.glVertex3fv(vertices[vertex])
                    else:
                        print(f"Index {vertex} is out of range for vertices list with length {len(vertices)}")
            
            GL.glEnd()

def draw_textured_quad(texture_id, vertices, surface):
    # Bind the texture
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    # Start drawing quads
    GL.glBegin(GL.GL_QUADS)
    # Loop through each vertex in the surface
    for vertex in surface:
        # Get the texture coordinates based on vertex index
        tex_coords = (0.0, 0.0)
        if vertex == 0:
            tex_coords = (0.0, 1.0)
        elif vertex == 1:
            tex_coords = (1.0, 1.0)
        elif vertex == 2:
            tex_coords = (1.0, 0.0)
        elif vertex == 3:
            tex_coords = (0.0, 0.0)
        # Set the texture coordinates and vertex position
        GL.glTexCoord2f(tex_coords[0], tex_coords[1])
        GL.glVertex3fv(vertices[vertex])
    # End drawing quads
    GL.glEnd()

def renderXYdepth():

    color = (3.0, 3.0, 3.0)

    GL.glColor3fv(color)
    GL.glBegin(GL.GL_LINES)
    for x in range(-5, 6):
        GL.glVertex3f(x, -1, -5)
        GL.glVertex3f(x, -1, 5)
    for z in range(-5, 6):
        GL.glVertex3f(-5, -1, z)
        GL.glVertex3f(5, -1, z)
    GL.glEnd()

def load_texture(texture_path):
    try:
        texture_image = Image.open(texture_path)
    except IOError as ex:
        print("Failed to open texture file:", texture_path)
        return None
    
    texture_data = texture_image.tobytes("raw", "RGBA", 0, -1)
    texture_width, texture_height = texture_image.size
    texture_image.close()
    
    texture_id = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, texture_width, texture_height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, texture_data)
    
    return texture_id

class editorenv(OpenGLFrame):
    def initgl(self):
        GL.glLoadIdentity()
        GLU.gluPerspective(45, (self.width / self.height), 0.1, 50.0)
        GL.glTranslatef(0.0, 0.0, -5)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_TEXTURE_2D)  # Enable 2D texturing
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
        RenderAll()

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
        step = 0.0001
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
            root.after(3, lambda: move_camera(direction))

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
                file.write("[Kunity object]\nVertices:\nEdges:\nColors:\nSurfaces:")
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
    style.configure(".", background="#484848", foreground="#ddd", bordercolor="000", font="Calibri")  # Default background and foreground colors
    style.configure("TEntry", foreground="White", background="#FFF", fieldbackground="#FFF", bordercolor="#222")  

    # Configure style for Treeview
    style.configure("Treeview", background="#333", foreground="#ddd", fieldbackground="#333")
    style.map("Treeview", background=[('selected', '#2c5d87')])

    # Configure style for buttons
    style.map("TButton", background=[('active', '#ddd')])  # Hover state: slightly lighter grey background
    style.map("TButton", background=[('pressed', '#222')])  # Pressed state: dark grey background
    style.map("TEntry", foreground="White", background="#333")  # Pressed state: dark grey background

    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New Scene", command=donothing)
    filemenu.add_command(label="Open Scene", command=donothing)
    filemenu.add_command(label="Open Recent >", command=donothing)
    filemenu.add_separator()
    filemenu.add_command(label="Save", command=donothing)
    filemenu.add_command(label="Save as...", command=donothing)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=safe_exit)

    menubar.add_cascade(label="File", menu=filemenu)

    editmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=editmenu)
    editmenu.add_command(label="Undo", command=donothing)
    editmenu.add_command(label="Redo", command=donothing)
    editmenu.add_separator()
    editmenu.add_command(label="Cut", command=donothing)
    editmenu.add_command(label="Copy", command=donothing)
    editmenu.add_command(label="Paste", command=donothing)
    editmenu.add_separator()
    editmenu.add_command(label="Rename", command=donothing)

    preferencesmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Preferences", menu=preferencesmenu)

    windowmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Window", menu=windowmenu)

    windowmenu.add_command(label="Default", command=lambda: root.state("normal"))
    windowmenu.add_command(label="Minimize", command=lambda: root.state("iconic"))
    windowmenu.add_command(label="Maximize", command=lambda: root.state("zoomed"))
    windowmenu.add_separator()
    windowmenu.add_command(label="Close", command=safe_exit)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About...", command=open_about)
    menubar.add_cascade(label="Help", menu=helpmenu)

    root.config(menu=menubar)

    # Create a Frame for the second bar
    top_bar_frame = ttk.Frame(root)
    top_bar_frame.pack(fill=tk.X)

    # Load the images
    play_image = Image.open("./images/icons/play.png")
    pause_image = Image.open("./images/icons/pause.png")
    stop_image = Image.open("./images/icons/stop.png")

    play_image = play_image.resize((25, 25), Image.Resampling.LANCZOS)
    pause_image = pause_image.resize((25, 25), Image.Resampling.LANCZOS)
    stop_image = stop_image.resize((25, 25), Image.Resampling.LANCZOS)

    # Convert PIL images to Tkinter PhotoImage objects
    play_photo = ImageTk.PhotoImage(play_image)
    pause_photo = ImageTk.PhotoImage(pause_image)
    stop_photo = ImageTk.PhotoImage(stop_image)

    # Update button creation with images
    play_button = ttk.Button(top_bar_frame, image=play_photo, command=compileandrun)
    pause_button = ttk.Button(top_bar_frame, image=pause_photo, command=compileandrun)
    stop_button = ttk.Button(top_bar_frame, image=stop_photo, command=stopplay)

    # Pack buttons
    play_button.pack(side=tk.LEFT, pady=3, padx=6)
    pause_button.pack(side=tk.LEFT, pady=3, padx=6)
    stop_button.pack(side=tk.LEFT, pady=3, padx=6)

    # Toolbar
    toolbar = ttk.Frame(root, relief="flat", height=20, style="Toolbar.TFrame")
    toolbar.pack(side=tk.TOP, fill=tk.X)

    style.configure("Toolbar.TFrame", background="#222")

    paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    left_frame = ttk.Frame(paned_window, relief="flat", width=400, height=500)
    editor = ttk.Frame(paned_window, width=400, height=600)
    paned_window.add(left_frame)
    paned_window.add(editor)
    paned_window.pack(fill=tk.BOTH, expand=True)

    # Add a label at the top of the left_frame
    hierarchy_label = ttk.Label(toolbar, width=17, text="    Hierarchy", background="#484848", foreground="#FFFFFF")
    hierarchy_label.pack(padx=8, pady=0, side= TOP, anchor="w")

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
    new_object_entry = ttk.Entry(left_frame, font=("Calibri", 8))  # Set font to Consolas and increase font size
    new_object_entry.pack(side=tk.RIGHT, padx=5, pady=3, fill=tk.X, expand=True)  # Make the entry field fill the available space horizontally
    new_object_entry.insert(0, "NewObject")

    root.bind("<Key>", on_key)
    return root.mainloop()

if __name__ == "__main__":
    main()
