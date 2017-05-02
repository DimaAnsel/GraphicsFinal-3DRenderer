################################
# displays.py
# Noah Ansel
# nba38
# 2016-11-17
# ------------------------------
# Main rendering class. All render code except rasterization
# and matrix generation is contained in this class.
################################

# import validation
fail = False
try:
  from tkinter import *
except Exception:
  print("ERROR: Could not import 'tkinter' module.")
  fail = True
try:
  from PIL import Image, ImageTk
except Exception:
  print("ERROR: Could not import 'PIL' module. Is pillow installed?")
  fail = True
try:
  from time import clock
except Exception:
  print("ERROR: Could not import 'time' module.")
  fail = True

try:
  from model_creator import *
except Exception:
  print("ERROR: Could not import 'model_creator' module. Is it in this folder?")
  fail = True
try:
  from transforms import *
except Exception:
  print("ERROR: Could not import 'transforms' module. Is it in this folder?")
  fail = True
try:
  from rasterizer import *
except Exception:
  print("ERROR: Could not import 'rasterizer' module. Is it in this folder?")
  fail = True
try:
  from scene_parser import *
except Exception:
  print("ERROR: Could not import 'scene_parser' module. Is it in this folder?")
  fail = True
if fail:
  input("Press ENTER to close this window.")
  exit()


