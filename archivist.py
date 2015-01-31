##############################
# ARCHIVIST.PY               #
#                            #
# Requirements:              #
# 7za.exe                    #
# 7za64.exe                  #
# cap.exe                    #
#                            #
# Instructions:              #
# Read the CMD prompt :p     #
#                            #
# - Thurask                  #
##############################

import os
import glob
import shutil
import platform

localdir = os.getcwd()
print("!!!!EXTRACT THIS TO BAR FILE FOLDER!!!!\n")
osversion = input("OS VERSION: ")
radioversion = input("RADIO VERSION: ")
extracted = input("EXTRACT BAR FILES? Y/N: ")
received = input("COMPRESS LOADERS? Y/N: ")

#Get OS type, set 7z type
if platform.machine().endswith("64") == True: 
    sevenzip = "7za64.exe"
else:
    sevenzip = "7za.exe"

#Extract bars with 7z
def extract():
    print("EXTRACTING...")
    for file in os.listdir(localdir):
        if file.endswith(".bar"):
            print("\nEXTRACTING: " + file + "\n")
            os.system(sevenzip + " x " + '"' + file + '" *.signed -aos')

#Compress loaders with 7z
##WARNING: Requires a lot of RAM.
def compress():
    for file in os.listdir(localdir):
        if file.endswith(".exe") and file.startswith(("Q10", "Z10", "Z30", "Z3", "Passport")):
            os.system(sevenzip + " a -mx9 -mmt8 -m0=lzma2:d128m:fb128 " + '"' + os.path.splitext(os.path.basename(file))[0]   + '.7z" "' + file + '"')

#Extract bars (if chosen)
if extracted == "yes" or extracted == "y" or extracted == "Y":
    extract()
else:
    pass

#Make dirs
if not os.path.exists(os.path.join(localdir, 'bars')):
    os.mkdir(os.path.join(localdir, 'bars'))
bardir = os.path.join(localdir, 'bars')

if not os.path.exists(os.path.join(localdir, 'loaders')):
    os.mkdir(os.path.join(localdir, 'loaders'))
loaderdir = os.path.join(localdir, 'loaders')

if received == "yes" or received == "y" or received == "Y":
    if not os.path.exists(os.path.join(localdir, 'zipped')):
        os.mkdir(os.path.join(localdir, 'zipped'))
    zipdir = os.path.join(localdir, 'zipped')

##OS Images
#8960
try:
    os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
except IndexError:
    print("\nNo 8960 image found\n")

#8974
try:
    os_8974 = str(glob.glob("*qc8974*desktop*.signed")[0])
except IndexError:
    print("No 8974 image found\n")

#OMAP
try:
    os_ti = str(glob.glob("qcfm.image.com.qnx.coreos.qcfm.os.factory_sfi.desktop.*.signed")[0])
except IndexError:
    print("No OMAP image found, trying 10.3.1 name\n")

#Winchester (10.3.1+)
try:
    os_ti = str(glob.glob("*winchester*.signed")[0])
except IndexError:
    print("No OMAP image found\n")

##Radios + Autoloaders
#STL100-1
try:
    radio_z10_ti = str(glob.glob("*radio.m5730*.signed")[0])
except IndexError:
    print("No OMAP radio found\n")
else:
    print("Creating OMAP Z10 OS...\n")
    try:
        os.system("cap.exe create " + os_ti + " " + radio_z10_ti + " Z10_" + osversion + "_STL100-1.exe")
    except Exception:
        print("Could not create STL100-1 OS/radio loader\n")
    print("Creating OMAP Z10 radio...\n")
    try:
        os.system("cap.exe create " + radio_z10_ti + " Z10_" + radioversion + "_STL100-1.exe")
    except Exception:
        print("Could not create STL100-1 radio loader\n")
    
#STL100-X
try:
    radio_z10_qcm = str(glob.glob("*radio.qc8960.BB*.signed")[0])
except IndexError:
    print("No 8960 radio found\n")
else:
    print("Creating Qualcomm Z10 OS...\n")
    try:
        os.system("cap.exe create " + os_8960 + " " + radio_z10_qcm + " Z10_" + osversion + "_STL100-2-3.exe")
    except Exception:
        print("Could not create Qualcomm Z10 OS/radio loader\n")    
    print("Creating Qualcomm Z10 radio...\n")
    try:
        os.system("cap.exe create " + radio_z10_qcm + " Z10_" + radioversion + "_STL100-2-3.exe")
    except Exception:
        print("Could not create Qualcomm Z10 radio loader\n")
    
#STL100-4
try:
    radio_z10_vzw = str(glob.glob("*radio.qc8960*omadm*.signed")[0])
