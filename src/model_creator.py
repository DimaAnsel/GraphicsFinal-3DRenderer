################################
# model_creator.py
# Noah Ansel
# nba38
# 2016-11-17
# ------------------------------
# Generates models of different resolutions
# for use in main rendering program.
################################

# import validation
fail = False
try:
  from numpy import *
except Exception:
  print("ERROR: Could not import 'numpy' module.")
  fail = True
try:
  from math import *
except Exception:
  print("ERROR: Could not import 'math' module.")
  fail = True
try:
  from copy import copy
except Exception:
  print("ERROR: Could not import 'copy' module.")
  fail = True
try:
  from time import clock
except Exception:
  print("ERROR: Could not import 'time' module.")
  fail = True
try:
  import warnings
except Exception:
  print("ERROR: Could not import 'warnings' module.")
  fail = True
if fail:
  input("Press ENTER to close this window.")
  exit()



# ignore unnecessary warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)

# If set to true, models will use minimal number of points. This slows down
# model generation exponentially.
USE_MINIMAL_POINTS = False

# output file (if run standalone)
OUTPUT_FILE = "models.txt"

# Flags used for cube_intersect() preliminary intersection tests.
POS_X = 0x1
POS_Y = 0x2
POS_Z = 0x4
NEG_X = 0x8
NEG_Y = 0x10
NEG_Z = 0x20
IN_X = 0x40
IN_Y = 0x80
IN_Z = 0x100
EXT = POS_X | POS_Y | POS_Z | NEG_X | NEG_Y | NEG_Z

########
# Determines if the line between 2 points intersects a cube (centered at origin).
# Loosely based on Cohen–Sutherland clipping algorithm discussed in lecture.
#   Params:
#     p1, p2 : Endpoints of line to test for intersection.
#   Returns: True if detects intersection, False otherwise
def cube_intersect(size, p1, p2):
  minBound = -size / 2
  maxBound = size / 2
  p1sides =  POS_X if (p1.x >= maxBound) else (NEG_X if (p1.x <= minBound) else IN_X)
  p1sides |= POS_Y if (p1.y >= maxBound) else (NEG_Y if (p1.y <= minBound) else IN_Y)
  p1sides |= POS_Z if (p1.z >= maxBound) else (NEG_Z if (p1.z <= minBound) else IN_Z)

  p2sides =  POS_X if (p2.x >= maxBound) else (NEG_X if (p2.x <= minBound) else IN_X)
  p2sides |= POS_Y if (p2.y >= maxBound) else (NEG_Y if (p2.y <= minBound) else IN_Y)
  p2sides |= POS_Z if (p2.z >= maxBound) else (NEG_Z if (p2.z <= minBound) else IN_Z)

  comb = p1sides & p2sides
  if comb & EXT or p1sides == p2sides: # both on same side
    return False
  elif ((comb & IN_X and comb & IN_Y) or 
        (comb & IN_Y and comb & IN_Z) or 
        (comb & IN_Z and comb & IN_X)): # on opposite sides
    return True
  else: # check each face to see if it intersects
    lVec = Point(matrix = p2.mat() - p1.mat())
    maxD = lVec.mag()
    lVec.normalize() # make unit vect
    if lVec.x != 0:
      dBot = (minBound - p1.x) / lVec.x
      dTop = (maxBound - p1.x) / lVec.x
      if 0 < dBot and dBot < maxD:
        res = Point(matrix = p1.mat() + dBot * lVec.mat())
        if (minBound < res.y and res.y < maxBound and
            minBound < res.z and res.z < maxBound):
          return True
      if 0 < dTop and dTop < maxD:
        res = Point(matrix = p1.mat() + dTop * lVec.mat())
        if (minBound < res.y and res.y < maxBound and
            minBound < res.z and res.z < maxBound):
          return True
    if lVec.y != 0:
      dBot = (minBound - p1.y) / lVec.y
      dTop = (maxBound - p1.y) / lVec.y
      if 0 < dBot and dBot < maxD:
        res = Point(matrix = p1.mat() + dBot * lVec.mat())
        if (minBound < res.x and res.x < maxBound and
            minBound < res.z and res.z < maxBound):
          return True
      if 0 < dTop and dTop < maxD:
        res = Point(matrix = p1.mat() + dTop * lVec.mat())
        if (minBound < res.x and res.x < maxBound and
            minBound < res.z and res.z < maxBound):
          return True
    if lVec.z != 0:
      dBot = (minBound - p1.z) / lVec.z
      dTop = (maxBound - p1.z) / lVec.z
      if 0 < dBot and dBot < maxD:
        res = Point(matrix = p1.mat() + dBot * lVec.mat())
        if (minBound < res.x and res.x < maxBound and
            minBound < res.y and res.y < maxBound):
          return True
      if 0 < dTop and dTop < maxD:
        res = Point(matrix = p1.mat() + dTop * lVec.mat())
        if (minBound < res.x and res.x < maxBound and
            minBound < res.y and res.y < maxBound):
          return True
    return False

