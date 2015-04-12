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
import zlib  # CRC32, Adler32
import sys  # arguments
import argparse  # argument parsing
import time  # time for downloader
import queue  # downloader multithreading
import threading  # downloader multithreading
import binascii  # downloader thread naming
import math  # rounding of floats
import webbrowser  # invoke browser if update is there
import subprocess # invocation of 7z, cap

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
				subprocess.call(getSevenZip() + " x " + '"' + file + '" *.signed -aos', shell=True)
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
				subprocess.call(getSevenZip() + " a -mx9 -m0=lzma2 -mmt" + getCoreCount() + " " + '"' + os.path.splitext(os.path.basename(file))[0] + '.7z" "' + file + '"', shell=True)  # ultra compression
			else:
				subprocess.call(getSevenZip() + " a -mx5 -m0=lzma2 -mmt" + getCoreCount() + " " + '"' + os.path.splitext(os.path.basename(file))[0] + '.7z" "' + file + '"', shell=True)  # normal compression

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
# Hash/verification functions; perform operation on specific file
# CRC32
def crc32hash(filepath):
	seed = 0
	with open(filepath, 'rb') as file:
		for line in file:
			seed = zlib.crc32(line, seed)
	final = format(seed & 0xFFFFFFFF, "x")
	return final

# Adler32
def adler32hash(filepath, blocksize=16 * 1024 * 1024):
	with open(filepath, "rb") as f:
		data = f.read(blocksize)
		seed = zlib.adler32(data)
		rdata = f.read(blocksize)
		while rdata:
			for i in range(len(rdata)):
				seed = zlib.adler32(data[i:]+rdata[:i])
			data = rdata
			rdata = f.read(blocksize)
	final = format(seed & 0xFFFFFFFF, "x")
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
def verifier(workingdir, blocksize=16 * 1024 * 1024, crc32=False, adler32=False, sha1=True, sha224=False, sha256=False, sha384=False, sha512=False, md5=True):
	print("ADLER32:", adler32, "CRC32:", crc32, "MD5:", md5, "\nSHA1:", sha1, "SHA224:", sha224, "SHA256:", sha256, "\nSHA384:", sha384, "SHA512:", sha512, "\n")
	hashoutput_crc32 = "CRC32\n"
	hashoutput_adler32 = "Adler32\n"
	hashoutput_sha1 = "SHA1\n"
	hashoutput_sha224 = "SHA224\n"
	hashoutput_sha256 = "SHA256\n"
	hashoutput_sha384 = "SHA384\n"
	hashoutput_sha512 = "SHA512\n"
	hashoutput_md5 = "MD5\n"
	for file in os.listdir(workingdir):
		if os.path.isdir(os.path.join(workingdir, file)):
			pass  # exclude folders
		elif file.endswith(".cksum"):
			pass  # exclude already generated files
		else:
			if adler32 == True:
				print("Adler32:", str(file))
				result_adler32 = adler32hash(os.path.join(workingdir, file))
				hashoutput_adler32 += str(result_adler32.upper())
				hashoutput_adler32 += " "
				hashoutput_adler32 += str(file)
				hashoutput_adler32 += " \n"
			if md5 == True:
				print("MD5:", str(file))
				result_md5 = md5hash(os.path.join(workingdir, file))
				hashoutput_md5 += str(result_md5.upper())
				hashoutput_md5 += " "
				hashoutput_md5 += str(file)
				hashoutput_md5 += " \n"
			if crc32 == True:
				print("CRC32:", str(file))
				result_crc32 = crc32hash(os.path.join(workingdir, file))
				hashoutput_crc32 += str(result_crc32.upper())
				hashoutput_crc32 += " "
				hashoutput_crc32 += str(file)
				hashoutput_crc32 += " \n"
			if sha1 == True:
				print("SHA1:", str(file))
				result_sha1 = sha1hash(os.path.join(workingdir, file))
				hashoutput_sha1 += str(result_sha1.upper())
				hashoutput_sha1 += " "
				hashoutput_sha1 += str(file)
				hashoutput_sha1 += " \n"
			if sha224 == True:
				print("SHA224:", str(file))
				result_sha224 = sha224hash(os.path.join(workingdir, file))
				hashoutput_sha224 += str(result_sha224.upper())
				hashoutput_sha224 += " "
				hashoutput_sha224 += str(file)
				hashoutput_sha224 += " \n"
			if sha256 == True:
				print("SHA256:", str(file))
				result_sha256 = sha256hash(os.path.join(workingdir, file))
				hashoutput_sha256 += str(result_sha256.upper())
				hashoutput_sha256 += " "
				hashoutput_sha256 += str(file)
				hashoutput_sha256 += " \n"
			if sha384 == True:
				print("SHA384:", str(file))
				result_sha384 = sha384hash(os.path.join(workingdir, file))
				hashoutput_sha384 += str(result_sha384.upper())
				hashoutput_sha384 += " "
				hashoutput_sha384 += str(file)
				hashoutput_sha384 += " \n"
			if sha512 == True:
				print("SHA512:", str(file))
				result_sha512 = sha512hash(os.path.join(workingdir, file))
				hashoutput_sha512 += str(result_sha512.upper())
				hashoutput_sha512 += " "
				hashoutput_sha512 += str(file)
				hashoutput_sha512 += " \n"
			print("\n")
	target = open(os.path.join(workingdir, 'all.cksum'), 'w')
	if adler32 == True:
		target.write(hashoutput_adler32 + "\n")
	if crc32 == True:
		target.write(hashoutput_crc32 + "\n")
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
		
