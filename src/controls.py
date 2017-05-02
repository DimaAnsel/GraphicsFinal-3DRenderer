################################
# controls.py
# Noah Ansel
# nba38
# 2016-11-17
# ------------------------------
# Controls viewpoint, scene, and rendering options of a Display object.
################################

# import validation
fail = False
try:
  from tkinter import *
except Exception:
  print("ERROR: Could not import 'tkinter' module.")
  fail = True
try:
  from display import Display
except Exception:
  print("ERROR: Could not import 'display' module. Is it in this folder?")
  fail = True
try:
  from time import clock
except Exception:
  print("ERROR: Could not import 'time' module.")
  fail = True
try:
  import os
except Exception:
  print("ERROR: Could not import 'os' module.")
  fail = True
if fail:
  print("Press ENTER to close this window.")
  exit()


################
# Controls: Tkinter object that controls a Display.
class Controls(Frame):

  # shade modes (and labels)
  SHADE_MODES = [("Ambient",  Display.SHADE_AMBIENT),
                 ("Diffuse",  Display.SHADE_DIFFUSE),
                 ("Specular", Display.SHADE_SPECULAR)]

  # resolution options (and labels)
  RES_OPTIONS = [("Low",    Display.RES_LOW),
                 ("Medium", Display.RES_MEDIUM),
                 ("High",   Display.RES_HIGH),
                 ("Ultra",  Display.RES_ULTRA),
                 ("Insane", Display.RES_INSANE),
                 ("Realistic", Display.RES_REALISTIC)]

  # Directory in which to save images.
  IMAGE_DIRECTORY = "../images/"

  # Filename to save images to. Will be appended with a number.
  IMAGE_OUTFILE = IMAGE_DIRECTORY + "generated_image"


  ########
  # Initializes references and sets up internal Tkinter widgets.
  #   Params:
  #     master  : Reference to master Tkinter widget
  #     display : Reference to the Display object to render scenes in.
  def __init__(self, master, display):
    if not isinstance(display, Display):
      raise TypeError("Expected 'Display' type, got '{}'.".format(type(display)))

    super().__init__(master)
    self._display = display

    self._create_widgets()
    self._place_widgets()

    self._on_res_select()

  ########
  # Creates and initializes all Tkinter widgets.
  def _create_widgets(self):
    self._sceneLabel = Label(self, text = "Scene:")
    self._sceneVar = StringVar()
    self._sceneVar.set("scene1.txt")
    self._sceneEntry = Entry(self, textvariable = self._sceneVar)
    self._sceneEntry.bind("<Return>", self._on_res_select)

    self._widthLabel = Label(self, text = "Width:")
    self._heightLabel = Label(self, text = "Height:")
    self._widthVar = StringVar()
    self._widthVar.set(self._display._canvas.cget("width"))
    self._widthEntry = Entry(self, textvariable = self._widthVar)
    self._widthEntry.bind("<Return>", self._on_commit_press)
    self._heightVar = StringVar()
    self._heightVar.set(self._display._canvas.cget("height"))
    self._heightEntry = Entry(self, textvariable = self._heightVar)
    self._heightEntry.bind("<Return>", self._on_commit_press)

    self._rotationSlider = Scale(self,
                                 orient = HORIZONTAL,
                                 label = "Camera Rotation (π):",
                                 from_ = 0,
                                 to = 2,
                                 resolution = 0.05)
    self._rotationSlider.set(0.25)
    self._rotationSlider.config(command = self._on_commit_press)

    self._inclineSlider = Scale(self,
                                orient = HORIZONTAL,
                                label = "Camera Incline (π):",
                                from_ = 0,
                                to = 1,
                                resolution = 0.05)
    self._inclineSlider.set(0.75)
    self._inclineSlider.config(command = self._on_commit_press)

    self._zoomSlider = Scale(self,
                             orient = HORIZONTAL,
                             label = "Camera Distance:",
                             from_ = 10,
                             to = 100,
                             resolution = 1)
    self._zoomSlider.set(30)
    self._zoomSlider.config(command = self._on_commit_press)

    self._shadeTypeLabel = Label(self,
                                 text = "Shading:")
    self._shadeTypeFrame = Frame(self)
    self._shadeTypeVars = []
    self._shadeTypeButtons = []
    for label, val in Controls.SHADE_MODES:
      var = IntVar(self)
      c = Checkbutton(self._shadeTypeFrame,
                      text = label,
                      variable = var,
                      onvalue = val,
                      offvalue = 0)
      c.select()
      c.config(command = self._on_commit_press)
      self._shadeTypeVars.append(var)
      self._shadeTypeButtons.append(c)

    self._resLabel = Label(self, text = "Resolution:")
    self._resVar = StringVar()
    self._resVar.set(Display.RES_MEDIUM)
    self._resFrame = Frame(self)
    self._resButtons = []
    for label, val in Controls.RES_OPTIONS:
      b = Radiobutton(self._resFrame,
                      text = label,
                      variable = self._resVar,
                      value = val,
                      command = self._on_res_select)
      self._resButtons.append(b)

    self._castShadowsVar = IntVar(self)
    self._castShadowsCheck = Checkbutton(self,
                                         text = "Cast shadows",
                                         variable = self._castShadowsVar)
    self._castShadowsCheck.select()
    self._castShadowsCheck.config(command = self._on_commit_press)

    self._renderTimeLabel = Label(self,
                                  text = "Not yet rendered.",
                                  justify = LEFT)
    self._loadTimeLabel = Label(self,
                                text = "Not yet loaded.",
                                justify = LEFT)

    self._commitButton = Button(self,
                                text = "Commit",
                                command = self._on_commit_press)

    self._saveButton = Button(self,
                              text = "Save Image",
                              command = self._on_save_press)

  ########
  # Places all Tkinter widgets inside the Controls frame.
  def _place_widgets(self):
    self._sceneLabel.grid(row = 0, column = 0, sticky = N+W)
    self._sceneEntry.grid(row = 0, column = 1, sticky = W+E)

    self._widthLabel.grid(row = 1, column = 0, sticky = N+W)
    self._widthEntry.grid(row = 1, column = 1, sticky = W+E)
    self._heightLabel.grid(row = 2, column = 0, sticky = N+W)
    self._heightEntry.grid(row = 2, column = 1, sticky = W+E)

    self._rotationSlider.grid(row = 3, column = 0, columnspan = 2, sticky = W+E)
    self._inclineSlider.grid(row = 4, column = 0, columnspan = 2, sticky = W+E)
    self._zoomSlider.grid(row = 5, column = 0, columnspan = 2, sticky = W+E)

    self._shadeTypeLabel.grid(row = 6, column = 0, columnspan = 2, sticky = W)
    for i in range(len(self._shadeTypeButtons)):
      self._shadeTypeButtons[i].grid(row = i, column = 0, sticky = W)
    self._shadeTypeFrame.grid(row = 7, column = 0, columnspan = 2, sticky = W+E)

    self._resLabel.grid(row = 8, column = 0, columnspan = 2, sticky = W)
    for i in range(len(self._resButtons)):
      self._resButtons[i].grid(row = i, column = 0, sticky = W)
    self._resFrame.grid(row = 9, column = 0, columnspan = 2, sticky = W+E)

    self._castShadowsCheck.grid(row = 10, column = 0, columnspan = 2, sticky = W)

    self._loadTimeLabel.grid(row = 18, column = 0, columnspan = 2, sticky = W+E)
    self._renderTimeLabel.grid(row = 19, column = 0, columnspan = 2, sticky = W+E)

    self._commitButton.grid(row = 20, column = 0, columnspan = 2, sticky = W+E)

    self._saveButton.grid(row = 21, column = 0, columnspan = 2, sticky = W+E)

  ########
  # Updates the display's camera position and renders the scene.
  # Also updates timing information in bottom of controls pane.
  def _on_commit_press(self, *args, **kwargs):
    start = clock()
    try:
      self._display._canvas.config(width = int(self._widthVar.get()),
                                   height = int(self._heightVar.get()))
    finally:
      self._display.update_camera(zoom = self._zoomSlider.get(),
                                  incline = self._inclineSlider.get(),
                                  rotation = self._rotationSlider.get())
      shadeType = 0
      for v in self._shadeTypeVars:
        shadeType += v.get()
      rasterTime = self._display.render(shadeType = shadeType, castShadows = self._castShadowsVar.get())
      elapsed = clock() - start
      rasterPct = 100 * rasterTime / elapsed
      self._renderTimeLabel.config(text = "Rendered in: {:.4f} sec\n\
Rasterize: {:.2f}s ({:.0f}%)\n\
Other:     {:.2f}s ({:.0f}%)".format(elapsed,
                                     rasterTime,
                                     rasterPct,
                                     elapsed - rasterTime,
                                     100 - rasterPct))

  ########
  # Saves the currently rendered image in the current directory.
  def _on_save_press(self, *args, **kwargs):
    i = 0
    try:
      os.listdir(Controls.IMAGE_DIRECTORY)
    except FileNotFoundError:
      os.mkdir(Controls.IMAGE_DIRECTORY)
    try:
      while True:
        f = open(Controls.IMAGE_OUTFILE + str(i) + '.png', 'r')
        f.close()
        i += 1
    except FileNotFoundError: # found our next file
      self._display._buffer.save(Controls.IMAGE_OUTFILE + str(i) + '.png', format = "PNG")

  ########
  # Reloads scene with the current resolution and renders the scene.
  def _on_res_select(self, *args, **kwargs):
    start = clock()
    self._display.load_objects(filename = self._sceneVar.get(),
                               resolution = self._resVar.get())
    elapsed = clock() - start
    self._loadTimeLabel.config(text = "Loaded in: {:.4f} sec".format(elapsed))
    self._on_commit_press()
# Controls
################