########
# Determines if the line between 2 points intersects a sphere (centered at origin).
# Formula from: https://en.wikipedia.org/wiki/Line%E2%80%93sphere_intersection
#   Params:
#     p1, p2 : Endpoints of line to test for intersection.
#   Returns: True if detects intersection, False otherwise
def sphere_intersect(size, p1, p2):
  lVec = Point(matrix = p2.mat() - p1.mat())
  maxD = lVec.mag()
  lVec.normalize() # make unit vector
  res = (lVec.dot(p1))**2 - (p1.x * p1.x + p1.y * p1.y + p1.z * p1.z) + size ** 2
  if res < 0:
    return False
  else:
    d = -lVec.dot(p1) - sqrt(res)
    if 0 < d and d < maxD: # check that inside line segment
      return True
    else:
      return False

################
# Point: Container class for a single 3-D point.
#   Members:
#     x, y, z : Coordinates of point in 3-space.
#     phi     : Declination from positive z-axis. None if not provided on init
#     theta   : Clockwise rotation from positive x-axis. None if not provided on init
#     radius  : Distance from origin. None if not provided on init.
class Point:

  C1 = 0.4
  C2 = 0.3
  C3 = 0.3

  ########
  # Initializes the point. Precedence of parameters is: point, matrix,
  # spherical coords, Cartesian coords.
  #   Params:
  #     point   : Point to generate copy of. Supercedes other parameters.
  #     x, y, z : Coordinates of point in 3-space.
  #     phi     : Declination from positive z-axis. Supercedes x,y,z.
  #     theta   : Clockwise rotation from positive x-axis. Supercedes x,y,z.
  #     radius  : Distance from origin. Supercedes x,y,z.
  #     matrix  : Matrix to set point from. Supersedes spherical and Cartesian coordinates.
  def __init__(self,
               point = None,
               x = 0,
               y = 0,
               z = 0,
               theta = None,
               phi = None,
               radius = None,
               matrix = None):
    if point != None:
      self.x = point.x
      self.y = point.y
      self.z = point.z
      self.phi    = point.phi
      self.theta  = point.phi
      self.radius = point.radius
      return
    elif matrix != None:
      self.x = matrix.item((0,0))
      self.y = matrix.item((1,0))
      self.z = matrix.item((2,0))
      self.phi = None
      self.theta = None
      self.radius = None
    elif theta != None and phi != None and radius != None:
      self.x = radius * sin(phi) * cos(theta)
      self.y = radius * sin(phi) * sin(theta)
      self.z = radius * cos(phi)
    else:
      self.x = x
      self.y = y
      self.z = z
    # always save for reference
    self.phi = phi
    self.theta = theta
    self.radius = radius

  ########
  # Generates a string representation of the point.
  # Coordinates are comma-separated 9-decimal-precision floats.
  #   Returns: String representation of the point.
  def __str__(self):
    return "{:.9f},{:.9f},{:.9f}".format(self.x, self.y, self.z)

  ########
  # Determines if two points are identical.
  #   Params:
  #     other : Point to compare with
  #   Returns: True if identical, False otherwise
  def __eq__(self, other):
    if other == None:
      return False
    elif isinstance(other, Point):
      return (self.x == other.x and self.y == other.y and self.z == other.z)
    else:
      raise TypeError("Can only compare of type Point.")

  ########
  # Returns a vector matrix representation for translations.
  def mat(self):
    return mat([[self.x], [self.y], [self.z], [1]])

  ########
  # Computes the attenuation factor of this point for shading.
  def att(self):
    return min(1 / (Point.C1 + Point.C2 * self.mag() + Point.C3 * (self.x * self.x + self.y * self.y + self.z * self.z)),
               1)

  ########
  # Computes the magnitude of this vector.
  def mag(self):
    return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

  ########
  # Computes the spherical coordinates of this point.
  #   Returns: θ, ϕ, and radius of point in spherical coordinates
  def to_spherical(self):
    r = self.mag()
    phi   = acos(self.z/r)
    theta = atan2(self.y, self.x)
    return (theta, phi, r)

  ########
  # Converts the given point into a unit vector.
  def normalize(self):
    mag = self.mag()

    self.x /= mag
    self.y /= mag
    self.z /= mag

  ########
  # Sets a point from a vector matrix.
  #   Params:
  #     matrix : Numpy matrix to set given point from.
  def set(self, matrix = None):
    if matrix != None:
      self.x = matrix.item((0,0))
      self.y = matrix.item((1,0))
      self.z = matrix.item((2,0))

  ########
  # Computes the dot product of two points.
  #   Params:
  #     other : Point to compute dot product with.
  #   Returns: Computed dot product of two points.
  def dot(self, other):
    return self.x * other.x + self.y * other.y + self.z * other.z
