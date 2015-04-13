##############################
# ARCHIVIST.PY				 #
# 							 #
# Requirements:				 #
# 7za.exe					 #
# 7za64.exe					 #
# cap.exe					 #
# Windows					 #
# 							 #
# Instructions:				 #
# Read the CMD prompt :p	 #
# 							 #
# - Thurask					 #
##############################

import os  # filesystem read
import glob  # string matching for files
import shutil  # directory read/write
import platform  # bit type
import hashlib  # SHA-x, MD5
import requests  # downloading
from requests.packages import urllib3  # disable SSL warnings
import sys  # arguments
import argparse  # argument parsing
import time  # time for downloader
import queue  # downloader multithreading
import threading  # downloader multithreading
import binascii  # downloader thread naming
import math  # rounding of floats
import webbrowser  # invoke browser if update is there
import subprocess # invocation of 7z, cap
import zlib #adler32, crc32

# Hash/verification functions; perform operation on specific file
# CRC32
def crc32hash(filepath, blocksize=16 * 1024 * 1024):
	seed = 0
	with open(filepath, 'rb') as f:
		for chunk in iter(lambda: f.read(1024), b''):
			seed = zlib.crc32(chunk, seed)
	final = format(seed & 0xFFFFFFFF, "x")
	return final

# Adler32
def adler32hash(filepath, blocksize=16 * 1024 * 1024):
	asum = 1
	with open(filepath, 'rb') as f:
		while True:
			data = f.read(blocksize)
			if not data:
				break
			asum = zlib.adler32(data, asum)
			if asum < 0:
				asum += 2**32
	final = format(asum & 0xFFFFFFFF, "x")
	return final

# SHA-1
def sha1hash(filepath, blocksize=16 * 1024 * 1024):
	sha1 = hashlib.sha1()
	f = open(filepath, 'rb')
	try:
		while True:
			data = f.read(blocksize)
			if not data:
				break
			sha1.update(data)  # read in 16MB chunks, not whole autoloader
	finally:
		f.close()
	return sha1.hexdigest()

# SHA-224
def sha224hash(filepath, blocksize=16 * 1024 * 1024):
	sha224 = hashlib.sha224()
	f = open(filepath, 'rb')
	try:
		while True:
			data = f.read(blocksize)
			if not data:
				break
			sha224.update(data)  # read in 16MB chunks, not whole autoloader
	finally:
		f.close()
	return sha224.hexdigest()

# SHA-256
def sha256hash(filepath, blocksize=16 * 1024 * 1024):
	sha256 = hashlib.sha256()
	f = open(filepath, 'rb')
	try:
		while True:
			data = f.read(blocksize)
			if not data:
				break
			sha256.update(data)  # read in 16MB chunks, not whole autoloader
	finally:
		f.close()
	return sha256.hexdigest()

# SHA-384
def sha384hash(filepath, blocksize=16 * 1024 * 1024):
	sha384 = hashlib.sha384()
	f = open(filepath, 'rb')
	try:
		while True:
			data = f.read(blocksize)
			if not data:
				break
			sha384.update(data)  # read in 16MB chunks, not whole autoloader
	finally:
		f.close()
	return sha384.hexdigest()

# SHA-512
def sha512hash(filepath, blocksize=16 * 1024 * 1024):
	sha512 = hashlib.sha512()
	f = open(filepath, 'rb')
	try:
		while True:
			data = f.read(blocksize)
			if not data:
				break
			sha512.update(data)  # read in 16MB chunks, not whole autoloader
	finally:
		f.close()
	return sha512.hexdigest()

# MD5
def md4hash(filepath, blocksize=16 * 1024 * 1024):
	md4 = hashlib.new('md4')
	f = open(filepath, 'rb')
	try:
		while True:
			data = f.read(blocksize)
			if not data:
				break
			md4.update(data)  # read in 16MB chunks, not whole autoloader
	finally:
		f.close()
	return md4.hexdigest()


# MD5
def md5hash(filepath, blocksize=16 * 1024 * 1024):
	md5 = hashlib.md5()
	f = open(filepath, 'rb')
	try:
		while True:
			data = f.read(blocksize)
			if not data:
				break
			md5.update(data)  # read in 16MB chunks, not whole autoloader
	finally:
		f.close()
	return md5.hexdigest()

