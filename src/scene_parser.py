################################
# scene_parser.py
# Noah Ansel
# nba38
# 2016-11-17
# ------------------------------
# Parses a scene file and generates models for the desired resolution.
################################

fail = False
try:
  from model_creator import *
except Exception:
  print("ERROR: Could not import 'model_creator' module. Is it in this folder?")
  fail = True
try:
  from math import *
except Exception:
  print("ERROR: Could not import 'math' module.")
  fail = True
if fail:
  input("Press ENTER to close this window.")
  exit()

# resolution options
RES_LOW = "RES_LOW"
RES_MEDIUM = "RES_MEDIUM"
RES_HIGH = "RES_HIGH"
RES_ULTRA = "RES_ULTRA"
RES_INSANE = "RES_INSANE"
RES_REALISTIC = "RES_REALISTIC"

# model generation parameters for given resolution options
SHAPE_RESOLUTIONS = {"cube":  {RES_LOW:       2,
                               RES_MEDIUM:    8,
                               RES_HIGH:      32,
                               RES_ULTRA:     128,
                               RES_INSANE:    512,
                               RES_REALISTIC: 2048},
                     "sphere":{RES_LOW:       (4, 6),
                               RES_MEDIUM:    (8, 12),
                               RES_HIGH:      (16, 24),
                               RES_ULTRA:     (32, 48),
                               RES_INSANE:    (64, 96),
                               RES_REALISTIC: (128, 192)}}

# directory where scenes are located
SCENE_DIRECTORY = "../scenes/"

########
# Parses a scene file and generates models for the desired resolution.
# If file does not exist, returns an empty scene.
#   Params:
#     filename   : File to be parsed.
#     resolution : The desired resolution of the models.
#     debug      : If True, prints summary on exit.
#   Returns: List of Model objects and list of Light objects.
def parse_scene(filename, resolution = RES_MEDIUM, debug = False):
  models = []
  lights = []

  try:
    f = open(SCENE_DIRECTORY + filename)
    lines = f.readlines()
    f.close()
  except FileNotFoundError:
    print("ERROR: File '{}' not found.".format(filename))
    lines = []
  except:
    print("ERROR: Unknown error occured while opening '{}'.".format(filename))
    lines = []

  if resolution not in (RES_LOW, RES_MEDIUM, RES_HIGH, RES_ULTRA, RES_INSANE, RES_REALISTIC):
    raise ValueError("Unexpected resolution.")

  for line in lines:
    if len(line) == 0 or line[0] == '#': # commented out
      continue
    words = line.split()
    if len(words) == 0: # blank line
      continue
    if words[0] not in ("cube", "sphere", "light"):
      print(line, end = '')
      print("ERROR: '{}' not a supported shape.".format(words[0]))
      continue

    if words[0] in ("cube", "sphere"):
      if len(words) != 6:
        print(line, end = '')
        print("ERROR: Expected 6 args, had {}.".format(len(words)))
        continue
      try:
        size = float(words[1])
        color = words[2].split(',')
        for i in range(len(color)):
          color[i] = float(color[i])
        scale = words[3].split(',')
        for i in range(len(scale)):
          scale[i] = float(scale[i])
        offset = words[4].split(',')
        for i in range(len(offset)):
          offset[i] = float(offset[i])
        rotation = words[5].split(',')
        for i in range(len(rotation)):
          rotation[i] = eval(rotation[i])
      except:
        print(line, end = '')
        print("ERROR: Could not parse arguments for '{}'.".format(line))
        continue

      if words[0] == "cube":
        new = generate_cube(size = size,
                            trisPerSide = SHAPE_RESOLUTIONS[words[0]][resolution],
                            color = color)
      elif words[0] == "sphere":
        new = generate_sphere(radius = size,
                              numLaterals = SHAPE_RESOLUTIONS[words[0]][resolution][0],
                              numVerticals = SHAPE_RESOLUTIONS[words[0]][resolution][1],
                              color = color)
      new.scale = Point(x = scale[0], y = scale[1], z = scale[2])
      new.offset = Point(x = offset[0], y = offset[1], z = offset[2])
      new.rotation = Point(phi = rotation[0], theta = rotation[1], radius = 1)
      models.append(new)
    elif words[0] == "light":
      if len(words) not in (2,3):
        print(line, end = '')
        print("ERROR: Expected 2 or 3 args, had {}.".format(len(words)))
        continue
      try:
        loc = words[1].split(',')
        for i in range(len(loc)):
          loc[i] = float(loc[i])
        if len(words) == 3:
          color = words[2].split(',')
          for i in range(len(color)):
            color[i] = float(color[i])
        else:
          color = None
      except:
        print(line, end = '')
        print("ERROR: Could not parse arguments for '{}'.".format(line))
        continue

      new = Light(x = loc[0], y = loc[1], z = loc[2], color = color)
      lights.append(new)

  numPts = 0
  numNorms = 0
  numTris = 0
  for m in models:
    numPts += len(m.points)
    numNorms += len(m.norms)
    numTris += len(m.tris)
  if debug:
    print('+-Parser Report--\n' +
          '|Points: {}\n|Norms: {}\n|Tris: {}\n'.format(numPts, numNorms, numTris) +
          '|Models: {}\n|Lights: {}\n'.format(len(models), len(lights)) +
          '+----------------')

  return models, lights


########
# Main code architecture if run standalone.
# Parses a scene and prints debug output.
if __name__ == "__main__":
  models, lights = parse_scene("scene1.txt", debug = True)

  input("Press ENTER to close this window.")