#-------------------------
#Alec Barton
#Kplayers.py
#-------------------------

import os

#-------------------------
#CHANGE DIR
#changes the current working directory to a different working directory
#PARAEMETERS:
#destination (string) - name of directory to switch to
#RETURNS: nothing
#-------------------------
def change_dir(destination = None):
    #if the current directory is a sub-folder, returns to the main folder
    if str(os.path.basename(os.getcwd())) == "assets" or str(os.path.basename(os.getcwd())) == "saves":
        os.chdir(os.path.normpath(os.getcwd() + os.sep + os.pardir))
    #changes the current working directory to the destination
    if destination:
        os.chdir(os.getcwd()+ os.sep + str(destination))