def generateLoaders(osversion, radioversion, radios):
	# #OS Images
	# 8960
	try:
		os_8960 = str(glob.glob("*qc8960*_sfi.desktop*.signed")[0])
	except IndexError:
		print("No 8960 image found")

	# 8x30 (10.3.1 MR+)
	try:
		os_8x30 = str(glob.glob("*qc8x30*desktop*.signed")[0])
	except IndexError:
		print("No 8x30 image found")

	# 8974
	try:
		os_8974 = str(glob.glob("*qc8974*desktop*.signed")[0])
	except IndexError:
		print("No 8974 image found")

	# OMAP (incl. 10.3.1)
	try:
		os_ti = str(glob.glob("*winchester*.signed")[0])
	except IndexError:
			print("No OMAP image found")
			
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
		radio_z10_ti = str(glob.glob("*radio.m5730*.signed")[0])
	except IndexError:
		print("No OMAP radio found")
	else:
		print("Creating OMAP Z10 OS...")
		try:
			subprocess.call("cap.exe create " + os_ti + " " + radio_z10_ti + " Z10_" + osversion + "_STL100-1.exe", shell=True)
		except Exception:
			print("Could not create STL100-1 OS/radio loader")
		if radios == True:
			print("Creating OMAP Z10 radio...")
			try:
				subprocess.call("cap.exe create " + radio_z10_ti + " Z10_" + radioversion + "_STL100-1.exe", shell=True)
			except Exception:
				print("Could not create STL100-1 radio loader")

	# STL100-X
	try:
		radio_z10_qcm = str(glob.glob("*radio.qc8960.BB*.signed")[0])
	except IndexError:
		print("No 8960 radio found")
	else:
		print("Creating Qualcomm Z10 OS...")
		try:
			subprocess.call("cap.exe create " + os_8960 + " " + radio_z10_qcm + " Z10_" + osversion + "_STL100-2-3.exe", shell=True)
		except Exception:
			print("Could not create Qualcomm Z10 OS/radio loader")
		if radios == True:
			print("Creating Qualcomm Z10 radio...")
			try:
				subprocess.call("cap.exe create " + radio_z10_qcm + " Z10_" + radioversion + "_STL100-2-3.exe", shell=True)
			except Exception:
				print("Could not create Qualcomm Z10 radio loader")

	# STL100-4
	try:
		radio_z10_vzw = str(glob.glob("*radio.qc8960*omadm*.signed")[0])
	except IndexError:
		print("No Verizon 8960 radio found")
	else:
		print("Creating Verizon Z10 OS...")
		try:
			subprocess.call("cap.exe create " + os_8960 + " " + radio_z10_vzw + " Z10_" + osversion + "_STL100-4.exe", shell=True)
		except Exception:
			print("Could not create Verizon Z10 OS/radio loader")
		if radios == True:
			print("Creating Verizon Z10 radio...")
			try:
				subprocess.call("cap.exe create " + radio_z10_vzw + " Z10_" + radioversion + "_STL100-4.exe", shell=True)
			except Exception:
				print("Could not create Verizon Z10 radio loader")

	# Q10/Q5
	try:
		radio_q10 = str(glob.glob("*8960*wtr.*.signed")[0])
	except IndexError:
		print("No Q10/Q5 radio found")
	else:
		print("Creating Q10/Q5 OS...")
		try:
			subprocess.call("cap.exe create " + os_8960 + " " + radio_q10 + " Q10_" + osversion + "_SQN100-1-2-3-4-5.exe", shell=True)
		except Exception:
			print("Could not create Q10/Q5 OS/radio loader")
		if radios == True:
			print("Creating Q10/Q5 radio...")
			try:
				subprocess.call("cap.exe create " + radio_q10 + " Q10_" + radioversion + "_SQN100-1-2-3-4-5.exe", shell=True)
			except Exception:
				print("Could not create Q10/Q5 radio loader")

	# Z30/Classic
	try:
		radio_z30 = str(glob.glob("*8960*wtr5*.signed")[0])
	except IndexError:
		print("No Z30/Classic radio found")
	else:
		print("Creating Z30/Classic OS...")
		try:
			subprocess.call("cap.exe create " + os_8960 + " " + radio_z30 + " Z30_" + osversion + "_STA100-1-2-3-4-5-6.exe", shell=True)
		except Exception:
			print("Could not create Z30/Classic OS/radio loader")
		if radios == True:
			print("Creating Z30/Classic radio...")
			try:
				subprocess.call("cap.exe create " + radio_z30 + " Z30_" + radioversion + "_STA100-1-2-3-4-5-6.exe", shell=True)
			except Exception:
				print("Could not create Z30/Classic radio loader")



	# Z3 (more damn hybrids)
	try:
		radio_z3 = str(glob.glob("*8930*wtr5*.signed")[0])
	except IndexError:
		print("No Z3 radio found")
	else:
		print("Creating Z3 OS...")
		try:
			subprocess.call("cap.exe create " + os_8x30 + " " + radio_z3 + " Z3_" + osversion + "_STJ100-1-2.exe", shell=True)
		except Exception:
			print("Could not create Z3 OS/radio loader (8x30)")
		if radios == True:
			print("Creating Z3 radio...")
			try:
				subprocess.call("cap.exe create " + radio_z3 + " Z3_" + radioversion + "_STJ100-1-2.exe", shell=True)
			except Exception:
				print("Could not create Z3 radio loader")

	# Passport
	try:
		radio_8974 = str(glob.glob("*8974*wtr2*.signed")[0])
	except NameError:
		print("No 8974 OS found")
	except IndexError:
		print("No Passport radio found")
	else:
		print("Creating Passport OS...")
		try:
			subprocess.call("cap.exe create " + os_8974 + " " + radio_8974 + " Passport_" + osversion + "_SQW100-1-2-3.exe", shell=True)
		except Exception:
			print("Could not create Passport OS/radio loader")
		if radios == True:
			print("Creating Passport radio...")
			try:
				subprocess.call("cap.exe create " + radio_8974 + " Passport_" + radioversion + "_SQW100-1-2-3.exe", shell=True)
			except Exception:
				print("Could not create Passport radio loader")