################
# Display: Tkinter object that displays models.
class Display(Frame):

  BG_COLOR = "#CCCCFF"
  AMBIENT = 0.3
  ALPHA = 4
  SPECULAR = (1.0,1.0,1.0)

  # shading options
  SHADE_AMBIENT = 0x1
  SHADE_DIFFUSE = 0x2
  SHADE_SPECULAR = 0x4
  SHADE_ALL = SHADE_AMBIENT | SHADE_DIFFUSE | SHADE_SPECULAR

  # resolution options
  RES_LOW = "RES_LOW"
  RES_MEDIUM = "RES_MEDIUM"
  RES_HIGH = "RES_HIGH"
  RES_ULTRA = "RES_ULTRA" # NOTE: using this or below takes a long time to render
  RES_INSANE = "RES_INSANE"
  RES_REALISTIC = "RES_REALISTIC"

  ########
  # Creates Tk and internal objects.
  #   Params:
  #     master : Tkinter master widget
  def __init__(self, master):
    super().__init__(master)

    self._canvas = Canvas(self, width = 400, height = 400, bg = Display.BG_COLOR)
    self._canvas.grid(row = 0, column = 0)

    self._zoomDist = 30
    self._cameraLoc = Point(theta = pi, phi = pi/4, radius = self._zoomDist)
    self._cameraDir = Point(theta = 0, phi = 3*pi/4, radius = 1)

    self.load_objects()

    self._buffer = Image.new(mode = 'RGB',
                             size = (int(self._canvas.cget('width')),
                                     int(self._canvas.cget('height'))))

  ########
  # Loads objects into frame. Also deletes any rendered scene.
  #   Params:
  #     filename   : Specifies file of scene to be loaded
  #     resolution : Specifies polygon resolution of objects.
  #                  One of RES_LOW, RES_MEDIUM, RES_HIGH, or RES_ULTRA.
  def load_objects(self, filename = "scene1.txt", resolution = RES_MEDIUM):
    self._canvas.delete("all")

    self._objects, self._lights = parse_scene(filename, resolution = resolution)

    self._camViewObjects = []
    self._perspectiveObjects = []
    for i in range(len(self._objects)):
      self._camViewObjects.append(Model(points = self._objects[i].points,
                                          norms = self._objects[i].norms,
                                          tris = self._objects[i].tris))
      self._perspectiveObjects.append(Model(points = self._objects[i].points,
                                            norms = self._objects[i].norms,
                                            tris = self._objects[i].tris))

    self._camViewLights = []
    for i in range(len(self._lights)):
      self._camViewLights.append(Light(color = self._lights[i].color))

  ########
  # Displays a new PIL.Image object on the canvas.
  #   Params:
  #     newImage : New image to be displayed.
  def _update_image(self, newImage):
    self._canvas.delete("all")
    size = newImage.size
    self._image = ImageTk.PhotoImage(image = newImage)
    self._canvas.create_image(0, 0, anchor = NW, image = self._image)
    self._canvas.config(width = size[0], height = size[1])

  ########
  # Renders and displays the scene with the provided shading selection.
  #   Params:
  #     shadeType   : The shading to be used.
  #                   One of SHADE_AMBIENT, SHADE_DIFFUSE, SHADE_SPECULAR, or SHADE_ALL.
  #     castShadows : If True, renders shadows. Disabling speeds up performance.
  def render(self, shadeType = SHADE_ALL, castShadows = True):
    elapsed = 0
    self._buffer = Image.new(mode = 'RGB',
                             size = (int(self._canvas.cget('width')),
                                     int(self._canvas.cget('height'))))

    viewx = float(self._canvas.cget("width"))
    viewy = float(self._canvas.cget("height"))
    zBuffer = []
    for i in range(int(viewx)):
      zBuffer.append([None]*int(viewy))
    
    viewMax = max((viewx, viewy))
    viewMin = min((viewx, viewy))
    
    dispMat = ( # for conversion to canvas coordinates
               translate(x = viewx / 2, y = viewy / 2) *
               scale(y = -1) *
               scale(x = viewMin / 2, y = viewMin / 2) *
               perspective_project()
              )
    viewMat = ( # for conversion from world space to view space
               rotateX(pi -self._cameraDir.phi) *
               rotateZ(-pi/2 -self._cameraDir.theta) *
               translate(-self._cameraLoc.x, -self._cameraLoc.y, -self._cameraLoc.z)
              )

    viewNormMat = (
                   rotateX(pi -self._cameraDir.phi) *
                   rotateZ(-pi/2 -self._cameraDir.theta)
                  )

    for l in range(len(self._lights)):
      res = viewMat * self._lights[l].mat()
      self._camViewLights[l].loc.set(matrix = res)
    
    for o in range(len(self._objects)):
      obj = self._objects[o]
      
      objMat = (
                translate(x = obj.offset.x, y = obj.offset.y, z = obj.offset.z) *
                rotateZ(obj.rotation.theta) *
                rotateY(obj.rotation.phi) *
                scale(x = obj.scale.x, y = obj.scale.y, z = obj.scale.z)
               )
      objNormMat = (
                    rotateZ(obj.rotation.theta) *
                    rotateY(obj.rotation.phi) *
                    scale_norm(x = obj.scale.x, y = obj.scale.y, z = obj.scale.z)
                   )

      for i in range(len(obj.points)):
        res = viewMat * objMat * obj.points[i].mat()
        res2 = dispMat * res
        res2 = res2 / res2.item((3,0)) # normalize
        self._camViewObjects[o].points[i].set(matrix = res)
        self._perspectiveObjects[o].points[i].set(matrix = res2)

      for i in range(len(obj.norms)):
        res = viewNormMat * objNormMat * obj.norms[i].mat()
        self._camViewObjects[o].norms[i].set(matrix = res)
        self._camViewObjects[o].norms[i].normalize() # need it in unit-vector format
        self._perspectiveObjects[o].norms[i].set(matrix = res)

      viewWorldMat = linalg.inv(viewMat) # for conversion from view space to world space
      objMats = []
      for obj in self._objects:
        objMat = ( # for conversion from model space to world space
                  translate(x = obj.offset.x, y = obj.offset.y, z = obj.offset.z) *
                  rotateZ(obj.rotation.theta) *
                  rotateY(obj.rotation.phi) *
                  scale(x = obj.scale.x, y = obj.scale.y, z = obj.scale.z)
                 )
        worldObjMat = linalg.inv(objMat) # for conversion from world space to model space
        objMats.append(worldObjMat)

      for tri in self._perspectiveObjects[o].tris:
        if self._perspectiveObjects[o].norms[tri.norm].z < 0: # skip if definitely not facing us
          continue

        p1 = self._camViewObjects[o].points[tri.p1]
        p2 = self._camViewObjects[o].points[tri.p2]
        p3 = self._camViewObjects[o].points[tri.p3]
        c1 = self._shade(point = p1,
                         normal = self._camViewObjects[o].norms[tri.norm],
                         color = tri.color,
                         specular = self._camViewObjects[o].specular,
                         diffuse = self._camViewObjects[o].diffuse,
                         shadeType = shadeType,
                         viewWorldMat = viewWorldMat,
                         objMats = objMats,
                         myObj = o,
                         castShadows = castShadows)
        c2 = self._shade(point = p2,
                         normal = self._camViewObjects[o].norms[tri.norm],
                         color = tri.color,
                         specular = self._camViewObjects[o].specular,
                         diffuse = self._camViewObjects[o].diffuse,
                         shadeType = shadeType,
                         viewWorldMat = viewWorldMat,
                         objMats = objMats,
                         myObj = o,
                         castShadows = castShadows)
        c3 = self._shade(point = p3,
                         normal = self._camViewObjects[o].norms[tri.norm],
                         color = tri.color,
                         specular = self._camViewObjects[o].specular,
                         diffuse = self._camViewObjects[o].diffuse,
                         shadeType = shadeType,
                         viewWorldMat = viewWorldMat,
                         objMats = objMats,
                         myObj = o,
                         castShadows = castShadows)

        start = clock()
        render_triangle(p1 = self._perspectiveObjects[o].points[tri.p1],
                        p2 = self._perspectiveObjects[o].points[tri.p2],
                        p3 = self._perspectiveObjects[o].points[tri.p3],
                        c1 = c1,
                        c2 = c2,
                        c3 = c3,
                        zBuffer = zBuffer)
        elapsed += clock() - start

    start = clock()
    for x in range(int(viewx)):
      for y in range(int(viewy)):
        if zBuffer[x][y] != None:
          self._buffer.putpixel(xy=(x,y),value=tuple(zBuffer[x][y][1:]))

    self._update_image(self._buffer)
    elapsed += clock() - start

    return elapsed

  ########
  # Moves the camera to a new location. Camera is always looking at origin.
  #   Params:
  #     zoom     : Distance from the origin.
  #     incline  : View vector's phi component, from positive z-axis.
  #     rotation : View vector's theta component, from positive x-axis.
  def update_camera(self, zoom, incline, rotation):
    self._zoomDist = zoom
    self._cameraLoc = Point(theta = pi + rotation * pi,
                            phi = pi - incline * pi,
                            radius = self._zoomDist)
    self._cameraDir = Point(theta = rotation * pi, phi = incline * pi, radius = 1)

  ########
  # Determines the color of a point using a simplified lighting model.
  #   Params:
  #     point        : Point to be colored
  #     normal       : Surface normal at point
  #     color        : Color of point
  #     specular     : Specular coefficient for the point
  #     diffuse      : Diffuse coefficient for the point
  #     shadeType    : The shading to be used.
  #                    One of SHADE_AMBIENT, SHADE_DIFFUSE, SHADE_SPECULAR, or SHADE_ALL.
  #     viewWorldMat : View -> World matrix
  #     objMats      : World -> Object matrices
  #     myObj        : Index of the object this point belongs to
  #     castShadows  : If True, renders shadows. Disabling speeds up performance.
  def _shade(self,
             point,
             normal,
             color,
             specular,
             diffuse,
             shadeType,
             viewWorldMat,
             objMats,
             myObj,
             castShadows):

    if shadeType & Display.SHADE_AMBIENT: # ambient portion
      r = Display.AMBIENT * color[0]
      g = Display.AMBIENT * color[1]
      b = Display.AMBIENT * color[2]
    else: # no ambient
      r = 0
      g = 0
      b = 0

    viewdir = Point(x = -point.x, y = -point.y, z = -point.z)
    viewdir.normalize()

    if shadeType & (Display.SHADE_DIFFUSE | Display.SHADE_SPECULAR):
      for l in self._camViewLights:
        lightdir = Point(matrix = l.mat() - point.mat())
        att = lightdir.att()
        lightdir.normalize()
        dotLightNorm = lightdir.dot(normal)

        if dotLightNorm > 0: # isVisible
          useLight = True

          if castShadows:
            for o in range(len(self._objects)):
              if o == myObj: # don't process our own object
                continue
              worldObjMat = objMats[o]
              p1 = Point(matrix = worldObjMat * viewWorldMat * l.loc.mat())
              p2 = Point(matrix = worldObjMat * viewWorldMat * point.mat())
              # determine if occluded
              if self._objects[o].intersects(p1 = p1, p2 = p2):
                useLight = False
                break
          if not useLight:
            continue # skip to next light


          # Formula from: http://math.stackexchange.com/questions/13261/how-to-get-a-reflection-vector
          if shadeType & Display.SHADE_SPECULAR:
            dot = lightdir.dot(normal)
            reflectdir = Point(matrix = lightdir.mat() - 2 * dot * normal.mat())

          if shadeType & Display.SHADE_DIFFUSE: # diffuse portion
            r += att * 10 * l.color[0] * color[0] * diffuse * dotLightNorm
            g += att * 10 * l.color[1] * color[1] * diffuse * dotLightNorm
            b += att * 10 * l.color[2] * color[2] * diffuse * dotLightNorm

          if shadeType & Display.SHADE_SPECULAR: # specular portion
            dot = -reflectdir.dot(viewdir)
            if dot > 0:
              r += att * 10 * l.color[0] * Display.SPECULAR[0] * specular * dot ** Display.ALPHA
              g += att * 10 * l.color[1] * Display.SPECULAR[1] * specular * dot ** Display.ALPHA
              b += att * 10 * l.color[2] * Display.SPECULAR[2] * specular * dot ** Display.ALPHA

    # if r > 1 or g > 1 or b > 1:
    #   print("ERROR: {:.2f},{:.2f},{:.2f}".format(r,g,b))
    return (min((255, int(255*r))),
            min((255, int(255*g))),
            min((255, int(255*b))))
    # return color
# Display
################


########
# Main code architecture if run standalone.
# Creates and renders a display object with default parameters.
if __name__ == "__main__":
  root = Tk()
  d = Display(root)
  d.pack()

  d.render()

  root.mainloop()