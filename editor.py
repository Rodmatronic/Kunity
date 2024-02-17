import tkinter as tk
from tkinter import ttk
from pyopengltk import OpenGLFrame
from OpenGL import GL, GLU
from tkinter import *
import os
from PIL import Image, ImageTk

global_ver = "1.0"

# The default object
verticies = ((1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
             (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1))

edges = ((0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7),
         (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7))

root = tk.Tk()
root.geometry("1100x600")
root.title("Kunity")

try:
    os.remove("kubuntu.logfile.txt") 
except:
    print("No previous logfile! Nothing to remove")

def logwrite(log):
    print(log)
    logfile = open("kubuntu.logfile.txt", "a")
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

def Cube():
    GL.glBegin(GL.GL_LINES)
    for edge in edges:
        for vertex in edge:
            GL.glVertex3fv(verticies[vertex])
    GL.glEnd()


class CubeSpinner(OpenGLFrame):
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
    def on_key(event):
        if event.keysym == "w":
            logwrite("Moving main camera foward")
            frm.move_camera("forward")
        elif event.keysym == "s":
            logwrite("Moving main camera backward")
            frm.move_camera("backward")
        elif event.keysym == "a":
            logwrite("Moving main camera right")
            frm.move_camera("sideways_right")
        elif event.keysym == "d":
            logwrite("Moving main camera left")
            frm.move_camera("sideways_left")
        elif event.keysym == "Left":
            logwrite("Turning main camera to the left")
            frm.rotate_camera("left_arrow")
        elif event.keysym == "Right":
            logwrite("Turning main camera to the right")
            frm.rotate_camera("right_arrow")
        elif event.keysym == "Up":
            logwrite("Turning main camera upwards")
            frm.rotate_camera("up_arrow")
        elif event.keysym == "Down":
            logwrite("Turning main camera downards")
            frm.rotate_camera("down_arrow")

    def donothing():
        print("Placeholder")

    def open_about():
        logwrite("About menu open")
        top = Toplevel(root)
        top.geometry("320x350")
        top.title("About Kunity")
        top.configure(bg="#333")

        # Load the image
        image = PhotoImage(file="./kunity.logo.png")

        # Create a label to display the image
        image_label = Label(top, image=image, bg="#333")
        image_label.image = image  # Keep a reference to the image to prevent it from being garbage collected
        image_label.place(x=0, y=0)  # Adjust the position as needed

        Label(top, text="Ver " + global_ver, bg="#333", fg="White",font=('Mistral 18 bold')).place(x=5, y=100)

    # Set dark mode theme
    style = ttk.Style()
    style.theme_use('clam')  # Use 'clam' theme as it's closer to dark mode

    # Configure style for Treeview
    style.configure("Treeview", background="#333", foreground="#ddd", fieldbackground="#333")
    style.map("Treeview", background=[('selected', '#666')])

    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=donothing)
    filemenu.add_command(label="Open", command=donothing)
    filemenu.add_command(label="Save", command=donothing)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=safe_exit)
    menubar.add_cascade(label="File", menu=filemenu)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=donothing)
    helpmenu.add_command(label="About...", command=open_about)
    menubar.add_cascade(label="Help", menu=helpmenu)

    root.config(menu=menubar)

    paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    left_frame = ttk.Frame(paned_window, width=300, height=500)
    editor = ttk.Frame(paned_window, width=400, height=600)
    paned_window.add(left_frame)
    paned_window.add(editor)
    paned_window.pack(fill=tk.BOTH, expand=True)

    # Create a Treeview widget
    tree = ttk.Treeview(left_frame)
    tree.pack(fill='both', expand=True)
    populate_tree(tree, "./scene")

    frm = CubeSpinner(master=editor, height=600, width=400)
    frm.animate = 10
    frm.pack(fill=tk.BOTH, expand=True)

    root.bind("<Key>", on_key)
    return root.mainloop()

if __name__ == "__main__":
    main()
