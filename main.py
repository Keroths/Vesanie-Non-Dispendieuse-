from cons import *
import sys, time, inspect, math

if sys.version_info[0] == 2:  # Just checking your Python version to import Tkinter properly.
    from Tkinter import *
else:
    from tkinter import *


__funcs_screen = ["toggle_fullscreen", "end_fullscreen","switch_fullscreen", "leave", "background", "getScreen", "update", "c_empty", "c_undo"]
__funcs_pen = ["cercle", "forward", "rotate", "left", "right", "undo", "empty", "setColor"]


ALL_FUNCS_NAME = __funcs_screen + __funcs_pen

class PAP_Error(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr("Une erreur est survenue:",self.value)

class Terminated(Exception):
    def __init__(self): pass
    def __str__(self):
        print("==================\n\
\
\
La fenêtre a été fermée. Les commandes sont désactivées.\
\n\
============================\
")
        return ""

def debug(s, t="ALL"):
    try:
        if DEBUG[t]or DEBUG["ALL"]:
            print(s)
    except KeyError: print("Unknown type %s, passing debug" %(t)); print(s)


    
class Screen:

    __name__ = "Screen"

    def __init__(self, root=None):

        
        #Parametres de FullScreen
        self.fullscreen = FULLSCREEN

        if root==None:self.tk = Tk() #Permet l'importation de la fenetre en tant que frame
        else: self.tk = root        #ou en tant que standalone.
        
        self.frame = Frame(self.tk)
        self.frame.pack()
        
        #Binding 
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        self.tk.bind("<Configure>", self.__reconfig__)
        
        self.tk.protocol("WM_DELETE_WINDOW", self.leave)
        
        if FULLSCREEN :self.toggle_fullscreen()
        
        self.canvas = Canvas(self.tk, width = 800, height = 800, bg="white")
        self.canvas.pack(expand=True, fill='both')

    def reset(self):
        self.canvas.delete(ALL)
        self.update()
            
    def toggle_fullscreen(self, event=None):
        self.state = True  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "done"
    
    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", self.state)
        return "done"

    def switch_fullscreen(self):
        self.state = not self.state
        self.tk.attributes("-fullscreen", self.state)
        return self.state

    
    def leave(self, event=None):
        if not CONFIRM_QUIT or messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter ? #Tristesse"):
            self.tk.destroy()
        raise Terminated
        
    def __reconfig__(self, event):
        x, y = event.width//2, event.height//2
        self.canvas.config(scrollregion=(-x, -y, x, y))

    def background(self, color):
        if isinstance(color, (int, int, int)):
            pass
        else: self.canvas.config(background=color)
        
    def getScreen(self): return self
    
    def update(self):
        self.canvas.update()

    def c_empty(self): return self.canvas.find_all()==()
    def c_undo(self):
        try:
            self.canvas.delete(self.canvas.find_all()[-1])
            self.update()
            return True
        except: return False
        
class __Head_Navigator:  #Implementation de la gestion des positions

    def __init__(self, pos=(0,0), dire = 0):

        self.x = pos[0]
        self.y = pos[1]
        self.dir = math.radians(dire)

    def get(self):
        return ((self.x, self.y), self.dir)
    
    def forward(self, x):

        self.x = (self.x+(x*(math.cos(self.dir))))
        self.y = (self.y+(x*(math.sin(self.dir))))
        return (self.x, self.y)

    def left(self, angle): self.dir -= math.radians(angle)
    def right(self, angle): self.dir += math.radians(angle)
    def rotate(self, angle): self.right(angle)

    def reset(self):
        self.x = self.y = self.dir= 0

 
#Classe gestion de buffering, peut etre améliorée
        

class __Item_Change_Buffer:

    def __init__(self, size=2000): self.buff = []; self.size = size
    def empty(self): return self.buff==[]
    def pop(self): return self.buff.pop(-1)
    def add(self, item):
        if len(self.buff)==self.size: self.buff.pop(0)
        self.buff.append(item)



class Navigator(__Head_Navigator):

    __obj_counter = 0
    
    def __init__(self, pos=(0,0), dire = 0, shown=False):

        _HN.__init__(self, pos, dire)

        Navigator.__obj_counter +=1
        self.id = "Navigator_"+str(Navigator.__obj_counter)
        
        self.w = getScreen()
        self.shown = shown

        self.show()
        
    def link(self, other, couleur="black", epaisseur=LINE_WIDTH):
        debug(*_HN.get(self)[0], *_HN.get(other)[0])
        self.w.canvas.create_line(*_HN.get(self)[0], *_HN.get(other)[0],  width=epaisseur,
                                  smooth=0, fill = couleur)
        self.w.update()

    def forward(self, x):
        _HN.forward(self, x)
        if self.shown: self.show()
        
    def show(self):
        if self.shown :
            self.w.canvas.delete(self.id)
            Pen.cercle(self, 5)
        self.w.update()

class Pen(__Head_Navigator, __Item_Change_Buffer):

    __name__ = "Pen"
    __obj_count__ = 0
    
    def __init__(self, pos = (0,0), direction = 0):

        
        _HN.__init__(self, pos, direction)
        _ICB.__init__(self)
        
        Pen.__obj_count__ += 1
        self.id = "Pen_"+str(Pen.__obj_count__)
         
        self.w = getScreen()
        self.color = "black"
        debug(("got it,", self.w))

    def __setDefault__(self, kwargs, output, kw, trslt, dflt):
        if kw in kwargs: output[trslt]=kwargs[kw]
        else : output[trslt]=dflt
        
    def __getOptions__(self, kwargs):
        output = {}
        return output
    
    def cercle(self, r, couleur="", contour="black", epaisseur=LINE_WIDTH):

        debug((r, couleur, contour, epaisseur, self.id), "DRAWING")

        self.w.canvas.create_oval(self.x-r, self.y-r, self.x+r, self.y+r,
                             fill=couleur, outline=contour, width=epaisseur, tag=self.id)
        self.w.update()

    def forward(self, x, epaisseur=LINE_WIDTH):
        
        self.buff.append(
            self.w.canvas.create_line(*_HN.get(self)[0], *_HN.forward(self, x),
                                      tag = self.id, width=epaisseur, smooth=True, fill = self.color)
            )
        self.w.update()

    def reset(self):
        _HN.reset(self)

    def undo(self):
        self.w.canvas.delete(_ICB.pop(self))
        self.w.update()
        
    def setColor(self, color): self.color = color
    def setLineWidth(self, width): self.lineWidth = width

    
#Raccourci pour accès classe
_HN = __Head_Navigator
_ICB = __Item_Change_Buffer

        
###Permet de faire forward(x) au lieu de p.forward(x)###


#Creation d'une fonction qui sera ensuite adapté grace a un format().
#Ce texte sera ensuite compilé dans la zone "global" afin d'etre accessible directement.
#L'interet de ces deux fonctions est de pouvoir ajouter des fonctionnalités sans modification
#Et sans code tres repetitif;

func_format = """\
def {name}({args}):
    global {obj}
    if {obj}==None: {obj} = {cls}()
    try:
        return {obj}.{name}({args_name})
    except: raise PAP_Error("Error", sys.exc_info())   
"""
def some_iter(l):
    for x in l:
        if isinstance(x, str):
            yield '"'+x+'"'
        else: yield x
def get_args_list(func):

    a, var, kwarg, b = inspect.getargspec(func)  #Output -> args
    if b:
        b = [x for x in some_iter(b)]
        output = a[1:len(a)-len(b)]+list(map(lambda x:"%s=%s" %(x[0], x[1]),  #Cette ligne a pour but d'ajouter les premiers argument sans valeur par defaut, et d'assembler 
                                 (zip(a[len(a)-len(b)::1], b))))              #Les arguments avec des valeurs par defaut. Le zip fait des tuple de a[n], b[n]. La lambda le depack et en fait un "{argname}={defaultvalue}" 
    else: output = a[1::1]
    default = a[1::1]
    if var:
        temp ="*%s" %(var);output.append(temp);default.append(temp)
    if kwarg:
        temp="**%s" %(kwarg);output.append(temp);default.append(temp)
    return output, default

def construct_func(funcs, clss, varName = None): #La classe entrée doit posséder un attribut __name__
    if varName == None: varName = "_"+clss.__name__
    debug(varName)
    exec("%s = None"%(varName), globals())
    for funcname in funcs:
        func = getattr(clss, funcname)
        args_entry, args = get_args_list(func)
        exec(func_format.format(name=funcname, args = ",".join(args_entry),
                                args_name = ",".join(args), cls=clss.__name__, obj=varName),
             globals())

construct_func(__funcs_screen, Screen)
construct_func(__funcs_pen, Pen)

def reset():
    _Screen.reset()
    _Pen.reset()
