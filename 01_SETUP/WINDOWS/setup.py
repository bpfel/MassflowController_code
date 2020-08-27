import subprocess
import sys
import os

os.system("echo starting installing requirements")

os.system("pip install -r ../../02_SOFTWARE/requirements.txt")

os.system("echo finished installing requirements")

os.system("echo starting installation")

os.chdir("../../02_SOFTWARE")

os.system("pyinstaller main.spec")

os.system("echo finished installation")