# Point
################


################
# Model: Class containing all information about a single 3-D model.
#   Members:
#     name          : A string name for the model
#     points        : List containing all points in model
#     norms         : List containing all surface normals in model
#     tris          : List containing all triangles in model
#     offset        : Offset of this model from the origin, stored as a Point.
#     rotation      : Rotation of this model, stored as a Point.
#     scale         : Scaling of this model, stored as a Point.
#     color         : 3-tuple of RGB format representing model's color
#     specular      : Specular coefficient. Higher means specular lighting is brighter.
#     diffuse       : Diffuse coefficient. Higher means diffuse lighting is brighter.
#     _size         : Size parameter used when calling intersectFcn
#     _intersectFcn : Function to be used when determining if given line segment
#                     intersects with this model. See intersects().
class Model:

  DEFAULT_NAME = "unnamedModel"
  DEFAULT_COLOR = (1.0, 1.0, 1.0)
  DEFAULT_SPECULAR = 0.6
  DEFAULT_DIFFUSE = 0.5

  ################
  # Triangle: Interior class to Model that must refer to its parent.
  # Should not be instantiated outside of Model's methods.
  #   Members:
  #     _parent    : Reference to model used for points and norms lists
  #     p1, p2, p3 : Indexes to parent's points list
  #     norm       : Index to parent's norms list
  #     color      : 3-tuple of RGB format representing triangle's color
  #                  If None or not provided, uses parent's color
  class Triangle:

    ########
    # Generates a new triangle.
    #   Params:
    #     parent     : Reference to model used for points and norms lists
    #     p1, p2, p3 : Indexes to parent's points list
    #     norm       : Index to parent's norms list
    #     color      : 3-tuple of RGB format representing triangle's color
    #                  If None or not provided, uses parent's color
    #     triangle   : Triangle to copy information from.
    def __init__(self, parent, p1 = None, p2 = None, p3 = None, norm = None, color = None, triangle = None):
      self._parent = parent
      if triangle != None:
        self.p1 = triangle.p1
        self.p2 = triangle.p2
        self.p3 = triangle.p3
        self.norm = triangle.norm
        self.color = triangle.color
      else:
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.norm = norm

        if color != None:
          self.color = color
        else:
          self.color = parent.color


    ########
    # Generates a string representation of this triangle.
    # Points are separated by spaces, with the last point being the normal.
    #   Returns: String representation of the triangle
    def __str__(self):
      return "{} {} {} {}".format(str(self._parent.points[self.p1]),
                                  str(self._parent.points[self.p2]),
                                  str(self._parent.points[self.p3]),
                                  str(self._parent.norms[self.norm]))
  # Triangle
  ################

  ########
  # Generates a model with the given name and parameters.
  #   Params:
  #     name         : A string name for this model
  #     color        : A 3-tuple of RGB format representing model's color
  #     points       : List of points to associate with this model.
  #     norms        : List of normals to associate with this model.
  #     tris         : List of triangles to associate with this model.
  #     offset       : Offset of this model from the origin, stored as a Point.
  #     rotation     : Rotation of this model, stored as a Point.
  #     scale        : Scaling of this model, stored as a Point.
  #     specular     : Specular coefficient. Higher means specular lighting is brighter.
  #     diffuse      : Diffuse coefficient. Higher means diffuse lighting is brighter.
  #     size         : Size parameter used when calling intersectFcn
  #     intersectFcn : Function to be used when determining if given line segment
  #                    intersects with this model. See intersects().
  def __init__(self,
               name = DEFAULT_NAME,
               color = None,
               points = None,
               norms = None,
               tris = None,
               offset = None,
               rotation = None,
               scale = None,
               specular = DEFAULT_SPECULAR,
               diffuse = DEFAULT_DIFFUSE,
               size = 1,
               intersectFcn = cube_intersect):
    self.name = name

    self.points = []
    if points != None:
      for p in points:
        self.points.append(Point(p))
    
    self.norms = []
    if norms != None:
      for n in norms:
        self.norms.append(Point(n))
    
    self.tris = []
    if tris != None:
      for t in tris:
        self.tris.append(Model.Triangle(self, triangle = t))

    if offset != None:
      self.offset = Point(offset)
    else:
      self.offset = Point(x = 0, y = 0, z = 0)

    if rotation != None:
      self.rotation = Point(rotation)
    else:
      self.rotation = Point(phi = 0, theta = 0, radius = 1)

    if scale != None:
      self.scale = Point(rotation)
    else:
      self.scale = Point(x = 1, y = 1, z = 1)

    if color != None:
      self.color = color
    else:
      self.color = copy(Model.DEFAULT_COLOR)

    self.specular = specular
    self.diffuse = diffuse

    self._size = size
    self._intersectFcn = intersectFcn

  ########
  # Generates a multi-line string representation of the model.
  # Each line represents a triangle in the model.
  #   Returns: String representation of the model
  def __str__(self):
    retStr = "{} {} ({},{},{})\n".format(self.name,
                                         len(self.tris),
                                         self.color[0],
                                         self.color[1],
                                         self.color[2])
    for tri in self.tris:
      retStr += str(tri) + "\n"
    return retStr

  ########
  # Creates a new normal and appends it to the model's list. If normal already exists
  # in list and USE_MINIMAL_POINTS set to True, does not create new normal.
  #   Params:
  #     x, y, z : Cartesian coordinates of the point.
  #     phi     : Declination from positive z-axis.
  #     theta   : Rotation clockwise from positive x-axis.
  #     radius  : Distance from the origin.
  #   Returns: Index of the normal
  def add_norm(self, x = None, y = None, z = None, phi = None, theta = None, radius = None):
    if x != None and y != None and z != None:
      if USE_MINIMAL_POINTS:
        for i in range(len(self.norms)): # search for already existing point
          if x == self.norms[i].x and y == self.norms[i].y and z == self.norms[i].z:
            return i
      p = Point(x = x, y = y, z = z)
      self.norms.append(p)
      return len(self.norms) - 1
    elif phi != None and theta != None and radius != None:
      if USE_MINIMAL_POINTS:
        for i in range(len(self.norms)):
          if phi == self.norms[i].phi and theta == self.norms[i].theta and radius == self.norms[i].radius:
            return i
      p = Point(phi = phi, theta = theta, radius = radius)
      self.norms.append(p)
      return len(self.norms) - 1
    raise ValueError("Unrecognized params: x={} y={} z = {} phi={} theta={} radius={}".format(x,y,z,phi,theta,radius))

  ########
  # Creates a new point and appends it to the model's list. If point already exists
  # in list and USE_MINIMAL_POINTS set to True, does not create new point.
  #   Params:
  #     x, y, z : Cartesian coordinates of the point.
  #     phi     : Declination from positive z-axis.
  #     theta   : Rotation clockwise from positive x-axis.
  #     radius  : Distance from the origin.
  #   Returns: Index of the point
  def add_point(self, x = None, y = None, z = None, phi = None, theta = None, radius = None):
    if x != None and y != None and z != None:
      if USE_MINIMAL_POINTS:
        for i in range(len(self.points)): # search for already existing point
          if x == self.points[i].x and y == self.points[i].y and z == self.points[i].z:
            return i
      p = Point(x = x, y = y, z = z)
      self.points.append(p)
      return len(self.points) - 1
    elif phi != None and theta != None and radius != None:
      if USE_MINIMAL_POINTS:
        for i in range(len(self.points)):
          if phi == self.points[i].phi and theta == self.points[i].theta and radius == self.points[i].radius:
            return i
      p = Point(phi = phi, theta = theta, radius = radius)
      self.points.append(p)
      return len(self.points) - 1
    raise ValueError("Unrecognized params: x={} y={} z = {} phi={} theta={} radius={}".format(x,y,z,phi,theta,radius))

  ########
  # Creates a new triangle and appends it to the model's list.
  #   Params:
  #     p1, p2, p3 : Indexes of triangle corners in the model's points array.
  #     norm       : Index of triangle normal in the model's norms array.
  #   Returns: Index of the new triangle
  def add_tri(self, p1, p2, p3, norm):
    tri = Model.Triangle(parent = self, p1 = p1, p2 = p2, p3 = p3, norm = norm)
    self.tris.append(tri)
    return len(self.tris) - 1

  ########
  # Divides all triangles in model into 4 smaller triangles. Used to generate
  # higher resolution cube.
  def subdivide_triangles(self):
    for i in range(len(self.tris)-1, -1, -1): # from back to not interfere when inserting
      tri = self.tris[i]

      midX = (self.points[tri.p1].x + self.points[tri.p2].x) / 2
      midY = (self.points[tri.p1].y + self.points[tri.p2].y) / 2
      midZ = (self.points[tri.p1].z + self.points[tri.p2].z) / 2
      mid12idx = self.add_point(x = midX, y = midY, z = midZ)

      midX = (self.points[tri.p2].x + self.points[tri.p3].x) / 2
      midY = (self.points[tri.p2].y + self.points[tri.p3].y) / 2
      midZ = (self.points[tri.p2].z + self.points[tri.p3].z) / 2
      mid23idx = self.add_point(x = midX, y = midY, z = midZ)

      midX = (self.points[tri.p3].x + self.points[tri.p1].x) / 2
      midY = (self.points[tri.p3].y + self.points[tri.p1].y) / 2
      midZ = (self.points[tri.p3].z + self.points[tri.p1].z) / 2
      mid31idx = self.add_point(x = midX, y = midY, z = midZ)

      newTri = Model.Triangle(parent = self, p1 = mid23idx, p2 = mid31idx, p3 = mid12idx, norm = tri.norm)
      self.tris.insert(i + 1, newTri)

      newTri = Model.Triangle(parent = self, p1 = mid31idx, p2 = mid23idx, p3 = tri.p3, norm = tri.norm)
      self.tris.insert(i + 1, newTri)      

      newTri = Model.Triangle(parent = self, p1 = mid12idx, p2 = tri.p2, p3 = mid23idx, norm = tri.norm)
      self.tris.insert(i + 1, newTri)

      # must occur after above
      tri.p2 = mid12idx
      tri.p3 = mid31idx

  ########
  # Determines if the line segment intersects the given model using the
  # intersect function provided on initialization.
  #   Params:
  #     p1, p2 : Line endpoints.
  #   Returns: True if segment intersects model, False otherwise
  def intersects(self, p1, p2):
    return self._intersectFcn(self._size, p1, p2)