# Use choice of hash functions for all files in a directory
def verifier(workingdir, blocksize=16 * 1024 * 1024, crc32=False, adler32=False, sha1=True, sha224=False, sha256=False, sha384=False, sha512=False, md5=True, md4=False):
	target = open(os.path.join(workingdir, 'all.cksum'), 'w')
	hashoutput_crc32 = "CRC32\n"
	hashoutput_adler32 = "ADLER32\n"
	hashoutput_sha1 = "SHA1\n"
	hashoutput_sha224 = "SHA224\n"
	hashoutput_sha256 = "SHA256\n"
	hashoutput_sha384 = "SHA384\n"
	hashoutput_sha512 = "SHA512\n"
	hashoutput_md5 = "MD5\n"
	hashoutput_md4 = "MD4\n"
	for file in os.listdir(workingdir):
		if os.path.isdir(os.path.join(workingdir, file)):
			pass  # exclude folders
		elif file.endswith(".cksum"):
			pass  # exclude already generated files
		else:
			if adler32 == True:
				print("Adler32:", str(file))
				result_adler32 = adler32hash(os.path.join(workingdir, file), blocksize)
				hashoutput_adler32 += str(result_adler32.upper())
				hashoutput_adler32 += " "
				hashoutput_adler32 += str(file)
				hashoutput_adler32 += " \n"
			if crc32 == True:
				print("CRC32:", str(file))
				result_crc32 = crc32hash(os.path.join(workingdir, file), blocksize)
				hashoutput_crc32 += str(result_crc32.upper())
				hashoutput_crc32 += " "
				hashoutput_crc32 += str(file)
				hashoutput_crc32 += " \n"
			if md4 == True:
				print("MD4:", str(file))
				result_md4 = md4hash(os.path.join(workingdir, file), blocksize)
				hashoutput_md4 += str(result_md4.upper())
				hashoutput_md4 += " "
				hashoutput_md4 += str(file)
				hashoutput_md4 += " \n"
			if md5 == True:
				print("MD5:", str(file))
				result_md5 = md5hash(os.path.join(workingdir, file), blocksize)
				hashoutput_md5 += str(result_md5.upper())
				hashoutput_md5 += " "
				hashoutput_md5 += str(file)
				hashoutput_md5 += " \n"
			if sha1 == True:
				print("SHA1:", str(file))
				result_sha1 = sha1hash(os.path.join(workingdir, file), blocksize)
				hashoutput_sha1 += str(result_sha1.upper())
				hashoutput_sha1 += " "
				hashoutput_sha1 += str(file)
				hashoutput_sha1 += " \n"
			if sha224 == True:
				print("SHA224:", str(file))
				result_sha224 = sha224hash(os.path.join(workingdir, file), blocksize)
				hashoutput_sha224 += str(result_sha224.upper())
				hashoutput_sha224 += " "
				hashoutput_sha224 += str(file)
				hashoutput_sha224 += " \n"
			if sha256 == True:
				print("SHA256:", str(file))
				result_sha256 = sha256hash(os.path.join(workingdir, file), blocksize)
				hashoutput_sha256 += str(result_sha256.upper())
				hashoutput_sha256 += " "
				hashoutput_sha256 += str(file)
				hashoutput_sha256 += " \n"
			if sha384 == True:
				print("SHA384:", str(file))
				result_sha384 = sha384hash(os.path.join(workingdir, file), blocksize)
				hashoutput_sha384 += str(result_sha384.upper())
				hashoutput_sha384 += " "
				hashoutput_sha384 += str(file)
				hashoutput_sha384 += " \n"
			if sha512 == True:
				print("SHA512:", str(file))
				result_sha512 = sha512hash(os.path.join(workingdir, file), blocksize)
				hashoutput_sha512 += str(result_sha512.upper())
				hashoutput_sha512 += " "
				hashoutput_sha512 += str(file)
				hashoutput_sha512 += " \n"
			print("\n")
	if adler32 == True:
		target.write(hashoutput_adler32 + "\n")
	if crc32 == True:
		target.write(hashoutput_crc32 + "\n")
	if md4 == True:
		target.write(hashoutput_md4 + "\n")
	if md5 == True:
		target.write(hashoutput_md5 + "\n")
	if sha1 == True:
		target.write(hashoutput_sha1 + "\n")
	if sha224 == True:
		target.write(hashoutput_sha224 + "\n")
	if sha256 == True:
		target.write(hashoutput_sha256 + "\n")
	if sha384 == True:
		target.write(hashoutput_sha384 + "\n")
	if sha512 == True:
		target.write(hashoutput_sha512 + "\n")
	target.close()

def ghettoConvert(intsize):
	hexsize = format(intsize, '08x')  # '00AABBCC'
	newlist = [hexsize[i:i + 2] for i in range(0, len(hexsize), 2)]  # ['00', 'AA','BB','CC']
	while "00" in newlist:
		newlist.remove("00")  # extra padding
	newlist.reverse()
	ghettoHex = "".join(newlist)  # 'CCBBAA'
	ghettoHex = ghettoHex.rjust(16, '0')
	return binascii.unhexlify(bytes(ghettoHex.upper(), 'ascii'))

