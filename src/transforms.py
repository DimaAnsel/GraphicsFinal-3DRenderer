################################
# transforms.py
# Noah Ansel
# nba38
# 2016-11-17
# ------------------------------
# Functions to generate transformation matrices.
################################

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
if fail:
  input("Press ENTER to close this window.")
  exit()

# focal constant used in perspective projection
FOCAL_CONST = 1.0 / tan(pi / 8) # 45deg view angle (22.5 per side)


########
# Generates the perspective projection matrix.
# Projection assumes looking towards negative Z. Implementation from textbook.
#   Returns: Perspective rotation matrix.
def perspective_project():
  far = 1000
  near = 5
  toRet = mat([[near,    0,          0,           0],
               [0,    near,          0,           0],
               [0,       0, near + far, -far * near],
               [0,       0,          1,           0]])
  return toRet * translate(z = -near) # move camera back before projecting

########
# Given rotation in radians about X axis (viewing towards negative X),
# returns the rotation matrix. Translation matrix from
# https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions.
#   Params:
#     rad : Extent of rotation in radians.
#   Returns: Rotation matrix
def rotateX(rad):
  return mat([[1,        0,         0, 0],
              [0, cos(rad), -sin(rad), 0],
              [0, sin(rad),  cos(rad), 0],
              [0,        0,         0, 1]])

########
# Given rotation in radians about Y axis (viewing towards negative Y),
# returns the rotation matrix. Translation matrix from
# https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions.
#   Params:
#     rad : Extent of rotation in radians.
#   Returns: Rotation matrix
def rotateY(rad):
  # return rotateZ(pi/4) * rotateX(rad) * rotateZ(-pi/4)
  return mat([[ cos(rad), 0, sin(rad), 0],
              [        0, 1,        0, 0],
              [-sin(rad), 0, cos(rad), 0],
              [        0, 0,        0, 1]])

########
# Given rotation in radians about Z axis (viewing towards negative Z),
# returns the rotation matrix. Translation matrix from
# https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions.
#   Params:
#     rad : Extent of rotation in radians.
#   Returns: Rotation matrix
def rotateZ(rad):
  return mat([[cos(rad), -sin(rad), 0, 0],
              [sin(rad), cos(rad), 0, 0],
              [       0,        0, 1, 0],
              [       0,        0, 0, 1]])

########
# Given x, y, and z offsets, returns the translation matrix.
#   Params:
#     x, y, z : Translation offsets.
#   Returns: Translation matrix.
def translate(x = 0, y = 0, z = 0):
  arr = [[1, 0, 0, x],
         [0, 1, 0, y],
         [0, 0, 1, z],
         [0, 0, 0, 1]]
  return mat(arr)

########
# Given x, y, and z scalars, returns scaling matrix.
#   Params:
#     x, y, z : Scaling factors.
#   Returns: Scaling matrix.
def scale(x = 1, y = 1, z = 1):
  return mat([[x, 0, 0, 0],
              [0, y, 0, 0],
              [0, 0, z, 0],
              [0, 0, 0, 1]])

########
# Given x, y, and z scalars for regular points, returns scaling matrix for normals.
#   Params:
#     x, y, z : Scalars used for scale() when transforming points of model.
#   Returns: Scaling matrix to use for normals.
def scale_norm(x = 1, y = 1, z = 1):
  return mat([[1/x,   0,   0, 0],
              [  0, 1/y,   0, 0],
              [  0,   0, 1/z, 0],
              [  0,   0,   0, 1]])