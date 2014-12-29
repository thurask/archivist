##############################
# ARCHIVIST.PY               #
#                            #
# Requirements:              #
# 7za.exe                    #
# cap.exe                    #
#                            #
# Instructions:              #
# Read the CMD prompt :p     #
#                            #
# - Thurask                  #
#                            #
##############################

import os
import glob

localdir = os.getcwd()
print("!!!!EXTRACT EVERYTHING TO BAR FILE FOLDER!!!!\n")

osversion = input("OS VERSION: ")
radioversion = input("RADIO VERSION: ")
print("\n")
extracted = input("EXTRACT BAR FILES? Y/N: ")
received = input("COMPRESS LOADERS? Y/N: ") 
print("\n")

#Extract bars with 7za.exe
def extract():
    for file in os.listdir(localdir):
        if file.endswith(".bar"):
            os.system("7za.exe x " + '"' + file + '" *.signed -aos')

if extracted == "yes" or received == "y" or received == "Y":
    extract()
else:
    pass

##OS Images
#8960
try:
    os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
except IndexError:
    print("No 8960 image found")

#8974
try:
    os_8974 = str(glob.glob("*qc8974*desktop*.signed")[0])
except IndexError:
    print("No 8974 image found")

#OMAP
try:
    os_ti = str(glob.glob("qcfm.image.com.qnx.coreos.qcfm.os.factory_sfi.desktop.*.signed")[0])
except IndexError:
    print("No OMAP image found, trying 10.3.1 name")

#Winchester (10.3.1+)
try:
    os_ti = str(glob.glob("*winchester*.signed")[0])
except IndexError:
    print("No OMAP image found")

##Radios + Autoloaders
#STL100-1
try:
    radio_z10_ti = str(glob.glob("*radio.m5730*.signed")[0])
except IndexError:
    print("No OMAP radio found")
else:
    os.system("cap.exe create " + os_ti + " " + radio_z10_ti + " Z10_" + osversion + "_STL100-1.exe")
    os.system("cap.exe create " + radio_z10_ti + " Z10_" + radioversion + "_STL100-1.exe")
    
#STL100-X
try:
    radio_z10_qcm = str(glob.glob("*radio.qc8960.BB*.signed")[0])
except IndexError:
    print("No 8960 radio found")
else:
    os.system("cap.exe create " + os_8960 + " " + radio_z10_qcm + " Z10_" + osversion + "_STL100-2-3.exe")
    os.system("cap.exe create " + radio_z10_qcm + " Z10_" + radioversion + "_STL100-2-3.exe")
    
#STL100-4
try:
    radio_z10_vzw = str(glob.glob("*radio.qc8960*omadm*.signed")[0])
except IndexError:
    print("No Verizon 8960 radio found")
else:
    os.system("cap.exe create " + os_8960 + " " + radio_z10_vzw + " Z10_" + osversion + "_STL100-4.exe")
    os.system("cap.exe create " + radio_z10_vzw + " Z10_" + radioversion + "_STL100-4.exe")
    
#Q10/Q5
try:
    radio_q10 = str(glob.glob("*8960*wtr*.signed")[0])
except IndexError:
    print("No Q10/Q5 radio found")
else:
    os.system("cap.exe create " + os_8960 + " " + radio_q10 + " Q10_" + osversion + "_SQN100-1-2-3-4-5.exe")
    os.system("cap.exe create " + radio_q10 + " Q10_" + radioversion + "_SQN100-1-2-3-4-5.exe")
    
#Z30/Classic
try:
    radio_z30 = str(glob.glob("*8960*wtr5*.signed")[0])
except IndexError:
    print("No Z30/Classic radio found")
else:
    os.system("cap.exe create " + os_8960 + " " + radio_z30 + " Z30_" + osversion + "_STA100-1-2-3-4-5-6.exe")
    os.system("cap.exe create " + radio_z30 + " Z30_" + radioversion + "_STA100-1-2-3-4-5-6.exe")
    
#Z3
try:
    radio_z3 = str(glob.glob("*8930*wtr5*.signed")[0])
except IndexError:
    print("No Z3 radio found")
else:
    os.system("cap.exe create " + os_8960 + " " + radio_z3 + " Z3_" + osversion + "_STJ100-1-2.exe")
    os.system("cap.exe create " + radio_z3 + " Z3_" + radioversion + "_STJ100-1-2.exe")
    
#Passport
try:
    radio_8974 = str(glob.glob("*8974*wtr2*.signed")[0])
except NameError:
    print("No 8974 OS found")
except IndexError:
    print("No Passport radio found")
else:
    os.system("cap.exe create " + os_8974 + " " + radio_8974 + " Passport_" + osversion + "_SQW100-1-2-3.exe")
    os.system("cap.exe create " + radio_8974 + " Passport_" + radioversion + "_SQW100-1-2-3.exe")

for file in os.listdir(localdir):
    if file.endswith(".signed"):
        os.remove(file)

#Compress loaders with 7za.exe
def compress():
    for file in os.listdir(localdir):
        if file.endswith(".exe"):
            os.system("7za.exe a -mx9 -mmt8 -m0=lzma2:d128m:fb128 " + '"' + file + '.7z" "' + file + '"')

def purge7z():
    os.remove("7za.7z")
    os.remove("cap.7z")
    os.remove("archivist.7z")

if received == "yes" or received == "y" or received == "Y":
    compress()
    purge7z()
else:
    pass