def makeOffset(cap, firstfile, secondfile="", thirdfile="", fourthfile="", fifthfile="", sixthfile="", folder=os.getcwd()):
	filecount = 0
	filelist = [firstfile, secondfile, thirdfile, fourthfile, fifthfile, sixthfile]
	for i in filelist:
		if i:
			filecount += 1
	# immutable things
	separator = binascii.unhexlify("6ADF5D144E4B4D4E474F46464D4E532B170A0D1E0C14532B372A2D3E2C34522F3C534F514F514F514F534E464D514E4947514E51474F70709CD5C5979CD5C5979CD5C597") #3.11.0.18
	password = binascii.unhexlify("0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
	singlepad = binascii.unhexlify("00")
	doublepad = binascii.unhexlify("0000")
	signedpad = binascii.unhexlify("0000000000000000")
	filepad = binascii.unhexlify(bytes(str(filecount).rjust(2, '0'), 'ascii'))  # between 01 and 06
	trailermax = int(7 - int(filecount))
	trailermax = trailermax * 2
	trailer = "0" * trailermax  # 00 repeated between 1 and 6 times
	trailers = binascii.unhexlify(trailer)
		
	capfile = str(glob.glob(cap)[0])
	capsize = os.path.getsize(capfile)  # size of cap.exe, in bytes
	
	first = str(glob.glob(firstfile)[0])
	firstsize = os.path.getsize(first)  # required
	if (filecount >= 2):
		second = str(glob.glob(secondfile)[0])
		secondsize = os.path.getsize(second)
	if (filecount >= 3):
		third = str(glob.glob(thirdfile)[0])
		thirdsize = os.path.getsize(third)
	if (filecount >= 4):
		fourth = str(glob.glob(fourthfile)[0])
		fourthsize = os.path.getsize(fourth)
	if (filecount >= 5):
		fifth = str(glob.glob(fifthfile)[0])
		fifthsize = os.path.getsize(fifth)
		
	
	firstoffset = len(separator) + len(password) + 64 + capsize  # start of first file; length of cap + length of offset
	firststart = ghettoConvert(firstoffset)
	if (filecount >= 2):
		secondoffset = firstoffset + firstsize  # start of second file
		secondstart = ghettoConvert(secondoffset)
	if (filecount >= 3):
		thirdoffset = secondstart + secondsize  # start of third file
		thirdstart = ghettoConvert(thirdoffset)
	if (filecount >= 4):
		fourthoffset = thirdoffset + thirdsize  # start of fourth file
		fourthstart = ghettoConvert(fourthoffset)
	if (filecount >= 5):
		fifthoffset = fourthstart + fourthsize  # start of fifth file
		fifthstart = ghettoConvert(fifthoffset)
	if (filecount == 6):
		sixthoffset = fifthoffset + fifthsize  # start of sixth file
		sixthstart = ghettoConvert(sixthoffset)
		
	with open(os.path.join(folder, "offset.hex"), "w+b") as file:
		file.write(separator)
		file.write(password)
		file.write(filepad)
		file.write(doublepad)
		file.write(firststart)
		file.write(singlepad)
		if (filecount >= 2):
			file.write(secondstart)
		else:
			file.write(signedpad)
		file.write(singlepad)
		if (filecount >= 3):
			file.write(thirdstart)
		else:
			file.write(signedpad)
		file.write(singlepad)
		if (filecount >= 4):
			file.write(fourthstart)
		else:
			file.write(signedpad)
		file.write(singlepad)
		if (filecount >= 5):
			file.write(fifthstart)
		else:
			file.write(signedpad)
		file.write(singlepad)
		if (filecount == 6):
			file.write(sixthstart)
		else:
			file.write(signedpad)
		file.write(singlepad)
		file.write(doublepad)
		file.write(trailers)
		
def makeAutoloader(filename, cap, firstfile, secondfile="", thirdfile="", fourthfile="", fifthfile="", sixthfile="", folder=os.getcwd()):
	makeOffset(cap, firstfile, secondfile, thirdfile, fourthfile, fifthfile, sixthfile, folder)
	
	filecount = 0
	filelist = [firstfile, secondfile, thirdfile, fourthfile, fifthfile, sixthfile]
	for i in filelist:
		if i:
			filecount += 1
	try:
		with open(os.path.join(os.path.abspath(folder), filename), "wb") as autoloader:
			try:
				with open(os.path.normpath(cap), "rb") as capfile:
					print("WRITING CAP.EXE...")
					while True:
						chunk = capfile.read(4096)  # 4k chunks
						if not chunk:
							break
						autoloader.write(chunk)
			except IOError as e:
				print("Operation failed:", e.strerror)
			try:
				with open(os.path.join(folder, "offset.hex"), "rb") as offset:
					print("WRITING MAGIC OFFSET...")
					autoloader.write(offset.read())
			except IOError as e:
				print("Operation failed:", e.strerror)
			try:
				with open(firstfile, "rb") as first:
					print("WRITING SIGNED FILE #1...\n", firstfile)
					while True:
						chunk = first.read(4096)  # 4k chunks
						if not chunk:
							break
						autoloader.write(chunk)
			except IOError as e:
				print("Operation failed:", e.strerror)
			if (filecount >= 2):
				try:
					print("WRITING SIGNED FILE #2...\n", secondfile)
					with open(secondfile, "rb") as second:
						while True:
							chunk = second.read(4096)  # 4k chunks
							if not chunk:
								break
							autoloader.write(chunk)
				except IOError as e:
					print("Operation failed:", e.strerror)
			if (filecount >= 3):
				try:
					print("WRITING SIGNED FILE #3...\n", thirdfile)
					with open(thirdfile, "rb") as third:
						while True:
							chunk = third.read(4096)  # 4k chunks
							if not chunk:
								break
							autoloader.write(chunk)
				except IOError as e:
					print("Operation failed:", e.strerror)
			if (filecount >= 4):
				try:
					print("WRITING SIGNED FILE #5...\n", fourthfile)
					with open(fourthfile, "rb") as fourth:
						while True:
							chunk = fourth.read(4096)  # 4k chunks
							if not chunk:
								break
							autoloader.write(chunk)
				except IOError as e:
					print("Operation failed:", e.strerror)
			if (filecount >= 5):
				try:
					print("WRITING SIGNED FILE #5...\n", fifthfile)
					with open(fifthfile, "rb") as fifth:
						while True:
							chunk = fifth.read(4096)  # 4k chunks
							if not chunk:
								break
							autoloader.write(chunk)
				except IOError as e:
					print("Operation failed:", e.strerror)
			if (filecount == 6):
				try:
					print("WRITING SIGNED FILE #6...\n", sixthfile)
					with open(sixthfile, "rb") as sixth:
						while True:
							chunk = sixth.read(4096)  # 4k chunks
							if not chunk:
								break
							autoloader.write(chunk)
				except IOError as e:
					print("Operation failed:", e.strerror)
	except IOError as e:
		print("Operation failed:", e.strerror)
		
	print(filename, "FINISHED!\n")
	os.remove(os.path.join(folder, "offset.hex"))

def fileExists(file):
	if not os.path.exists(file):
		raise argparse.ArgumentError("{0} does not exist".format(file))
	return file

def updateCheck(version):
	update = False
	updatesite = "https://raw.githubusercontent.com/thurask/thurask.github.io/master/archivist.version"
	print("LOCAL VERSION:", version)
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  #silence warnings about no SSL
	get = requests.get(updatesite, verify=False)  # don't use SSL until I figure it out
	remote = str(get.text).strip()
	print("REMOTE VERSION:", remote)
	if (get.status_code != 404):
		if version != remote:
				update = True
		else:
			update = False
	return update

# http://pipe-devnull.com/2012/09/13/queued-threaded-http-downloader-in-python.html
# Modified to work with Python 3:
# Downloader class - reads queue and downloads each file in succession
class Downloader(threading.Thread):
	def __init__(self, queue, output_directory):
		threading.Thread.__init__(self, name=binascii.hexlify(os.urandom(8)))
		self.queue = queue
		self.output_directory = output_directory
	def run(self):
		while True:
			# gets the url from the queue
			url = self.queue.get()
			# download the file
			self.download(url)
			# send a signal to the queue that the job is done
			self.queue.task_done()
	def download(self, url):
		t_start = time.clock()
		local_filename = url.split('/')[-1]
		print("Downloading:", local_filename)
		r = requests.get(url, stream=True)
		if (r.status_code != 404):  # 200 OK
			fname = self.output_directory + "/" + os.path.basename(url)
			with open(fname, "wb") as f:
				for chunk in r.iter_content(chunk_size=1024): 
					if chunk:  # filter out keep-alive new chunks
						f.write(chunk)
						f.flush()
			t_elapsed = time.clock() - t_start
			t_elapsed_proper = math.ceil(t_elapsed * 100) / 100
			print("Downloaded " + url + " in " + str(t_elapsed_proper) + " seconds")
			f.close()
		else:
			print("* Thread: " + self.name + " Bad URL: " + url)
			return

# Spawns dowloader threads and manages URL downloads queue
class DownloadManager():
	def __init__(self, download_dict, output_directory, thread_count=5):
		self.thread_count = thread_count
		self.download_dict = download_dict
		self.output_directory = output_directory
	# Start the downloader threads, fill the queue with the URLs and
	# then feed the threads URLs via the queue
	def begin_downloads(self):
		dlqueue = queue.Queue()
		# Create i thread pool and give them a queue
		for t in range(self.thread_count):
			t = Downloader(dlqueue, self.output_directory)
			t.setDaemon(True)
			t.start()
		# Load the queue from the download dict
		for linkname in self.download_dict:
			# print uri
			dlqueue.put(self.download_dict[linkname])

		# Wait for the queue to finish
		dlqueue.join()
		return

# Handle bools
def str2bool(v):
	return str(v).lower() in ("yes", "true", "t", "1", "y")

# Get 64 or 32 bit
def is64Bit():
	amd64 = platform.machine().endswith("64")
	return amd64

# Set 7z executable based on bit type
def getSevenZip():
	if is64Bit() == True:
		return "7za64.exe"
	else:
		return "7za.exe"
	
# Get corecount, with fallback 
def getCoreCount():
	cores = str(os.cpu_count())  # thank you Python 3.4
	if os.cpu_count() == None:
		cores = str(1)
	return cores

# Extract bars with 7z
def extractBar(filepath):
	for file in os.listdir(filepath):
		if file.endswith(".bar"):
			try:
				subprocess.call(getSevenZip() + " x " + '"' + os.path.join(filepath, file) + '" *.signed -aos -o' + filepath, shell=True)
			except Exception:
				print("EXTRACTION FAILURE")
				print("DID IT DOWNLOAD PROPERLY?")
				return
	
# Compress loaders with 7z
# #WARNING: Requires a lot of RAM.
def compress(filepath):
	for file in os.listdir(filepath):
		if file.endswith(".exe") and file.startswith(("Q10", "Z10", "Z30", "Z3", "Passport")):
			print("COMPRESSING: " + os.path.splitext(os.path.basename(file))[0] + ".exe @mmt" + getCoreCount())
			if is64Bit() == True:
				strength = "-mx9" #ultra compression
			else:
				strength = "-mx5" #normal compression
			subprocess.call(getSevenZip() + " a " + strength + " -m0=lzma2 -mmt" + getCoreCount() + " " + os.path.join(filepath, os.path.splitext(os.path.basename(os.path.join(filepath, file)))[0] + '.7z') + " " + os.path.join(filepath, file), shell=True)

# Check if URL has HTTP 200 or HTTP 300-308 status code			 
def availability(url):
	try:
		av = requests.head(str(url))
	except requests.ConnectionError:
		return False
	else:
		status = int(av.status_code)
		if (status == 200) or (300 < status <= 308):
			return True
		else:
			return False

# Create autoloaders
def generateLoaders(osversion, radioversion, radios, cap="cap.exe", localdir=os.getcwd()):
	# #OS Images
	# 8960
	try:
		os_8960 = glob.glob(os.path.join(localdir, "*qc8960*_sfi.desktop*.signed"))[0]
	except IndexError:
		print("No 8960 image found")

	# 8x30 (10.3.1 MR+)
	try:
		os_8x30 = glob.glob(os.path.join(localdir,"*qc8x30*desktop*.signed"))[0]
	except IndexError:
		print("No 8x30 image found")
	
	# 8974
	try:
		os_8974 = glob.glob(os.path.join(localdir,"*qc8974*desktop*.signed"))[0]
	except IndexError:
		print("No 8974 image found")
	
	# OMAP (incl. 10.3.1)
	try:
		os_ti = glob.glob(os.path.join(localdir,"*winchester*.signed"))[0]
	except IndexError:
			print("No OMAP image found")
	
	# Radio files
	# STL100-1
	try:
		radio_z10_ti = glob.glob(os.path.join(localdir,"*radio.m5730*.signed"))[0]
	except IndexError:
		print("No OMAP radio found")
		
	# STL100-X
	try:
		radio_z10_qcm = glob.glob(os.path.join(localdir,"*radio.qc8960.BB*.signed"))[0]
	except IndexError:
		print("No 8960 radio found")
		
	# STL100-4
	try:
		radio_z10_vzw = glob.glob(os.path.join(localdir,"*radio.qc8960*omadm*.signed"))[0]
	except IndexError:
		print("No Verizon 8960 radio found")
		
	# Q10/Q5
	try:
		radio_q10 = glob.glob(os.path.join(localdir,"*8960*wtr.*.signed"))[0]
	except IndexError:
		print("No Q10/Q5 radio found")
		
	# Z30/Classic
	try:
		radio_z30 = glob.glob(os.path.join(localdir,"*8960*wtr5*.signed"))[0]
	except IndexError:
		print("No Z30/Classic radio found")
		
	# Z3
	try:
		radio_z3 = glob.glob(os.path.join(localdir,"*8930*wtr5*.signed"))[0]
	except IndexError:
		print("No Z3 radio found")
		
	# Passport
	try:
		radio_8974 = glob.glob(os.path.join(localdir,"*8974*wtr2*.signed"))[0]
	except IndexError:
		print("No Passport radio found")
			
	# Pretty format names
	splitos = osversion.split(".")
	if len(splitos[2]) == 1:
		splitos[2] = "0" + splitos[2]
	osversion = ".".join(splitos)
	splitrad = radioversion.split(".")
	if len(splitrad[2]) == 1:
		splitrad[2] = "0" + splitrad[2]
	radioversion = ".".join(splitrad)
	
	# Generate loaders
	# STL100-1
	try:
		print("Creating OMAP Z10 OS...")
		makeAutoloader(filename="Z10_" + osversion + "_STL100-1.exe", cap=cap, firstfile=os_ti, secondfile=radio_z10_ti, thirdfile="", fourthfile="", fifthfile="", sixthfile="", folder=localdir)
	except Exception:
		print("Could not create STL100-1 OS/radio loader")
	if radios == True:
		print("Creating OMAP Z10 radio...")
		try:
			makeAutoloader("Z10_" + radioversion + "_STL100-1.exe", cap, radio_z10_ti, folder=localdir)
		except Exception:
			print("Could not create STL100-1 radio loader")

	# STL100-X
	try:
		print("Creating Qualcomm Z10 OS...")
		makeAutoloader("Z10_" + osversion + "_STL100-2-3.exe", cap, os_8960, radio_z10_qcm, folder=localdir)
	except Exception:
		print("Could not create Qualcomm Z10 OS/radio loader")
	if radios == True:
		print("Creating Qualcomm Z10 radio...")
		try:
			makeAutoloader("Z10_" + radioversion + "_STL100-2-3.exe", cap, radio_z10_qcm, folder=localdir)
		except Exception:
			print("Could not create Qualcomm Z10 radio loader")

	# STL100-4
	try:
		print("Creating Verizon Z10 OS...")
		makeAutoloader("Z10_" + osversion + "_STL100-4.exe", cap, os_8960, radio_z10_vzw, folder=localdir)
	except Exception:
		print("Could not create Verizon Z10 OS/radio loader")
	if radios == True:
		print("Creating Verizon Z10 radio...")
		try:
			makeAutoloader("Z10_" + radioversion + "_STL100-4.exe", cap, radio_z10_vzw, folder=localdir)
		except Exception:
			print("Could not create Verizon Z10 radio loader")

	# Q10/Q5
	try:
		print("Creating Q10/Q5 OS...")
		makeAutoloader("Q10_" + osversion + "_SQN100-1-2-3-4-5.exe", cap, os_8960, radio_q10, folder=localdir)
	except Exception:
		print("Could not create Q10/Q5 OS/radio loader")
	if radios == True:
		print("Creating Q10/Q5 radio...")
		try:
			makeAutoloader("Q10_" + radioversion + "_SQN100-1-2-3-4-5.exe", cap, radio_q10, folder=localdir)
		except Exception:
			print("Could not create Q10/Q5 radio loader")

	# Z30/Classic
	try:
		print("Creating Z30/Classic OS...")
		makeAutoloader("Z30_" + osversion + "_STA100-1-2-3-4-5-6.exe", cap, os_8960, radio_z30, folder=localdir)
	except Exception:
		print("Could not create Z30/Classic OS/radio loader")
	if radios == True:
		print("Creating Z30/Classic radio...")
		try:
			makeAutoloader("Z30_" + radioversion + "_STA100-1-2-3-4-5-6.exe", cap, radio_z30, folder=localdir)
		except Exception:
			print("Could not create Z30/Classic radio loader")

	# Z3
	try:
		print("Creating Z3 OS...")
		makeAutoloader("Z3_" + osversion + "_STJ100-1-2.exe", cap, os_8x30, radio_z3, folder=localdir)
	except Exception:
		print("Could not create Z3 OS/radio loader (8x30)")
	if radios == True:
		print("Creating Z3 radio...")
		try:
			makeAutoloader("Z3_" + radioversion + "_STJ100-1-2.exe", cap, radio_z3, folder=localdir)
		except Exception:
			print("Could not create Z3 radio loader")

	# Passport	
	try:
		print("Creating Passport OS...")
		makeAutoloader("Passport_" + osversion + "_SQW100-1-2-3.exe", cap, os_8974, radio_8974, folder=localdir)
	except Exception:
		print("Could not create Passport OS/radio loader")
	if radios == True:
		print("Creating Passport radio...")
		try:
			makeAutoloader("Passport_" + radioversion + "_SQW100-1-2-3.exe", cap, radio_8974, folder=localdir)
		except Exception:
			print("Could not create Passport radio loader")

def doMagic(osversion, radioversion, softwareversion, localdir, radios=True, compressed=True, deleted=True, hashed=True, crc32=False, adler32=False, sha1=True, sha224=False, sha256=False, sha384=False, sha512=False, md5=True, md4=False, cappath="cap.exe", download=True, extract=True, loaders=True, signed=True):
	starttime = time.clock()
	version = "2015-04-12-A"  # update as needed
	release = "https://github.com/thurask/archivist/releases/latest"
	
	print("~~~ARCHIVIST VERSION", version + "~~~")
	print("OS VERSION:", osversion)
	print("RADIO VERSION:", radioversion)
	print("SOFTWARE VERSION:", softwareversion)
	
	print("\nCHECKING FOR UPDATES...")
	update = updateCheck(version)
	if update == True:
		print("UPDATE AVAILABLE!")
		invoke = str2bool(input("DOWNLOAD UPDATE? Y/N: "))
		if invoke == True:
			webbrowser.open(release)
			print("CLOSING...")
			raise SystemExit  # bye
		else:
			pass
	else:
		print("NO UPDATE AVAILABLE...")
	
	# Hash software version
	swhash = hashlib.sha1(softwareversion.encode('utf-8'))
	hashedsoftwareversion = swhash.hexdigest()
	
	# Root of all urls
	baseurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + hashedsoftwareversion
	
	# List of OS urls
	osurls = [baseurl + "/winchester.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar",
		baseurl + "/qc8960.factory_sfi.desktop-" + osversion + "-nto+armle-v7+signed.bar",
		baseurl + "/qc8960.factory_sfi_hybrid_qc8x30.desktop-" + osversion + "-nto+armle-v7+signed.bar",
		baseurl + "/qc8960.factory_sfi_hybrid_qc8974.desktop-" + osversion + "-nto+armle-v7+signed.bar"]

	# List of radio urls
	radiourls = [baseurl + "/m5730-" + radioversion + "-nto+armle-v7+signed.bar",
		baseurl + "/qc8960-" + radioversion + "-nto+armle-v7+signed.bar",
		baseurl + "/qc8960.omadm-" + radioversion + "-nto+armle-v7+signed.bar",
		baseurl + "/qc8960.wtr-" + radioversion + "-nto+armle-v7+signed.bar",
		baseurl + "/qc8960.wtr5-" + radioversion + "-nto+armle-v7+signed.bar",
		baseurl + "/qc8930.wtr5-" + radioversion + "-nto+armle-v7+signed.bar",
		baseurl + "/qc8974.wtr2-" + radioversion + "-nto+armle-v7+signed.bar"]

	# Add URLs to dict, programmatically
	osdict = {}
	radiodict = {}
	for i in osurls:
		osdict[str(i)] = i
	for i in radiourls:
		radiodict[str(i)] = i
		
	# Check availability of software release
	av = availability(baseurl)
	if(av == True):
		print("\nSOFTWARE RELEASE", softwareversion, "EXISTS")
	else:
		print("\nSOFTWARE RELEASE", softwareversion, "NOT FOUND")
		cont = str2bool(input("CONTINUE? Y/N "))
		if (cont == True):
			pass
		else:
			print("\nEXITING...")
			raise SystemExit  # bye bye
	
	# Make dirs
	if not os.path.exists(os.path.join(localdir, 'bars')):
		os.mkdir(os.path.join(localdir, 'bars'))
	bardir = os.path.join(localdir, 'bars')
	if not os.path.exists(os.path.join(bardir, osversion)):
		os.mkdir(os.path.join(bardir, osversion))
	bardir_os = os.path.join(bardir, osversion)
	if not os.path.exists(os.path.join(bardir, radioversion)):
		os.mkdir(os.path.join(bardir, radioversion))
	bardir_radio = os.path.join(bardir, radioversion)

	if not os.path.exists(os.path.join(localdir, 'loaders')):
		os.mkdir(os.path.join(localdir, 'loaders'))
	loaderdir = os.path.join(localdir, 'loaders')
	if not os.path.exists(os.path.join(loaderdir, osversion)):
		os.mkdir(os.path.join(loaderdir, osversion))
	loaderdir_os = os.path.join(loaderdir, osversion)
	if not os.path.exists(os.path.join(loaderdir, radioversion)):
		os.mkdir(os.path.join(loaderdir, radioversion))
	loaderdir_radio = os.path.join(loaderdir, radioversion)

	if not os.path.exists(os.path.join(localdir, 'zipped')):
		os.mkdir(os.path.join(localdir, 'zipped'))
	zipdir = os.path.join(localdir, 'zipped')
	if not os.path.exists(os.path.join(zipdir, osversion)):
		os.mkdir(os.path.join(zipdir, osversion))
	zipdir_os = os.path.join(zipdir, osversion)
	if not os.path.exists(os.path.join(zipdir, radioversion)):
		os.mkdir(os.path.join(zipdir, radioversion))
	zipdir_radio = os.path.join(zipdir, radioversion)
	
	# Download files
	if download == True:
		print("\nBEGIN DOWNLOADING...")
		download_manager = DownloadManager(radiodict, localdir, 5)
		download_manager.begin_downloads()
		download_manager.download_dict = osdict
		download_manager.begin_downloads()
		
	# Extract bar files
	if extract == True:
		print("\nEXTRACTING...")
		extractBar(localdir)
	
	# Move bar files
	print("\nMOVING .bar FILES...")
	for files in os.listdir(localdir):
		if files.endswith(".bar"):
			print("MOVING: " + files)
			bardest_os = os.path.join(bardir_os, files)
			bardest_radio = os.path.join(bardir_radio, files)
			if os.path.getsize(os.path.join(localdir, files)) > 90000000:  # even the fattest radio is less than 90MB
				try:
					shutil.move(os.path.join(localdir, files), bardir_os)
				except shutil.Error:
					os.remove(bardest_os)
			else:
				try:
					shutil.move(os.path.join(localdir, files), bardir_radio)
				except shutil.Error:
					os.remove(bardest_radio)

	# Create loaders
	if loaders == True:
		print("\nGENERATING LOADERS...\n")
		generateLoaders(osversion, radioversion, radios, cappath, localdir)

	# Remove .signed files
	if signed == True:
		print("\nREMOVING .signed FILES...")
		for file in os.listdir(localdir):
			if os.path.join(localdir, file).endswith(".signed"):
				print("REMOVING: " + file)
				os.remove(os.path.join(localdir, file))

	# If compression = true, compress
	if compressed == True:
		print("\nCOMPRESSING...")
		compress(localdir)
	else:
		pass

	# Move zipped/unzipped loaders
	print("\nMOVING...")
	for files in os.listdir(localdir):
		if files.endswith(".exe") and files.startswith(("Q10", "Z10", "Z30", "Z3", "Passport")):
			print("MOVING: " + files)
			loaderdest_os = os.path.join(loaderdir_os, files)
			loaderdest_radio = os.path.join(loaderdir_radio, files)
			if os.path.getsize(os.path.join(localdir, files)) > 90000000:  # even the fattest radio is less than 90MB
				try:
					shutil.move(os.path.join(localdir, files), loaderdir_os)
				except shutil.Error:
					os.remove(loaderdest_os)
			else:
				try:
					shutil.move(os.path.join(localdir, files), loaderdir_radio)
				except shutil.Error:
					os.remove(loaderdest_radio)
		if files.endswith(".7z"):
				print("MOVING: " + files)
				zipdest_os = os.path.join(zipdir_os, files)
				zipdest_radio = os.path.join(zipdir_radio, files)
				if os.path.getsize(os.path.join(localdir, files)) > 90000000:  # even the fattest radio is less than 90MB
					try:
						shutil.move(os.path.join(localdir, files), zipdir_os)
					except shutil.Error:
						os.remove(zipdest_os)
				else:
					try:
						shutil.move(os.path.join(localdir, files), zipdir_radio)
					except shutil.Error:
						os.remove(zipdest_radio)
	# Get hashes (if specified)
	if hashed == True:
		print("\nHASHING LOADERS...")
		print("ADLER32:", adler32, "CRC32:", crc32, "MD4:", md4, "\nMD5:", md5, "SHA1:", sha1, "SHA224:", sha224, "\nSHA256:", sha256, "SHA384:", sha384, "SHA512:", sha512, "\n")
		blocksize = 32*1024*1024
		#if compressed == True:
		verifier(zipdir_os, blocksize, crc32, adler32, sha1, sha224, sha256, sha384, sha512, md5, md4)
		verifier(zipdir_radio, blocksize, crc32, adler32, sha1, sha224, sha256, sha384, sha512, md5, md4)
		if deleted == False:
			verifier(loaderdir_os, blocksize, crc32, adler32, sha1, sha224, sha256, sha384, sha512, md5, md4)
			verifier(loaderdir_radio, blocksize, crc32, adler32, sha1, sha224, sha256, sha384, sha512, md5, md4)

	# Remove uncompressed loaders (if specified)
	if deleted == True:
		print("\nDELETING UNCOMPRESSED LOADERS...")
		shutil.rmtree(loaderdir)
	
	# Delete empty folders
	if compressed == False:
		if (not os.listdir(zipdir_os)) and (not os.listdir(zipdir_radio)):
			shutil.rmtree(zipdir) # no zipped files if we didn't make them
	if radios == False:
		if deleted == False:
			if not os.listdir(loaderdir_radio):
				shutil.rmtree(loaderdir_radio) # we don't want to keep an empty radio dir with our non-empty os dir
		if compressed == True:
			if not os.listdir(zipdir_radio):
				shutil.rmtree(zipdir_radio) # as above, but for zipped radios

	print("\nFINISHED!")
	endtime = time.clock() - starttime
	endtime_proper = math.ceil(endtime * 100) / 100
	print("Completed in " + str(endtime_proper) + " seconds")

if __name__ == '__main__':
	if len(sys.argv) > 1:
		parser = argparse.ArgumentParser(description="Download bar files, create autoloaders.", usage="%(prog)s OSVERSION RADIOVERSION SWVERSION [options]", epilog="http://github.com/thurask/archivist")
		parser.add_argument("os", help="OS version, 10.x.y.zzzz")
		parser.add_argument("radio", help="Radio version, 10.x.y.zzzz")
		parser.add_argument("swrelease", help="Software version, 10.x.y.zzzz")
		parser.add_argument("-f", "--folder", type=fileExists, dest="folder", help="Working folder", default=os.getcwd())
		parser.add_argument("-c", "--cap-path", type=fileExists, dest="cappath", help="Path to cap.exe", default=os.path.join(os.getcwd(), "cap.exe"))
		parser.add_argument("-no", "--no-download", dest="download", help="Don't download files", action="store_false", default=True)
		parser.add_argument("-nx", "--no-extract", dest="extract", help="Don't extract bar files", action="store_false", default=True)
		parser.add_argument("-nl", "--no-loaders", dest="loaders", help="Don't create autoloaders", action="store_false", default=True)
		parser.add_argument("-nr", "--no-radios", dest="radloaders", help="Don't make radio autoloaders", action="store_false", default=True)
		parser.add_argument("-ns", "--no-rmsigned", dest="signed", help="Don't remove signed files", action="store_false", default=True)
		parser.add_argument("-nc", "--no-compress", dest="compress", help="Don't compress loaders", action="store_false", default=True)
		parser.add_argument("-nd", "--no-delete", dest="delete", help="Don't delete uncompressed loaders", action="store_false", default=True)
		parser.add_argument("-nv", "--no-verify", dest="verify", help="Don't verify created loaders", action="store_false", default=True)
		parser.add_argument("--crc32", dest="crc32", help="Enable CRC32 verification", action="store_true", default=False)
		parser.add_argument("--adler32", dest="adler32", help="Enable Adler-32 verification", action="store_true", default=False)
		parser.add_argument("--md4", dest="md4", help="Enable MD4 verification", action="store_true", default=False)
		parser.add_argument("--sha224", dest="sha224", help="Enable SHA-224 verification", action="store_true", default=False)
		parser.add_argument("--sha384", dest="sha384", help="Enable SHA-384 verification", action="store_true", default=False)
		parser.add_argument("--sha512", dest="sha512", help="Enable SHA-512 verification", action="store_true", default=False)
		parser.add_argument("--no-sha1", dest="sha1", help="Disable SHA-1 verification", action="store_false", default=True)
		parser.add_argument("--no-sha256", dest="sha256", help="Disable SHA-256 verification", action="store_false", default=True)
		parser.add_argument("--no-md5", dest="md5", help="Disable MD5 verification", action="store_false", default=True)
		args = parser.parse_args(sys.argv[1:])
		doMagic(args.os, args.radio, args.swrelease, args.folder, args.radloaders, args.compress, args.delete, args.verify, args.crc32, args.adler32, args.sha1, args.sha224, args.sha256, args.sha384, args.sha512, args.md5, args.md4, args.cappath, args.download, args.extract, args.loaders, args.signed)
	else:
		localdir = os.getcwd()
		osversion = input("OS VERSION: ")
		radioversion = input("RADIO VERSION: ")
		softwareversion = input("SOFTWARE RELEASE: ")
		radios = str2bool(input("CREATE RADIO LOADERS? Y/N: "))
		compressed = str2bool(input("COMPRESS LOADERS? Y/N: "))
		if compressed == True:
			deleted = str2bool(input("DELETE UNCOMPRESSED? Y/N: "))
		else:
			deleted = False
		hashed = str2bool(input("GENERATE HASHES? Y/N: "))
		print(" ")
		doMagic(osversion, radioversion, softwareversion, localdir, radios, compressed, deleted, hashed, False, False, True, False, False, False, False, True, False, "cap.exe", True, True, True, True)
	smeg = input("Press Enter to exit")