# Model
################

################
# Light: Class containing all information about a point light.
#   Members:
#     loc   : Location of light in the world space.
#     color : Light color as a 3-tuple of RGB values between 0 and 1.
class Light:

  DEFAULT_COLOR = (1.0, 1.0, 1.0)

  ########
  # Initializes internal variables.
  #   Params:
  #     x, y, z : Location of light in the world space.
  #     color   : Light color as a 3-tuple of RGB values between 0 and 1.
  def __init__(self, x = 0, y = 0, z = 0, color = None):
    self.loc = Point(x = x, y = y, z = z)
    if color != None:
      self.color = color
    else:
      self.color = copy(Light.DEFAULT_COLOR)

  ########
  # Returns a vector matrix representation of location for translations.
  def mat(self):
    return self.loc.mat()
# Light
################

########
# Generates an approximation of a sphere with provided radius.
#   Params:
#     radius       : Radius of sphere
#     numLaterals  : Number of lateral divisions
#     numVerticals : Number of vertical (longitudinal) divisions
#     color        : Model color as a 3-tuple of RGB values between 0 and 1. 
#   Returns: Model object approximation of sphere
def generate_sphere(radius = 1, numLaterals = 4, numVerticals = 6, color = Model.DEFAULT_COLOR):
  m = Model(color = color, size = radius * 2, intersectFcn = sphere_intersect)

  thetaStep = 2 * pi / numVerticals # clockwise rot from x
  thetaInc = thetaStep * 2 / numLaterals # each ring is shifted by 2/numLaterals rotations
  phiStep = pi / numLaterals # declination from pos z

  startTheta = 0
  rightTheta = startTheta

  # goes clockwise from x-axis
  for i in range(numVerticals): # for each vertical strip
    botPhi = 0
    leftTheta = startTheta
    rightTheta = startTheta + thetaStep
    startTheta += thetaStep

    botLeftIdx = m.add_point(phi = 0, theta = leftTheta, radius = radius)
    botLeft = m.points[botLeftIdx]


    botRightIdx = m.add_point(phi = 0, theta = rightTheta, radius = radius)
    botRight = m.points[botRightIdx]

    # goes down from z-axis
    for j in range(numLaterals):
      botPhi += phiStep
      leftTheta += thetaInc
      rightTheta += thetaInc

      topLeft = botLeft # copy previous data
      topLeftIdx = botLeftIdx
      topRight = botRight
      topRightIdx = botRightIdx
      
      botLeftIdx = m.add_point(phi = botPhi, theta = leftTheta, radius = radius)
      botLeft = m.points[botLeftIdx]
      
      if j > 0: # not the top, so include inverted triangle
        phi = (topLeft.phi + topRight.phi + botLeft.phi) / 3
        theta = (topLeft.theta + topRight.theta + botLeft.theta) / 3
        
        normIdx = m.add_norm(phi = phi, theta = theta, radius = radius)
        norm = m.norms[normIdx]
        
        m.add_tri(p1 = topLeftIdx, p2 = topRightIdx, p3 = botLeftIdx, norm = normIdx)
      if j < numLaterals - 1: # not the bottom, so include upright triangle
        botRightIdx = m.add_point(phi = botPhi, theta = rightTheta, radius = radius)
        botRight = m.points[botRightIdx]

        phi = (topRight.phi + botLeft.phi + botRight.phi) / 3
        theta = (topRight.theta + botLeft.theta + botRight.theta) / 3
        
        normIdx = m.add_norm(phi = phi, theta = theta, radius = radius)
        norm = m.norms[normIdx]

        m.add_tri(p1 = topRightIdx, p2 = botLeftIdx, p3 = botRightIdx, norm = normIdx)

  return m