except IndexError:
    print("No Verizon 8960 radio found\n")
else:
    print("Creating Verizon Z10 OS...\n")
    try:
        os.system("cap.exe create " + os_8960 + " " + radio_z10_vzw + " Z10_" + osversion + "_STL100-4.exe")
    except Exception:
        print("Could not create Verizon Z10 OS/radio loader\n")    
    print("Creating Verizon Z10 radio...\n")
    try:
        os.system("cap.exe create " + radio_z10_vzw + " Z10_" + radioversion + "_STL100-4.exe")
    except Exception:
        print("Could not create Verizon Z10 radio loader\n")
    
#Q10/Q5
try:
    radio_q10 = str(glob.glob("*8960*wtr.*.signed")[0])
except IndexError:
    print("No Q10/Q5 radio found\n")
else:
    print("Creating Q10/Q5 OS...\n")
    try:
        os.system("cap.exe create " + os_8960 + " " + radio_q10 + " Q10_" + osversion + "_SQN100-1-2-3-4-5.exe")
    except Exception:
        print("Could not create Q10/Q5 OS/radio loader\n")
    print("Creating Q10/Q5 radio...\n")
    try:
        os.system("cap.exe create " + radio_q10 + " Q10_" + radioversion + "_SQN100-1-2-3-4-5.exe")
    except Exception:
        print("Could not create Q10/Q5 radio loader\n")

#Z30/Classic
try:
    radio_z30 = str(glob.glob("*8960*wtr5*.signed")[0])
except IndexError:
    print("No Z30/Classic radio found\n")
else:
    print("Creating Z30/Classic OS...\n")
    try:
        os.system("cap.exe create " + os_8960 + " " + radio_z30 + " Z30_" + osversion + "_STA100-1-2-3-4-5-6.exe")
    except Exception:
        print("Could not create Z30/Classic OS/radio loader\n")
    print("Creating Z30/Classic radio...\n")
    try:
        os.system("cap.exe create " + radio_z30 + " Z30_" + radioversion + "_STA100-1-2-3-4-5-6.exe")
    except Exception:
        print("Could not create Z30/Classic radio loader\n")
    
#Z3
try:
    radio_z3 = str(glob.glob("*8930*wtr5*.signed")[0])
except IndexError:
    print("No Z3 radio found\n")
else:
    print("Creating Z3 OS...\n")
    try:
        os.system("cap.exe create " + os_8960 + " " + radio_z3 + " Z3_" + osversion + "_STJ100-1-2.exe")
    except Exception:
        print("Could not create Z3 OS/radio loader\n")
    print("Creating Z3 radio...\n")
    try:
        os.system("cap.exe create " + radio_z3 + " Z3_" + radioversion + "_STJ100-1-2.exe")
    except Exception:
        print("Could not create Z3 radio loader\n")
    
#Passport
try:
    radio_8974 = str(glob.glob("*8974*wtr2*.signed")[0])
except NameError:
    print("No 8974 OS found\n")
except IndexError:
    print("No Passport radio found\n")
else:
    print("Creating Passport OS...\n")
    try:
        os.system("cap.exe create " + os_8974 + " " + radio_8974 + " Passport_" + osversion + "_SQW100-1-2-3.exe")
    except Exception:
        print("Could not create Passport OS/radio loader\n")
    print("Creating Passport radio...\n")
    try:
        os.system("cap.exe create " + radio_8974 + " Passport_" + radioversion + "_SQW100-1-2-3.exe")
    except Exception:
        print("Could not create Passport radio loader\n")
    
#Remove .signed files only if extracted from bars
if extracted == "yes" or extracted == "y" or extracted == "Y":
    print("REMOVING .signed FILES...\n")
    for file in os.listdir(localdir):
        if file.endswith(".signed"):
            print("REMOVING: " + file)
            os.remove(file)
else:
    pass

#If compression = true, compress
if received == "yes" or received == "y" or received == "Y":
    print("\nCOMPRESSING...\n")
    compress()
else:
    pass

print("\nMOVING...\n")

for files in os.listdir(localdir):
    if files.endswith(".bar"):
        print("MOVING: " + files)
        shutil.move(files, bardir)
    if files.endswith(".exe") and files.startswith(("Q10", "Z10", "Z30", "Z3", "Passport")):
        print("MOVING: " + files)
        shutil.move(files, loaderdir)
    if received == "yes" or received == "y" or received == "Y":
        if files.endswith(".7z"):
            print("MOVING: " + files)
            shutil.move(files, zipdir)
            
print("\nFINISHED!\n")
smeg = input("Press Enter to exit")