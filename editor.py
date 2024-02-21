import tkinter as tk
import tkinter.filedialog as filedialog #not used
from tkinter import ttk
from tkinter import *
from tkinter import messagebox 
from PIL import Image, ImageTk
from pyopengltk import OpenGLFrame
from OpenGL import GL, GLU
import os
import glob
import gc
import platform
import shutil #not used

# Some global configurations
global_ver = "0.14"
global_year = "2024"
global_scene_noshade_brightness = 3.0, 3.0, 3.0
global campos
global camrot
global camid
iscompile = 0
camcount = 2 # 1 should be reserved
#campos = None
#camrot = None 
#camid = None
root = tk.Tk()
root.geometry("1100x600")
root.title("New Scene - " + "Kunity " + global_year + " " + global_ver + " (Python version " + platform.python_version() + ")")
# root.iconbitmap("logo.ico")

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
def cut():
    pass
def copy():
    pass
def paste():
    pass
def rename():
    pass
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
def undo():
    pass
def redo():
    pass
def compileandrun():
    global campos
    global frm
    global camrot
    global camid
    global iscompile
    iscompile = 1
    logwrite("Play")
    try:
        print(campos)
        print(camrot)
        print(camid)
       
        frm.setpos(campos[0],campos[1],campos[2],camrot[0],camrot[1])
    except OSError as err:
        logwrite(err)
        messagebox.showinfo("showerror", "No Valid Camera in Scene") 
        logwrite("error(!): No Valid Camera in Scene")
        logwrite("warn(W): Non-Fatal exception caught ")

def stopplay():
    global camerax
    global cameray
    global cameraz
    global camerarotx
    global cameraroty
    global frm
    global iscompile
    iscompile = 0
    logwrite("Stop")
    frm.setpos(camerax,cameray,cameraz,camerarotx,cameraroty)

def RenderAll():
   
    # Find all .kasset files in the specified directory
    asset_files = glob.glob("./scene/Assets/*.kasset")
    
    if iscompile == 0:
        {
            renderXYdepth()
        }

    # Iterate over each .kasset file
    for asset_file in asset_files:
        # Initialize lists to store data read from the asset file
        vertices = []
        edges = []
        face_colors = []  # Separate list for face colors
        surfaces = []
        image_path = None  # Initialize image path variable
        pos = []
        rot = []
        global camid
        global campos
        global camrot
        iscam = False
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
                elif line.startswith("pos:"):
                    pos_data = line.split(":")[1].strip().split(",")
                    pos = [tuple(map(float, poss.split())) for poss in pos_data]
                elif line.startswith("rot:"):
                    rot_data = line.split(":")[1].strip().split(",")
                    rot = [tuple(map(float, rots.split())) for rots in rot_data]
                elif line.startswith("id:"):
                    camid = line.split(":")[1].strip()
                elif line.startswith("sound_path:"):
                    sound_path = line.split(":")[1].strip()
                elif line.startswith("script_path:"):
                    sound_path = line.split(":")[1].strip()
        # Check if all necessary data has been read
        if not vertices or not edges:
            if not rot or not pos or not camid:
                if not sound_path:
                    logwrite(f"error(!): Incomplete data in the asset file: {asset_file}")
                    continue  # Move to the next asset file
            else:
                #print("camera at: "+str(pos)+"camera rotation: "+str(rot)+"camera id: "+str(camid))
                iscam = True
                campos = pos[0]
                camrot = rot[0]
                camid = camid
                
        # If image path is specified, draw textured quads
        if image_path and iscam == False:
            # Load the texture
            texture_id = load_texture(image_path)
            # Draw textured quad for each surface
            for surface in surfaces:
                draw_textured_quad(texture_id, vertices, surface)
        else:
            if iscam == False:
                GL.glBegin(GL.GL_QUADS)
                for surface, color in zip(surfaces, face_colors): 
                    for vertex in surface:
                        GL.glColor3fv(color)
                        if vertex < len(vertices):
                            GL.glVertex3fv(vertices[vertex])
                        else:
                            logwrite(f"error(!): Index {vertex} is out of range for vertices list with length {len(vertices)}")
                
                GL.glEnd()
            else:
                #do nothing
                pass

def draw_textured_quad(texture_id, vertices, surface):
    # Convert texture_id to integer if necessary
    texture_id = int(texture_id)

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
    GL.glDeleteTextures(texture_id)

