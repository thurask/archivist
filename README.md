archivist
=========
A Python 3 script to download bars and turn them into autoloaders. 

With command line arguments, it proceeds as directed. Without command line arguments, it queries the user as to OS version, radio version, software version, etc.
Most arguments are assumed with the questionnaire, so if you want fine control, use arguments.

## Requirements
### Universal
To make autoloaders, it requires [cap.exe](https://drive.bitcasa.com/send/Lrb0VC6NsOEX5BNSDmGVn2mkeiSDklghCXlYuQk_YkRE).
It doesn't actually run cap.exe, so just download the file and save it in the same folder as the script, or somewhere else using the -c command line option.

Since it does the entire autoloader process for all devices from start to finish, make sure to have A LOT of hard drive space. 40GB at least, even more if you aren't using 7-Zip compression.

If you're using this as a .py file, it requires Python =>3.4.2.

7-Zip compression (default) uses [p7zip](http://sourceforge.net/projects/p7zip/) (Linux/Mac)/[7-Zip](http://www.7-zip.org/download.html) (Windows). Zip and tar.xxx compression don't require external programs.

### Windows

By default, the script uses any installed instances of 7-Zip first.
If you're using them locally, 32-bit 7za.exe should be included as 7za.exe and 64-bit 7za.exe should be included as 7za64.exe.

If you're using the release .exe, extract everything into a folder (all .exes, .pyds and .dlls).

### Linux
If you're using 7z compression, this requires p7zip (look through your package manager, or install from source) in your path. I.e.:

	$which 7za
	
resolves to something.

Other than that, download archivist.py and make it executable with chmod.

### Mac

Same as Linux, but you'll have to either install p7zip from source, or install it with something like [Homebrew](http://brew.sh) or [MacPorts](https://www.macports.org).

## What It Does
1. Ask for OS/radio/software versions (if not specified)
2. Ask for compression of loaders/deletion of uncompressed loaders/verification of loaders (if not specified)
3. Download all bars
4. Extract all bars
5. Make OS + radio (and radio-only loaders if specified) for each recognized signed file
6. Compress them (optional)
7. Sort bars and loaders into subfolders
8. Delete uncompressed loaders (optional)
9. Verify loaders (optional)

## Command Line Arguments
### Help

    > archivist.exe -h

    usage: archivist [-h] [-v] [-f DIR] [-c PATH] [-no] [-nx] [-nl] [-nr] [-ns]
                 [-nc] [-nd] [-nv] [--crc32] [--adler32] [--md4] [--sha224]
                 [--sha384] [--sha512] [--ripemd160] [--no-sha1] [--no-sha256]
                 [--no-md5] [--7z | --tgz | --tbz | --txz | --zip]
                 os radio swrelease

	Download bar files, create autoloaders.
	
	positional arguments:
	  os                    OS version, 10.x.y.zzzz
	  radio                 Radio version, 10.x.y.zzzz
	  swrelease             Software version, 10.x.y.zzzz
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  -f DIR, --folder DIR  Working folder
	  -c PATH, --cap PATH   Path to cap.exe
	
	negators:
	  Disable program functionality
	
	  -no, --no-download    Don't download files
	  -nx, --no-extract     Don't extract bar files
	  -nl, --no-loaders     Don't create autoloaders
	  -nr, --no-radios      Don't make radio autoloaders
	  -ns, --no-rmsigned    Don't remove signed files
	  -nc, --no-compress    Don't compress loaders
	  -nd, --no-delete      Don't delete uncompressed loaders
	  -nv, --no-verify      Don't verify created loaders
	
	verifiers:
	  Verification methods
	
	  --crc32               Enable CRC32 verification
	  --adler32             Enable Adler-32 verification
	  --md4                 Enable MD4 verification
	  --sha224              Enable SHA-224 verification
	  --sha384              Enable SHA-384 verification
	  --sha512              Enable SHA-512 verification
	  --ripemd160           Enable RIPEMD-160 verification
	  --no-sha1             Disable SHA-1 verification
	  --no-sha256           Disable SHA-256 verification
	  --no-md5              Disable MD5 verification
	
	compressors:
	  Compression methods
	
	  --7z                  Compress with 7z, LZMA2
	  --tgz                 Compress with tar, GZIP
	  --tbz                 Compress with tar, BZIP2
	  --txz                 Compress with tar, LZMA
	  --zip                 Compress with zip, DEFLATE
	
	http://github.com/thurask/archivist

    
### Example
  
    > archivist.exe 10.3.1.2726 10.3.1.2727 10.3.1.1877 -nr --sha512 --no-md5
  
  would make OS-only autoloaders for 10.3.1.2726/10.3.1.2727, compress them, delete uncompressed loaders and verify with SHA-1, SHA-256, SHA-512.

## License
No fancy licensing here, just fork this and do whatever.
Although, if you figure out something interesting, please do try to put it upstream via pull request.

## Authors
* Thurask [(@thuraski)](http://www.twitter.com/thuraski)
* Viewers Like You
