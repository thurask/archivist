archivist
=========
A Python 3 script to turn bars into autoloaders. 

## Requirements
### Operation
Requires [7za.exe](http://www.7-zip.org/download.html) (32-bit and 64-bit) and [cap.exe](https://drive.bitcasa.com/send/Lrb0VC6NsOEX5BNSDmGVn2mkeiSDklghCXlYuQk_YkRE) in the same folder as the script and all of the OS/radio bars you intend to turn into loaders. 32-bit 7za.exe should be included as 7za.exe and 64-bit 7za.exe should be included as 7za64.exe, since the script reads the OS bit setup and uses the 64/32 bit 7-Zip executable accordingly. Because 32-bit Windows is just as annoyingly persistent as Windows XP.

If you're using just the .py file, make sure to have Python =>3.4.2 in your PATH and the support executables in the local folder. Or, if you're using the release .exe, extract everything into the bar file folder (all .exes, .pyds and .dlls).

### Bar Files
You must have debrick and radio bars or the corresponding signed files to use this script. If you're using signed files, you **MUST** use the default name. This does **NOT** work with IFS files (i.e. from extracted 10.3.1 autoloaders).

### Redistribution
Those listed in Operation, plus (preferably) conversion to executable formats via [cx_freeze](http://cx-freeze.readthedocs.org/en/latest/index.html).

## What It Does
1. Ask for OS/radio versions
2. Ask for extraction of bar files
3. If you said yes, it extracts every bar. If not, it skips to the next step.
4. Load each signed file filename
5. Make OS + radio and radio loaders for each recognized signed file
6. Sort bars and loaders into subfolders (your output is in the /loaders directory)
7. Compress them (optional)