def doMagic(osversion, radioversion, softwareversion, localdir, radios=True, compressed=True, deleted=True, hashed=True, crc32=False, adler32=False, sha1=True, sha224=False, sha256=False, sha384=False, sha512=False, md5=True):
	version = "2015-04-11-C"  # update as needed
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
	print("\nBEGIN DOWNLOADING...")
	download_manager = DownloadManager(radiodict, localdir, 5)
	download_manager.begin_downloads()
	download_manager.download_dict = osdict
	download_manager.begin_downloads()
		
	# Extract bar files
	print("\nEXTRACTING...")
	extractBar(localdir)
	
	# Move bar files
	print("\nMOVING .bar FILES...")
	for files in os.listdir(localdir):
		if files.endswith(".bar"):
			print("MOVING: " + files)
			bardest_os = os.path.join(bardir_os, files)
			bardest_radio = os.path.join(bardir_radio, files)
			if os.path.getsize(files) > 90000000:  # even the fattest radio is less than 90MB
				try:
					shutil.move(files, bardir_os)
				except shutil.Error:
					os.remove(bardest_os)
			else:
				try:
					shutil.move(files, bardir_radio)
				except shutil.Error:
					os.remove(bardest_radio)

	# Create loaders
	print("\nGENERATING LOADERS...")
	generateLoaders(osversion, radioversion, radios)

	# Remove .signed files
	print("\nREMOVING .signed FILES...")
	for file in os.listdir(localdir):
		if file.endswith(".signed"):
			print("REMOVING: " + file)
			os.remove(file)

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
			if os.path.getsize(files) > 90000000:  # even the fattest radio is less than 90MB
				try:
					shutil.move(files, loaderdir_os)
				except shutil.Error:
					os.remove(loaderdest_os)
			else:
				try:
					shutil.move(files, loaderdir_radio)
				except shutil.Error:
					os.remove(loaderdest_radio)
		if compressed == True:
			if files.endswith(".7z"):
				print("MOVING: " + files)
				zipdest_os = os.path.join(zipdir_os, files)
				zipdest_radio = os.path.join(zipdir_radio, files)
				if os.path.getsize(files) > 90000000:  # even the fattest radio is less than 90MB
					try:
						shutil.move(files, zipdir_os)
					except shutil.Error:
						os.remove(zipdest_os)
				else:
					try:
						shutil.move(files, zipdir_radio)
					except shutil.Error:
						os.remove(zipdest_radio)

	# Get hashes (if specified)
	if hashed == True:
		print("\nHASHING LOADERS...")
		if compressed == True:
			verifier(zipdir_os, 16 * 1024 * 1024, crc32, adler32, sha1, sha224, sha256, sha384, sha512, md5)
			verifier(zipdir_radio, 16 * 1024 * 1024, crc32, adler32, sha1, sha224, sha256, sha384, sha512, md5)
		if deleted == False:
			verifier(loaderdir_os, 16 * 1024 * 1024, crc32, adler32, sha1, sha224, sha256, sha384, sha512, md5)
			verifier(loaderdir_radio, 16 * 1024 * 1024, crc32, adler32, sha1, sha224, sha256, sha384, sha512, md5)

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