def renderXYdepth():
    color = (global_scene_noshade_brightness)

    GL.glColor3fv(color)
    GL.glBegin(GL.GL_LINES)
    for x in range(-250, 251, 10):
        GL.glVertex3f(x, 0, -250)
        GL.glVertex3f(x, 0, 250)
    for z in range(-250, 251, 10):
        GL.glVertex3f(-250, 0, z)
        GL.glVertex3f(250, 0, z)
    
    GL.glEnd()

def load_texture(texture_path):
    try:
        texture_image = Image.open(texture_path)
    except IOError as err:
        logwrite("error(!): Failed to open texture file: "+texture_path)
        logwrite("error(!): "+err)
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
        GLU.gluPerspective(45, (self.width / self.height), 0.1, 10000.0)  # Adjusted far clipping plane to 100.0
        GL.glTranslatef(self.camera_x, self.camera_y, self.camera_z)
        GL.glRotatef(self.view_angle_x, 1, 0, 0)
        GL.glRotatef(self.view_angle_y, 0, 1, 0)
        RenderAll()
        gc.collect()

    def setpos(self, x, y, z, xrot, yrot):
        
        self.camera_x = x
        self.camera_y = y
        self.camera_z = z
        self.view_angle_x = xrot
        self.view_angle_y = yrot
       
    def move_camera(self, direction):
        step = 0.2
        global camerax
        global cameray
        global cameraz
        global camerarotx
        global cameraroty
        camerax = self.camera_x
        cameray = self.camera_y
        cameraz = self.camera_z
        camerarotx = self.view_angle_x
        cameraroty = self.view_angle_y
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
        global camerax
        global cameray
        global cameraz
        global camerarotx
        global cameraroty
        camerax = self.camera_x
        cameray = self.camera_y
        cameraz = self.camera_z
        camerarotx = self.view_angle_x
        cameraroty = self.view_angle_y
        angle_step = 2
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
        if iscompile == 0:
            step = 0.01 #never used, will keep it. @Rodmatronic you can keep or remove as you see fit
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
                root.after(5, lambda: move_camera(direction))
            gc.collect()  # Trigger garbage collection
            

    root.bind("<KeyPress>", on_key)
    root.bind("<KeyRelease>", on_key_release)

    def donothing():
        pass

    def open_about():
        logwrite("About menu open")
        top = Toplevel(root) #undefined * import tk
        top.geometry("550x450")
        top.title("About Kunity")
        top.configure(bg="#333")
        top.resizable(False, False)  # Making the window unresizable
        top.attributes('-topmost', True)
        # top.iconbitmap("logo.ico")

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

        Label(top, text="Ver " + global_ver + " " + global_year + ", python version " + platform.python_version(), bg="#333", fg="White",font=('Mistral 10 bold')).place(x=22, y=145)
    
    def create_camera(camid):#creates camera with id (so you can have more than one camera)
        object_name = new_object_entry.get()

        # Check if the name is not empty
        print("Attempting to create file:", object_name)
        if object_name:
            # Create a new file with the given name and the ".kasset" extension
            with open(f"./scene/Assets/{object_name}.kasset", "w") as file:
                print("Created file:", object_name)
                
                file.write(str("[Kunity camera]\npos: 0.0 0.0 0.0\nrot: 0.0 0.0 0.0\nid: "+str(camid)))#creates a new camera instance file @ 0,0,0 with no rotation
            # Refresh the file view
            tree.delete(*tree.get_children())
            populate_tree(tree, "./scene")

    def create_soundsrc():
        object_name = new_object_entry.get()

        # Check if the name is not empty
        print("Attempting to create file:", object_name)
        if object_name:
            # Create a new file with the given name and the ".kasset" extension
            with open(f"./scene/Assets/{object_name}.kasset", "w") as file:
                print("note(N): Created file:", object_name)
                
                file.write(str("[Kunity soundsrc]\nsound_path: NULL"))
            # Refresh the file view
            tree.delete(*tree.get_children())
            populate_tree(tree, "./scene")

    def create_script():
        object_name = new_object_entry.get()

        # Check if the name is not empty
        print("Attempting to create file:", object_name)
        if object_name:
            # Create a new file with the given name and the ".kasset" extension
            with open(f"./scene/Assets/{object_name}.kasset", "w") as file:
                print("note(N): Created file:", object_name)
                
                file.write(str('[Kunity script]\nscript_path: NULL'))#add code editor to edit window :3
            # Refresh the file view
            tree.delete(*tree.get_children())
            populate_tree(tree, "./scene")

    def create_kasset_menu():
        # Create a new Toplevel window for the model options
        asset_selector_window = Toplevel(root)
        asset_selector_window.resizable(False, False)
        asset_selector_window.attributes('-topmost', True)
        asset_selector_window.configure(bg="#484848")
        asset_selector_window.geometry("420x500")
        # model_options_window.iconbitmap("logo.ico")

        # Get the name of the new object
        object_name = new_object_entry.get()

        asset_selector_window.title("'" + object_name + "' Select type")

        model_button = ttk.Button(asset_selector_window, text="📦 Generic asset", command=lambda: [create_kasset("model"), asset_selector_window.destroy()])
        model_button.grid(row=1, columnspan=1, pady=2, sticky=W)

        cam_button = ttk.Button(asset_selector_window, text="📷 Camera", command=lambda: [create_kasset("camera"), asset_selector_window.destroy()])
        cam_button.grid(row=2, columnspan=1, pady=2, sticky=W)

        src_button = ttk.Button(asset_selector_window, text="🔈Sound source", command=lambda: [create_kasset("soundsrc"), asset_selector_window.destroy()])
        src_button.grid(row=3, columnspan=1, pady=2, sticky=W)

        script_button = ttk.Button(asset_selector_window, text="🐍 Script", command=lambda: [create_kasset("script"), asset_selector_window.destroy()])
        script_button.grid(row=4, columnspan=1, pady=2, sticky=W)

    def create_kasset(type):
        object_name = new_object_entry.get()

        if type == "camera":
            create_camera(camcount+1)
        elif type == "soundsrc":
            create_soundsrc()
        elif type == "script":
            create_script()
        elif type == "model":
            # Check if the name is not empty
            logwrite("note(N): Attempting to create file:"+ object_name)
            if object_name:
                # Create a new file with the given name and the ".kasset" extension
                with open(f"./scene/Assets/{object_name}.kasset", "w") as file:
                    logwrite("note(N): Created file:"+ object_name)
                    file.write("[Kunity object]\nVertices: 0.0 0.0 0.0\nEdges:\nColors:\nSurfaces:")
                # Refresh the file view
                tree.delete(*tree.get_children())
                populate_tree(tree, "./scene")

    def delete_selected():
        # Get selected items from the Treeview
        selected_items = tree.selection()
        for item in selected_items:
            file_name = tree.item(item, "text")
            file_path = os.path.join("./scene/Assets/", file_name)
            logwrite("note(N): Attempting to delete file:"+ file_path)
            try:
                # Remove the file from the file system
                os.remove(file_path)
                # Delete the item from the Treeview
                tree.delete(item)
                logwrite("note(N): File deleted successfully.")
            except FileNotFoundError:
                try:
                    file_path = os.path.join("./scene/Assets/scripts/", file_name)
                    # Remove the file from the file system
                    os.remove(file_path)
                    # Delete the item from the Treeview
                    tree.delete(item)
                    logwrite("note(N): File deleted successfully.")
                except FileNotFoundError:
                    try:
                        file_path = os.path.join("./scene/Assets/materials/", file_name)
                        # Remove the file from the file system
                        os.remove(file_path)
                        # Delete the item from the Treeview
                        tree.delete(item)
                        logwrite("note(N): File deleted successfully.")
                    except FileNotFoundError:
                        logwrite("error(!): File not found:"+ file_path)

    # Set dark mode theme
    style = ttk.Style()
    style.theme_use('clam')  # Use 'clam' theme as it's closer to dark mode
    style.configure("TFrame", background="#222")
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
    filemenu.add_command(label="Restart", command=main)
    filemenu.add_command(label="Exit", command=safe_exit)
    menubar.add_cascade(label="File", menu=filemenu)

    editmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=editmenu)
    editmenu.add_command(label="Undo", command=undo)
    editmenu.add_command(label="Redo", command=redo)
    editmenu.add_separator()
    editmenu.add_command(label="Cut", command=cut)
    editmenu.add_command(label="Copy", command=copy)
    editmenu.add_command(label="Paste", command=paste)
    editmenu.add_separator()
    editmenu.add_command(label="Rename", command=rename)

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

    play_image = play_image.resize((17, 17), Image.Resampling.LANCZOS)
    pause_image = pause_image.resize((17, 17), Image.Resampling.LANCZOS)
    stop_image = stop_image.resize((17, 17), Image.Resampling.LANCZOS)

    # Convert PIL images to Tkinter PhotoImage objects
    play_photo = ImageTk.PhotoImage(play_image)
    pause_photo = ImageTk.PhotoImage(pause_image)
    stop_photo = ImageTk.PhotoImage(stop_image)

    # Update button creation with images
    play_button = ttk.Button(top_bar_frame, image=play_photo, command=compileandrun)
    pause_button = ttk.Button(top_bar_frame, image=pause_photo, command=stopplay)
    stop_button = ttk.Button(top_bar_frame, image=stop_photo, command=stopplay)

    # Pack buttons
    play_button.pack(side=tk.LEFT, pady=5, padx=4)
    pause_button.pack(side=tk.LEFT, pady=5, padx=4)
    stop_button.pack(side=tk.LEFT, pady=5, padx=4)

    # Toolbar
    toolbar = ttk.Frame(root, relief="flat", height=20, style="Toolbar.TFrame")
    toolbar.pack(side=tk.TOP, fill=tk.X)

    style.configure("Toolbar.TFrame", background="#333")

    paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    left_frame = ttk.Frame(paned_window, relief="flat", width=400, height=500)
    editor = ttk.Frame(paned_window, width=400, height=600)
    paned_window.add(left_frame)
    paned_window.add(editor)
    paned_window.pack(fill=tk.BOTH, expand=True)

    # Add a label at the top of the left_frame
    hierarchy_label = ttk.Label(toolbar, width=12, text=" ⫤ Hierarchy", background="#484848", foreground="#FFFFFF")
    hierarchy_label.pack(padx=8, pady=0, side= TOP, anchor="w")

    # Create a Treeview widget
    tree = ttk.Treeview(left_frame)
    tree.pack(fill='both', expand=True)
    populate_tree(tree, "./scene")

    # Add a "Delete" button next to the Treeview
    delete_button = ttk.Button(left_frame, text="Delete", command=delete_selected)
    delete_button.pack(side=tk.LEFT, padx=5, pady=3)
    global frm
    global camerax
    global cameray
    global cameraz
    global camerarotx
    global cameraroty
    frm = editorenv(master=editor, height=600, width=400)
    frm.animate = 10
    #frm.setpos(camerax,cameray,cameraz,camerarotx,cameraroty)
    frm.pack(fill=tk.BOTH, expand=True)

    # Add a "+" button to create a new ".kasset" object
    create_button = ttk.Button(left_frame, text="+", command=create_kasset_menu)
    create_button.pack(side=tk.RIGHT, padx=5, pady=3)

    # Add an entry field to enter the name of the new object
    new_object_entry = ttk.Entry(left_frame, font=("Calibri", 10))  # Set font to Consolas and increase font size
    new_object_entry.pack(side=tk.RIGHT, padx=0, pady=0, fill=tk.X, expand=True)  # Make the entry field fill the available space horizontally
    new_object_entry.insert(0, "GameObject")

    gc.collect()

    def on_tree_right_click(event):
        # Select item on right-click
        item = tree.identify('item', event.x, event.y)
        tree.selection_set(item)
        # Display the context menu
        context_menu.post(event.x_root, event.y_root)
    def save_script_changes(path_entry, file_path):
        updated_path = path_entry.get()
        with open(file_path, "w") as file:
            file.write("[Kunity script]\n")
            file.write(f"script_path: {updated_path}\n")
        logwrite("note(N): Changes saved successfully!")
    def save_model_changes(vertices_entry, edges_entry, colors_entry, surfaces_entry, image_entry, position_entry, file_path):
        # Get the updated data from the entry fields
        updated_vertices = vertices_entry.get()
        updated_edges = edges_entry.get()
        updated_colors = colors_entry.get()
        updated_surfaces = surfaces_entry.get()
        updated_image = image_entry.get()
        position = position_entry.get().split()  # Split the position input into X, Y, Z components

        # Check if the position input is valid
        if len(position) != 3:
            logwrite("error(!): Invalid position input. Please enter three values separated by spaces for X, Y, and Z.")
            return

        try:
            # Attempt to convert position components to float
            position = [float(coord) for coord in position]
        except ValueError:
            logwrite("error(!): Invalid position input. Please enter numeric values for X, Y, and Z.")
            return

        # Apply the position changes to the vertices
        updated_vertices = set_vertices_to_position(updated_vertices, position)

        # Write the updated data to the model file
        with open(file_path, "w") as file:
            file.write("[Kunity object]\n")
            file.write(f"Vertices: {updated_vertices}\n")
            file.write(f"Edges: {updated_edges}\n")
            file.write(f"Colors: {updated_colors}\n")
            file.write(f"Surfaces: {updated_surfaces}\n")
            file.write(f"Image: {updated_image}\n")

        logwrite("note(N): Changes saved successfully!")

    def save_camera_changes(position_entry, rotation_entry, id_entry, file_path):
        updated_position = position_entry.get()
        updated_rotation = rotation_entry.get()
        updated_id = id_entry.get()

        with open(file_path, "w") as file:
            file.write("[Kunity camera]\n")
            file.write(f"pos: {updated_position}\n")
            file.write(f"rot: {updated_rotation}\n")
            file.write(f"id: {updated_id}\n")
        logwrite("note(N): Changes saved successfully!")
        
    def set_vertices_to_position(vertices_str, position):
        # Split the vertices string into individual vertices
        vertices = vertices_str.split(",")
        updated_vertices = []

        # Loop through each vertex and set it to the specified position
        for vertex in vertices:
            # Remove any trailing or leading whitespace
            vertex = vertex.strip()
            x, y, z = map(float, vertex.split())
            x += position[0]  # Add the X component of the position
            y += position[1]  # Add the Y component of the position
            z += position[2]  # Add the Z component of the position
            updated_vertices.append(f"{x} {y} {z}")

        # Join the updated vertices into a single string
        return ", ".join(updated_vertices)

    def show_model_options():
        # Create a new Toplevel window for the model options
        model_options_window = Toplevel(root)
        model_options_window.resizable(False, False)  # Making the window unresizable
        model_options_window.attributes('-topmost', True)
        model_options_window.configure(bg="#484848")
        # model_options_window.iconbitmap("logo.ico")
        # Retrieve the selected item from the tree view
        selected_item = tree.selection()[0]
        file_name = tree.item(selected_item, "text")
        file_path = os.path.join("./scene/Assets/", file_name)

        model_options_window.title("'" + file_name + "' Options")

        # Read data from the selected model file
        with open(file_path, "r") as file:
            model_data = file.readlines()
            first_line = model_data[0].strip()
            if first_line == "[Kunity camera]":
                logwrite("note(N): Edit type: Camera")
                pos = ""
                rot = ""
                id = ""

                for line in model_data:
                    if line.startswith("pos:"):
                        pos = line.split(":")[1].strip()
                    elif line.startswith("rot:"):
                        rot = line.split(":")[1].strip()
                    elif line.startswith("id:"):
                        id = line.split(":")[1].strip()

                rotation_label = ttk.Label(model_options_window, text="Rotation (X Y Z):")
                rotation_label.grid(row=1, column=0, padx=6, sticky="w")
                rotation_entry = ttk.Entry(model_options_window)
                rotation_entry.grid(row=1, column=1, padx=5, pady=5)
                rotation_entry.insert(0, rot)

                position_label = ttk.Label(model_options_window, text="Position (X Y Z):")
                position_label.grid(row=5, column=0, padx=6, sticky="w")
                position_entry = ttk.Entry(model_options_window)
                position_entry.grid(row=5, column=1, padx=5, pady=5)
                position_entry.insert(0, pos)

                id_label = ttk.Label(model_options_window, text="Camera ID:")
                id_label.grid(row=2, column=0, padx=6, sticky="w")
                id_entry = ttk.Entry(model_options_window)
                id_entry.grid(row=2, column=1, padx=5, pady=5)
                id_entry.insert(0, id)

                # Add a "Save" button to save changes
                save_button = ttk.Button(model_options_window, text="Save", command=lambda: save_camera_changes(position_entry, rotation_entry, id_entry, file_path))
                save_button.grid(row=6, columnspan=2, pady=10)
            elif first_line == "[Kunity soundsrc]":
                logwrite("note(N): Edit type: Sound")
            elif first_line == "[Kunity script]":
                logwrite("note(N): Edit type: Script")
                path = ""
                for line in model_data:
                    if line.startswith("script_path:"):
                        path = line.split(":")[1].strip()
                path_label = ttk.Label(model_options_window, text="script path:")
                path_label.grid(row=1, column=0, padx=6, sticky="w")
                path_entry = ttk.Entry(model_options_window)
                path_entry.grid(row=1, column=1, padx=5, pady=5)
                path_entry.insert(0, path)
                save_button = ttk.Button(model_options_window, text="Save", command=lambda: save_script_changes(path_entry, file_path))
                save_button.grid(row=6, columnspan=2, pady=10)
                #do some crap here to edit
            else:
                logwrite("note(N): Edit type: Normal/model")
                # Initialize variables to store model data
                vertices = ""
                edges = ""
                colors = ""
                surfaces = ""
                image = ""

                # Parse model data and extract vertices, edges, colors, surfaces, and image
                for line in model_data:
                    if line.startswith("Vertices:"):
                        vertices = line.split(":")[1].strip()
                    elif line.startswith("Edges:"):
                        edges = line.split(":")[1].strip()
                    elif line.startswith("Colors:"):
                        colors = line.split(":")[1].strip()
                    elif line.startswith("Surfaces:"):
                        surfaces = line.split(":")[1].strip()
                    elif line.startswith("Image:"):
                        image = line.split(":")[1].strip()

                # Calculate the average of X, Y, and Z coordinates for all vertices
                total_x, total_y, total_z = 0, 0, 0
                num_vertices = 0
                for vertex in vertices.split(","):
                    x, y, z = map(float, vertex.strip().split())
                    total_x += x
                    total_y += y
                    total_z += z
                    num_vertices += 1

                avg_x = total_x / num_vertices
                avg_y = total_y / num_vertices
                avg_z = total_z / num_vertices

                # Add labels and entry fields for model options
                vertices_label = ttk.Label(model_options_window, text="Vertices:")
                vertices_label.grid(row=0, column=0, padx=6, sticky="w")
                vertices_entry = ttk.Entry(model_options_window)
                vertices_entry.grid(row=0, column=1, padx=5, pady=5)
                vertices_entry.insert(0, vertices)  # Insert vertices data into entry field

                # Add a label and entry field for the position
                position_label = ttk.Label(model_options_window, text="Position (X Y Z):")
                position_label.grid(row=5, column=0, padx=6, sticky="w")
                position_entry = ttk.Entry(model_options_window)
                position_entry.grid(row=5, column=1, padx=5, pady=5)
                position_entry.insert(0, f"{avg_x} {avg_y} {avg_z}")  # Insert average position data into entry field

                edges_label = ttk.Label(model_options_window, text="Edges:")
                edges_label.grid(row=1, column=0, padx=6, sticky="w")
                edges_entry = ttk.Entry(model_options_window)
                edges_entry.grid(row=1, column=1, padx=5, pady=5)
                edges_entry.insert(0, edges)  # Insert edges data into entry field

                colors_label = ttk.Label(model_options_window, text="Colors (RGB):")
                colors_label.grid(row=2, column=0, padx=6, sticky="w")
                colors_entry = ttk.Entry(model_options_window)
                colors_entry.grid(row=2, column=1, padx=5, pady=5)
                colors_entry.insert(0, colors)  # Insert colors data into entry field

                surfaces_label = ttk.Label(model_options_window, text="Surfaces:")
                surfaces_label.grid(row=3, column=0, padx=6, sticky="w")
                surfaces_entry = ttk.Entry(model_options_window)
                surfaces_entry.grid(row=3, column=1, padx=5, pady=5)
                surfaces_entry.insert(0, surfaces)  # Insert surfaces data into entry field

                image_label = ttk.Label(model_options_window, text="Image:")
                image_label.grid(row=4, column=0, padx=6, sticky="w")
                image_entry = ttk.Entry(model_options_window)
                image_entry.grid(row=4, column=1, padx=5, pady=5)
                image_entry.insert(0, image)  # Insert image path data into entry field

                # Add a "Save" button to save changes
                save_button = ttk.Button(model_options_window, text="Save", command=lambda: save_model_changes(vertices_entry, edges_entry, colors_entry, surfaces_entry, image_entry, position_entry, file_path))
                save_button.grid(row=6, columnspan=2, pady=10)
    
    def option1_action():
        show_model_options()

    # Create a context menu
    context_menu = Menu(root, tearoff=0)
    context_menu.add_command(label="New...", command=create_kasset_menu)
    context_menu.add_command(label="Edit model...", command=option1_action)

    tree.bind("<Button-3>", on_tree_right_click)  # Bind right-click event to the function

    root.bind("<Key>", on_key)
    return root.mainloop()

if __name__ == "__main__":
    main()
