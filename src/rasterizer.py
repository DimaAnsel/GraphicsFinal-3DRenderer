################################
# rasterizer.py
# Noah Ansel
# nba38
# 2016-11-17
# ------------------------------
# Contains triangle rendering code. Ported and modified from
# assignment 2 submission.
################################


# import validation
fail = False
try:
  from model_creator import Point
except Exception:
  print("ERROR: Could not import 'model_creator' module. Is it in this folder?")
  fail = True
try:
  from numpy import *
except Exception:
  print("ERROR: Could not import 'numpy' module.")
  fail = True
try:
  from PIL import Image
except Exception:
  print("ERROR: Could not import 'PIL' library. Is pillow installed?")
  fail = True
try:
  from time import clock
except Exception:
  print("ERROR: Could not import 'time' module.")
  fail = True
if fail:
  input("Press ENTER to close this window.")
  exit()

########
# Renders a triangle in the provided zBuffer. Ported and modified from
# assignment 2 submission. Rasterized pixels only overwrite points with
# lower z-values in zBuffer.
#   Params:
#     p1, p2, p3 : Corners of triangle
#     c1, c2, c3 : Colors of p1, p2, and p3, respectively.
#                  Should be 3-tuple of RGB values between 0 and 1.
#     zBuffer    : zBuffer to use when rasterizing triangle.
def render_triangle(p1, p2, p3, c1, c2, c3, zBuffer):

  # obtain min and max coordinates
  xArr = (int(p1.x), int(p2.x), int(p3.x))
  yArr = (int(p1.y), int(p2.y), int(p3.y))
  minX = min(xArr)
  minY = min(yArr)
  if minX < 0:
    minX = 0
  if minY < 0:
    minY = 0
  maxX = max(xArr)
  maxY = max(yArr)
  if maxX > len(zBuffer) - 1:
    maxX = len(zBuffer) - 1
  if maxY > len(zBuffer[0]) - 1:
    maxY = len(zBuffer[0]) - 1 

  # calculate x-mul, y-mul, and offset for z value
  temp = mat([[p1.x, p1.y, 1],
              [p2.x, p2.y, 1],
              [p3.x, p3.y, 1]])
  zMat = mat([[p1.z],
              [p2.z],
              [p3.z]])

  resMat = linalg.inv(temp) * zMat
  xZinc = resMat.item((0,0))
  yZinc = resMat.item((1,0))
  zInit = resMat.item((2,0)) + xZinc * minX + yZinc * minY # init to lower

  # calculate coefficients & constants
  f12xStep = p1.y - p2.y
  f23xStep = p2.y - p3.y
  f31xStep = p3.y - p1.y
  f12yStep = p2.x - p1.x
  f23yStep = p3.x - p2.x
  f31yStep = p1.x - p3.x

  f12Const = p1.x * p2.y - p2.x * p1.y
  f23Const = p2.x * p3.y - p3.x * p2.y
  f31Const = p3.x * p1.y - p1.x * p3.y
  f23_1 = f23xStep * p1.x + f23yStep * p1.y + f23Const
  f31_2 = f31xStep * p2.x + f31yStep * p2.y + f31Const
  f12_3 = f12xStep * p3.x + f12yStep * p3.y + f12Const

  # pre-calculate alpha, beta, gamma constants
  alphaYstep = f23yStep / f23_1
  alphaXstep = f23xStep / f23_1
  alphaInit = alphaXstep * minX + alphaYstep * minY + f23Const / f23_1
  betaYstep = f31yStep / f31_2
  betaXstep = f31xStep / f31_2
  betaInit = betaXstep * minX + betaYstep * minY + f31Const / f31_2
  gammaYstep = f12yStep / f12_3
  gammaXstep = f12xStep / f12_3
  gammaInit = gammaXstep * minX + gammaYstep * minY + f12Const / f12_3
  
  # must provide minimum value because of float imprecision
  minVal = -0.00000001

  # iterate through bounding box to find if inside
  # algorithm from text using barycentric coordinates
  for y in range(minY, maxY + 1):
    alpha = alphaInit
    beta  = betaInit
    gamma = gammaInit
    zVal = zInit
    for x in range(minX, maxX + 1):
      
      if alpha >= minVal and beta >= minVal and gamma >= minVal:
        color = [int(c1[i] * alpha + c2[i] * beta + c3[i] * gamma) for i in range(3)]

        if zBuffer[x][y] == None or zBuffer[x][y][0] < zVal:
          zBuffer[x][y] = [zVal] + color # TODO: put z calculation here
      alpha += alphaXstep
      beta += betaXstep
      gamma += gammaXstep
      zVal += xZinc
    # increase starting for next iteration
    alphaInit += alphaYstep
    betaInit += betaYstep
    gammaInit += gammaYstep

    zInit += yZinc


########
# Main code architecture if run standalone.
# Draws two intersecting triangles and saves image.
if __name__ == "__main__":
  p1 = Point(x = 80, y = 20, z = -200)
  p2 = Point(x = 200, y = 300, z = -100)
  p3 = Point(x = 30, y = 450, z = -20)
  v1 = Point(x = 10, y = 200, z = -300)
  v2 = Point(x = 160, y = 100, z = -50)
  v3 = Point(x = 140, y = 450, z = -100)

  c1 = (50, 220, 220)
  c2 = (0, 255, 100)
  c3 = (0, 100, 255)
  c4 = (200, 255, 0)
  c5 = (220, 220, 50)
  c6 = (255, 200, 0)
  w = (255, 255, 255)
  zBuffer = []
  for x in range(500):
    zBuffer.append([None]*300)
  start = clock()
  render_triangle(p1 = p1,
                  p2 = p2,
                  p3 = p3,
                  c1 = c1,
                  c2 = c2,
                  c3 = c3,
                  zBuffer = zBuffer)
  render_triangle(p1 = v1,
                  p2 = v2,
                  p3 = v3,
                  c1 = c4,
                  c2 = c5,
                  c3 = c6,
                  zBuffer = zBuffer)
  elapsed = clock() - start
  print("Render took {:.3f}s.".format(elapsed))
  start = clock()
  img = Image.new(mode = 'RGB', size = (500,500))
  for x in range(500):
    for y in range(500):
      if zBuffer[x][y] != None:
        img.putpixel(xy=(x,y),value=tuple(zBuffer[x][y][1:]))
  elapsed = clock() - start
  print("Pixels tool {:.3f}s.".format(elapsed))
  img.save('test.png')

  input("Press ENTER to close this window.")