import subprocess
import sys
import os

os.system('echo starting installing requirements')

os.system("pip install -r ../../02_SOFTWARE/requirements.txt")

os.system('echo finished installing requirements')

os.system('echo starting installation')

os.system("pyinstaller ../../02_SOFTWARE/main.spec")

os.system('echo finished installation')