########
# Generates a cube with provided side length.
#   Params:
#     size        : Side length
#     trisPerSide : Triangles to generate per side. Must be odd power of 2.
#     color       : Model color as a 3-tuple of RGB values between 0 and 1.
#   Returns: Model object of cube
def generate_cube(size = 1, trisPerSide = 2, color = Model.DEFAULT_COLOR):
  m = Model(color = color, size = 1)

  halfSize = size / 2

  # number of times to recursively subdivide triangles
  
  if trisPerSide % 2 != 0 or int(log2(trisPerSide)) % 2 == 0: # input validation
    raise ValueError("Invalid number of triangles. Must be odd power of 2.")
  
  numDivisions = (int(log2(trisPerSide)) - 1) // 2

  # generate pos x-y and neg x-y separately
  for mul in (-1, 1):
    # upper A tris
    p1idx = m.add_point(x = mul * halfSize, y = -mul * halfSize, z = halfSize)
    p1 = m.points[p1idx]
    
    p2idx = m.add_point(x = mul * halfSize, y = -mul * halfSize, z = -halfSize)
    p2 = m.points[p2idx]
    
    p3idx = m.add_point(x = mul * halfSize, y = mul * halfSize, z = halfSize)
    p3 = m.points[p3idx]

    nIdx = m.add_norm(x = mul, y = 0, z = 0)
    n = m.norms[nIdx]
    
    m.add_tri(p1 = p1idx, p2 = p2idx, p3 = p3idx, norm = nIdx)

    # lower A tris
    p1idx = m.add_point(x = mul * halfSize, y = mul * halfSize, z = -halfSize)
    p1 = m.points[p1idx]

    m.add_tri(p1 = p1idx, p2 = p3idx, p3 = p2idx, norm = nIdx)

    # lower B tris
    p2idx = m.add_point(x = -mul * halfSize, y = mul * halfSize, z = -halfSize)
    p2 = m.points[p2idx]

    nIdx = m.add_norm(x = 0, y = mul, z = 0)
    n = m.norms[nIdx]
    
    m.add_tri(p1 = p1idx, p2 = p2idx, p3 = p3idx, norm = nIdx)

    # upper B tris
    p1idx = m.add_point(x = -mul * halfSize, y = mul * halfSize, z = halfSize)
    p1 = m.points[p1idx]

    m.add_tri(p1 = p1idx, p2 = p3idx, p3 = p2idx, norm = nIdx)

    p2idx = m.add_point(x = mul * halfSize, y = -mul * halfSize, z = halfSize)
    p2 = m.points[p2idx]
    
    nIdx = m.add_norm(x = 0, y = 0, z = 1)
    n = m.norms[nIdx]
    
    m.add_tri(p1 = p3idx, p2 = p1idx, p3 = p2idx, norm = nIdx)

    # bot tris
    p1idx = m.add_point(x = mul * halfSize, y = -mul * halfSize, z = -halfSize)
    p1 = m.points[p1idx]
    
    p2idx = m.add_point(x = -mul * halfSize, y = -mul * halfSize, z = -halfSize)
    p2 = m.points[p2idx]
    
    p3idx = m.add_point(x = mul * halfSize, y = mul * halfSize, z = -halfSize)
    p3 = m.points[p3idx]
    
    nIdx = m.add_norm(x = 0, y = 0, z = -1)
    n = m.norms[nIdx]
    
    m.add_tri(p1 = p1idx, p2 = p2idx, p3 = p3idx, norm = nIdx)

  while numDivisions > 0:
    m.subdivide_triangles()
    numDivisions -= 1

  return m

