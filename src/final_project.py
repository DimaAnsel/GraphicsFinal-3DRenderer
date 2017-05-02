################################
# final_project.py
# Noah Ansel
# nba38
# 2016-11-17
# ------------------------------
# Controls viewpoint, scene, and rendering options of a Display object.
# Main code architecture for full application.
################################

fail = False
try:
  from tkinter import *
except Exception:
  print("ERROR: Could not import 'tkinter' module.")
  fail = True
try:
  from controls import Controls
except Exception:
  print("ERROR: Could not import 'controls' module. Is it in this folder?")
  fail = True
try:
  from display import Display
except Exception:
  print("ERROR: Could not import 'display' module. Is it in this folder?")
  fail = True
if fail:
  input("Press ENTER to close this window.")
  exit()

########
# Main code architecture. Sets up Tkinter objects and begins running program.
def main():
  root = Tk()
  root.title("Simple 3-D Renderer :: Noah Ansel (nba38)")

  display = Display(root)
  controls = Controls(root, display)
  controls.grid(row = 0, column = 0, sticky = N+W)
  display.grid(row = 0, column = 1, sticky = N+W+E+S)

  root.mainloop()

main()