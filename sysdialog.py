import sys
import os
import subprocess

p = subprocess.Popen("lsalrt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

print p.communicate()[0]

print "Done"