if __name__ == '__main__':
	if len(sys.argv) > 1:
		parser = argparse.ArgumentParser(description="Download bar files, create autoloaders.", usage="%(prog)s OSVERSION RADIOVERSION SWVERSION [options]", epilog="http://github.com/thurask/archivist")
		parser.add_argument("os", help="OS version, 10.x.y.zzzz")
		parser.add_argument("radio", help="Radio version, 10.x.y.zzzz")
		parser.add_argument("swrelease", help="Software version, 10.x.y.zzzz")
		parser.add_argument("--no-radio-loaders", dest="radloaders", help="Don't make radio loaders", action="store_false", default=True)
		parser.add_argument("--no-compress", dest="compress", help="Don't compress loaders", action="store_false", default=True)
		parser.add_argument("--no-delete-uncomp", dest="delete", help="Don't delete uncompressed loaders", action="store_false", default=True)
		parser.add_argument("--no-verify", dest="verify", help="Don't verify created loaders", action="store_false", default=True)
		parser.add_argument("--crc32", dest="crc32", help="Enable CRC32 verification", action="store_true", default=False)
		parser.add_argument("--adler32", dest="adler32", help="Enable Adler-32 verification", action="store_true", default=False)
		parser.add_argument("--sha224", dest="sha224", help="Enable SHA-224 verification", action="store_true", default=False)
		parser.add_argument("--sha384", dest="sha384", help="Enable SHA-384 verification", action="store_true", default=False)
		parser.add_argument("--sha512", dest="sha512", help="Enable SHA-512 verification", action="store_true", default=False)
		parser.add_argument("--no-sha1", dest="sha1", help="Disable SHA-1 verification", action="store_false", default=True)
		parser.add_argument("--no-sha256", dest="sha256", help="Disable SHA-256 verification", action="store_false", default=True)
		parser.add_argument("--no-md5", dest="md5", help="Disable MD5 verification", action="store_false", default=True)
		args = parser.parse_args(sys.argv[1:])
		doMagic(args.os, args.radio, args.swrelease, os.getcwd(), args.radloaders, args.compress, args.delete, args.verify, args.crc32, args.adler32, args.sha1, args.sha224, args.sha256, args.sha384, args.sha512, args.md5)
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
		doMagic(osversion, radioversion, softwareversion, localdir, radios, compressed, deleted, hashed, False, False, True, False, False, False, False, True)
	smeg = input("Press Enter to exit")
