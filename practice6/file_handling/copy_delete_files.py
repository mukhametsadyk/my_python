import shutil
import os

shutil.copy("test.txt", "copy.txt")
os.remove("copy.txt")