########
# Generates a torus with provided size.
#   Params:
#     outRadius    : Outer radius
#     inRadius     : Inner radius
#     numStripes   : Number of segments per cross-section
#     numDivisions : Number of divisions around center (number cross-sections)
def generate_torus(outRadius = 1, inRadius = 0.5, numStripes = 6, numDivisions = 6):
  m = Model()

  # TODO: generate torus
  faceStep = 2 * pi / numDivisions # clockwise rot from posx (model view)
  stripeStep = 2 * pi / numStripes # clockwise rot from posx (division view) 
  stripeInc = stripeStep * 2 / numDivisions # each stripe is shifted by 2/numDivisions rotations 
  torusRad = (outRadius - inRadius) / 2 # actual radius used for calculations
  torusMid = (outRadius + inRadius) / 2 # center point of each cross-section

  for i in range(numStripes):
    for j in range(numDivisions):
      pass

  # NOTE: Currently, this is an empty model. Torus generation not supported yet.
  return m


########
# Main code architecture if run standalone.
# Times generation of several models and saves models to file.
if __name__ == "__main__":

  # generate various models
  print("Generating models... ", end = "")
  start = clock()

  sphereLowModel = generate_sphere(radius = 1, numLaterals = 6, numVerticals = 9)
  sphereLowModel.name = "sphereLow"
  cubeLowModel = generate_cube(size = 1, trisPerSide = 2)
  cubeLowModel.name = "cubeLow"
  torusLowModel = generate_torus(outRadius = 1, inRadius = 0.5, numStripes = 6, numDivisions = 6)
  torusLowModel.name = "torusLow"

  sphereMedModel = generate_sphere(radius = 1, numLaterals = 8, numVerticals = 12)
  sphereMedModel.name = "sphereMed"
  cubeMedModel = generate_cube(size = 1, trisPerSide = 8)
  cubeMedModel.name = "cubeMed"
  torusMedModel = generate_torus(outRadius = 1, inRadius = 0.5, numStripes = 8, numDivisions = 9)
  torusMedModel.name = "torusMed"

  sphereHighModel = generate_sphere(radius = 1, numLaterals = 16, numVerticals = 24)
  sphereHighModel.name = "sphereHigh"
  cubeHighModel = generate_cube(size = 1, trisPerSide = 32)
  cubeHighModel.name = "cubeHigh"
  torusHighModel = generate_torus(outRadius = 1, inRadius = 0.5, numStripes = 10, numDivisions = 12)
  torusHighModel.name = "torusHigh"

  elapsed = clock() - start
  print("Completed in {:.3f}s.".format(elapsed))

  # validate file okay
  try:
    f = open(OUTPUT_FILE, 'w')
  except Exception:
    print("ERROR: Could not open output file.")
    f = None

  if f != None:
    # write objects to file
    print("Writing models to file... ", end = "")
    start = clock()

    f.write(str(sphereLowModel))
    f.write(str(cubeLowModel))
    f.write(str(torusLowModel))

    f.write(str(sphereMedModel))
    f.write(str(cubeMedModel))
    f.write(str(torusMedModel))

    f.write(str(sphereHighModel))
    f.write(str(cubeHighModel))
    f.write(str(torusHighModel))

    f.close()
    elapsed = clock() - start
    print("Completed in {:.3f}s.".format(elapsed))

  input("Press ENTER to close this window.")