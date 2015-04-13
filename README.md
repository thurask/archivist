archivist
=========
A Python 3 script to download bars and turn them into autoloaders. 

## Requirements
### Operation
Requires [7za.exe](http://www.7-zip.org/download.html) (32-bit and 64-bit) and [cap.exe](https://drive.bitcasa.com/send/Lrb0VC6NsOEX5BNSDmGVn2mkeiSDklghCXlYuQk_YkRE).

32-bit 7za.exe should be included as 7za.exe and 64-bit 7za.exe should be included as 7za64.exe, since the script reads the OS bit setup and uses the 64/32 bit 7-Zip executable accordingly. Because 32-bit Windows is just as annoyingly persistent as Windows XP.

If you're using just the .py file, make sure to have Python =>3.4.2 in your PATH and the support executables in the local folder/your PATH.
Or, if you're using the release .exe, extract everything into the bar file folder (all .exes, .pyds and .dlls). Since it's a self-extracting zip.

Since it does the entire autoloader process from start to finish, make sure to have A LOT of hard drive space. 40GB at least.

### Redistribution
Those listed in Operation, plus (preferably) conversion to executable formats via [cx_freeze](http://cx-freeze.readthedocs.org/en/latest/index.html).

## What It Does
1. Ask for OS/radio/software versions (if not specified with command line arguments)
2. Ask for compression of loaders/deletion of uncompressed loaders/verification of loaders (if not specified)
3. Download all bars
4. Extract all bars
5. Make OS + radio (and radio loaders if specified) for each recognized signed file
6. Compress them (optional)
7. Sort bars and loaders into subfolders
8. Delete uncompressed loaders (optional)
9. Verify loaders (optional)

## Command Line Arguments
### Help

    > archivist.exe -h

    usage: archivist.exe OSVERSION RADIOVERSION SWVERSION [options]

    Download bar files, create autoloaders.

    positional arguments:

        os                  OS version, 10.x.y.zzzz
      
        radio               Radio version, 10.x.y.zzzz
      
        swrelease           Software version, 10.x.y.zzzz
  
    optional arguments:

        -h, --help          show this help message and exit
      
        --no-radio-loaders  Don't make radio loaders
      
        --no-compress       Don't compress loaders
      
        --no-delete-uncomp  Don't delete uncompressed loaders
        
        --no-verify         Don't verify created loaders
        
        --crc32             Enable CRC32 verification
        
        --adler32           Enable Adler32 verification
        
        --sha224            Enable SHA-224 verification
        
        --sha384            Enable SHA-384 verification
        
        --sha512            Enable SHA-512 verification
        
        --no-sha1           Disable SHA-1 verification
        
        --no-sha256         Disable SHA-256 verification
        
        --no-md5            Disable MD5 verification
    
### Example
  
    > archivist.exe 10.3.1.2726 10.3.1.2727 10.3.1.1877 --no-radio-loaders --sha512 --no-md5
  
  would make OS-only autoloaders for 10.3.1.2726/10.3.1.2727, compress them, delete uncompressed loaders and verify with SHA-1, SHA-256, SHA-512.

## License
No fancy licensing here, just fork this and do whatever.
Although, if you figure out something interesting, please do try to put it upstream via pull request.

## Authors
* Thurask [(@thuraski)](http://www.twitter.com/thuraski)
* Viewers Like You
