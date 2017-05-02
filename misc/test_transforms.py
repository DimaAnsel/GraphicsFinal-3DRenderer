try:
  from transforms import *
except Exception:
  print("ERROR: Could not import 'transforms' module. Is it in this folder?")
try:
  from model_creator import *
except Exception:
  print("ERROR: Could not import 'model_creator' module. Is it in this folder?")

########
# Tests if 2 points are nearly identical (since floats have small error).
#   Params:
#     p1, p2 : Points to be compared
#     places : Number of significant digits after decimal point
def almost_equal(p1, p2, places = 7):
  precision = 10 ** -places
  if (abs(p1.x - p2.x) <= precision and
      abs(p1.y - p2.y) <= precision and
      abs(p1.z - p2.z) <= precision):
    return True
  else:
    return False

def test_perspective_project():
  pass

def test_rotateX():
  mat = rotateX(pi / 4)
  p = Point(theta = -pi / 2, phi = pi / 4, radius = 5)

  expected = Point(x = 0, y = -5, z = 0)
  res = Point(matrix = mat * p.mat())
  if almost_equal(res, expected):
    print("test_rotateX: Passed")
  else:
    print(p)
    print(res)
    print("test_rotateX: Failed")

def test_rotateY():
  mat = rotateY(pi / 4)
  p = Point(theta = 0, phi = 3 * pi / 4, radius = 5)

  expected = Point(x = 0, y = 0, z = -5)
  res = Point(matrix = mat * p.mat())
  if almost_equal(res, expected):
    print("test_rotateY: Passed")
  else:
    print(p)
    print(res)
    print("test_rotateY: Failed")

def test_rotateZ():
  mat = rotateZ(pi / 4)
  p = Point(theta = -pi/4, phi = pi / 2, radius = 5)

  expected = Point(x = 5, y = 0, z = 0)
  res = Point(matrix = mat * p.mat())
  if almost_equal(res, expected):
    print("test_rotateZ: Passed")
  else:
    print(p)
    print(res)
    print("test_rotateZ: Failed")

def test_translate():
  mat = translate(x = 3, y = 4, z = 6)
  p = Point(x = -2, y = -2, z = -2)

  expected = Point(x = 1, y = 2, z = 4)
  res = Point(matrix = mat * p.mat())
  if almost_equal(res, expected):
    print("test_translate: Passed")
  else:
    print(p)
    print(res)
    print("test_translate: Failed")

def test_scale():
  mat = scale(x = 4, y = 0.1, z = 2.5)
  p = Point(x = 1, y = 100, z = 4)

  expected = Point(x = 4, y = 10, z = 10)
  res = Point(matrix = mat * p.mat())
  if almost_equal(res, expected):
    print("test_scale: Passed")
  else:
    print(p)
    print(res)
    print("test_scale: Failed")


if __name__ == "__main__":
  test_perspective_project()
  test_rotateX()
  test_rotateY()
  test_rotateZ()
  test_translate()
  test_scale()