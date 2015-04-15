#!/usr/bin/env python3
"""
ARCHIVIST

A Python 3.4+ script to make autoloaders.
Downloads, extracts, packs, compresses and verifies
bar files from Blackberry servers.
"""
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
import subprocess  # invocation of 7z, cap
import zlib  # adler32, crc32
import zipfile  # zip extract, zip compresssion
import tarfile  # txz/tbz/tgz compression

_version = "2015-04-14-B"
_release = "https://github.com/thurask/archivist/releases/latest"
_updatesite = """https://raw.githubusercontent.com/thurask/\
thurask.github.io/master/archivist.version"""
_capversion = "3.11.0.18"


def crc32hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return CRC32 checksum of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    seed = 0
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(1024), b''):
            seed = zlib.crc32(chunk, seed)
    final = format(seed & 0xFFFFFFFF, "x")
    return final


def adler32hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return Adler32 checksum of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    asum = 1
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            asum = zlib.adler32(data, asum)
            if asum < 0:
                asum += 2 ** 32
    final = format(asum & 0xFFFFFFFF, "x")
    return final


def sha1hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-1 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    sha1 = hashlib.sha1()
    f = open(filepath, 'rb')
    try:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            sha1.update(data)
    finally:
        f.close()
    return sha1.hexdigest()


def sha224hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-224 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    sha224 = hashlib.sha224()
    f = open(filepath, 'rb')
    try:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            sha224.update(data)
    finally:
        f.close()
    return sha224.hexdigest()


def sha256hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-256 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    sha256 = hashlib.sha256()
    f = open(filepath, 'rb')
    try:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            sha256.update(data)
    finally:
        f.close()
    return sha256.hexdigest()


def sha384hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-384 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    sha384 = hashlib.sha384()
    f = open(filepath, 'rb')
    try:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            sha384.update(data)
    finally:
        f.close()
    return sha384.hexdigest()


def sha512hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return SHA-512 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    sha512 = hashlib.sha512()
    f = open(filepath, 'rb')
    try:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            sha512.update(data)
    finally:
        f.close()
    return sha512.hexdigest()


def md4hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return MD4 hash of a file; depends on system SSL library.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    try:
        md4 = hashlib.new('md4')
        f = open(filepath, 'rb')
        try:
            while True:
                data = f.read(blocksize)
                if not data:
                    break
                md4.update(data)
        finally:
            f.close()
        return md4.hexdigest()
    except Exception:
        print("MD4 HASH FAILED:\nIS IT AVAILABLE?")


def md5hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return MD5 hash of a file.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    md5 = hashlib.md5()
    f = open(filepath, 'rb')
    try:
        while True:
            data = f.read(blocksize)
            if not data:
                break
            md5.update(data)
    finally:
        f.close()
    return md5.hexdigest()


def ripemd160hash(filepath, blocksize=16 * 1024 * 1024):
    """
    Return RIPEMD160 hash of a file; depends on system SSL library.
    :param filepath: File you wish to verify.
    :type filepath: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    """
    try:
        r160 = hashlib.new('ripemd160')
        f = open(filepath, 'rb')
        try:
            while True:
                data = f.read(blocksize)
                if not data:
                    break
                r160.update(data)
        finally:
            f.close()
        return r160.hexdigest()
    except Exception:
        print("RIPEMD160 HASH FAILED:\nIS IT AVAILABLE?")


def verifier(workingdir, blocksize=16 * 1024 * 1024,
             crc32=False, adler32=False,
             sha1=True, sha224=False, sha256=False,
             sha384=False, sha512=False, md5=True, md4=False, ripemd160=False):
    """
    For all files in a directory, perform various hash/checksum functions.
    on them based on boolean arguments, writing the output to a .cksum file.
    :param workingdir: Path you wish to verify.
    :type workingdir: str
    :param blocksize: File read chunk size;
    how much of it to load into memory at a time.
    :type blocksize: int
    :param crc32: Whether to use CRC32. False by default.
    :type crc32: bool
    :param adler32: Whether to use Adler-32. False by default.
    :type adler32: bool
    :param sha1: Whether to use SHA-1. True by default.
    :type sha1: bool
    :param sha224: Whether to use SHA-224. False by default.
    :type sha224: bool
    :param sha256: Whether to use SHA-256. False by default.
    :type sha256: bool
    :param sha384: Whether to use SHA-384. False by default.
    :type sha384: bool
    :param sha512: Whether to use SHA-512. False by default.
    :type sha512: bool
    :param md5: Whether to use MD5. True by default.
    :type md5: bool
    :param md4: Whether to use MD4. False by default. Dependent on
    system OpenSSL implementation (not in stdlib).
    :type md4: bool
    :param ripemd160: Whether to use RIPEMD160. False by default. Dependent on
    system OpenSSL implementation (not in stdlib).
    :type ripemd160: bool
    """
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
    hashoutput_ripemd160 = "RIPEMD160\n"
    for file in os.listdir(workingdir):
        if os.path.isdir(os.path.join(workingdir, file)):
            pass  # exclude folders
        elif file.endswith(".cksum"):
            pass  # exclude already generated files
        else:
            if adler32:
                print("Adler32:", str(file))
                result_adler32 = adler32hash(
                    os.path.join(
                        workingdir,
                        file),
                    blocksize)
                hashoutput_adler32 += str(result_adler32.upper())
                hashoutput_adler32 += " "
                hashoutput_adler32 += str(file)
                hashoutput_adler32 += " \n"
            if crc32:
                print("CRC32:", str(file))
                result_crc32 = crc32hash(
                    os.path.join(
                        workingdir,
                        file),
                    blocksize)
                hashoutput_crc32 += str(result_crc32.upper())
                hashoutput_crc32 += " "
                hashoutput_crc32 += str(file)
                hashoutput_crc32 += " \n"
            if md4:
                print("MD4:", str(file))
                result_md4 = md4hash(
                    os.path.join(
                        workingdir,
                        file),
                    blocksize)
                hashoutput_md4 += str(result_md4.upper())
                hashoutput_md4 += " "
                hashoutput_md4 += str(file)
                hashoutput_md4 += " \n"
            if md5:
                print("MD5:", str(file))
                result_md5 = md5hash(
                    os.path.join(
                        workingdir,
                        file),
                    blocksize)
                hashoutput_md5 += str(result_md5.upper())
                hashoutput_md5 += " "
                hashoutput_md5 += str(file)
                hashoutput_md5 += " \n"
            if sha1:
                print("SHA1:", str(file))
                result_sha1 = sha1hash(
                    os.path.join(
                        workingdir,
                        file),
                    blocksize)
                hashoutput_sha1 += str(result_sha1.upper())
                hashoutput_sha1 += " "
                hashoutput_sha1 += str(file)
                hashoutput_sha1 += " \n"
            if sha224:
                print("SHA224:", str(file))
                result_sha224 = sha224hash(
                    os.path.join(
                        workingdir,
                        file),
                    blocksize)
                hashoutput_sha224 += str(result_sha224.upper())
                hashoutput_sha224 += " "
                hashoutput_sha224 += str(file)
                hashoutput_sha224 += " \n"
            if sha256:
                print("SHA256:", str(file))
                result_sha256 = sha256hash(
                    os.path.join(
                        workingdir,
                        file),
                    blocksize)
                hashoutput_sha256 += str(result_sha256.upper())
                hashoutput_sha256 += " "
                hashoutput_sha256 += str(file)
                hashoutput_sha256 += " \n"
            if sha384:
                print("SHA384:", str(file))
                result_sha384 = sha384hash(
                    os.path.join(
                        workingdir,
                        file),
                    blocksize)
                hashoutput_sha384 += str(result_sha384.upper())
                hashoutput_sha384 += " "
                hashoutput_sha384 += str(file)
                hashoutput_sha384 += " \n"
            if sha512:
                print("SHA512:", str(file))
                result_sha512 = sha512hash(
                    os.path.join(
                        workingdir,
                        file),
                    blocksize)
                hashoutput_sha512 += str(result_sha512.upper())
                hashoutput_sha512 += " "
                hashoutput_sha512 += str(file)
                hashoutput_sha512 += " \n"
            if ripemd160:
                print("RIPEMD160:", str(file))
                result_ripemd160 = ripemd160hash(
                    os.path.join(
                        workingdir,
                        file),
                    blocksize)
                hashoutput_ripemd160 += str(result_ripemd160.upper())
                hashoutput_ripemd160 += " "
                hashoutput_ripemd160 += str(file)
                hashoutput_ripemd160 += " \n"
            print("\n")
    if adler32:
        target.write(hashoutput_adler32 + "\n")
    if crc32:
        target.write(hashoutput_crc32 + "\n")
    if md4:
        target.write(hashoutput_md4 + "\n")
    if md5:
        target.write(hashoutput_md5 + "\n")
    if sha1:
        target.write(hashoutput_sha1 + "\n")
    if sha224:
        target.write(hashoutput_sha224 + "\n")
    if sha256:
        target.write(hashoutput_sha256 + "\n")
    if sha384:
        target.write(hashoutput_sha384 + "\n")
    if sha512:
        target.write(hashoutput_sha512 + "\n")
    if ripemd160:
        target.write(hashoutput_ripemd160 + "\n")
    target.close()


def ghetto_convert(intsize):
    """
    Convert from decimal integer to little endian
    hexadecimal string, padded to 16 characters with zeros.
    :param intsize: Integer you wish to convert.
    :type intsize: integer
    """
    hexsize = format(intsize, '08x')  # '00AABBCC'
    newlist = [hexsize[i:i + 2]
               for i in range(0, len(hexsize), 2)]  # ['00', 'AA','BB','CC']
    while "00" in newlist:
        newlist.remove("00")  # extra padding
    newlist.reverse()
    ghetto_hex = "".join(newlist)  # 'CCBBAA'
    ghetto_hex = ghetto_hex.rjust(16, '0')
    return binascii.unhexlify(bytes(ghetto_hex.upper(), 'ascii'))


def make_offset(cap, firstfile, secondfile="", thirdfile="",
                fourthfile="", fifthfile="", sixthfile="", folder=os.getcwd()):
    """
    Create magic offset file for use in autoloader creation.
    Cap.exe MUST match separator version.
    Defined in _capversion.
    :param cap: Location of cap.exe file.
    :type cap: str
    :param firstfile: First signed file. Required.
    :type firstfile: str
    :param secondfile: Second signed file. Optional.
    :type secondfile: str
    :param thirdfile: Third signed file. Optional.
    :type thirdfile: str
    :param fourthfile: Fourth signed file. Optional.
    :type fourthfile: str
    :param fifthfile: Fifth signed file. Optional.
    :type fifthfile: str
    :param sixthfile: Sixth signed file. Optional.
    :type sixthfile: str
    :param folder: Working folder. Optional.
    :type folder: str
    """
    filecount = 0
    filelist = [
        firstfile,
        secondfile,
        thirdfile,
        fourthfile,
        fifthfile,
        sixthfile]
    for i in filelist:
        if i:
            filecount += 1
    # immutable things
    separator = binascii.unhexlify(
        """6ADF5D144E4B4D4E474F46464D4E532B170A0D1E0C14532B372A2D3E2C34522F3C534F514\
F514F514F534E464D514E4947514E51474F70709CD5C5979CD5C5979CD5C597""")
    password = binascii.unhexlify("0" * 160)
    singlepad = binascii.unhexlify("0" * 2)
    doublepad = binascii.unhexlify("0" * 4)
    signedpad = binascii.unhexlify("0" * 16)
    filepad = binascii.unhexlify(
        bytes(
            str(filecount).rjust(
                2,
                '0'),
            'ascii'))  # between 01 and 06
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

    # start of first file; length of cap + length of offset
    firstoffset = len(separator) + len(password) + 64 + capsize
    firststart = ghetto_convert(firstoffset)
    if (filecount >= 2):
        secondoffset = firstoffset + firstsize  # start of second file
        secondstart = ghetto_convert(secondoffset)
    if (filecount >= 3):
        thirdoffset = secondstart + secondsize  # start of third file
        thirdstart = ghetto_convert(thirdoffset)
    if (filecount >= 4):
        fourthoffset = thirdoffset + thirdsize  # start of fourth file
        fourthstart = ghetto_convert(fourthoffset)
    if (filecount >= 5):
        fifthoffset = fourthstart + fourthsize  # start of fifth file
        fifthstart = ghetto_convert(fifthoffset)
    if (filecount == 6):
        sixthoffset = fifthoffset + fifthsize  # start of sixth file
        sixthstart = ghetto_convert(sixthoffset)

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


def make_autoloader(filename, cap,
                    firstfile, secondfile="", thirdfile="",
                    fourthfile="", fifthfile="", sixthfile="",
                    folder=os.getcwd()):
    """
    Python implementation of cap.exe.
    Writes cap.exe, magic offset, signed files to a .exe file.
    Uses output of make_offset().
    :param filename: Name of autoloader.
    :type filename: str
    :param cap: Location of cap.exe file.
    :type cap: str
    :param firstfile: First signed file. Required.
    :type firstfile: str
    :param secondfile: Second signed file. Optional.
    :type secondfile: str
    :param thirdfile: Third signed file. Optional.
    :type thirdfile: str
    :param fourthfile: Fourth signed file. Optional.
    :type fourthfile: str
    :param fifthfile: Fifth signed file. Optional.
    :type fifthfile: str
    :param sixthfile: Sixth signed file. Optional.
    :type sixthfile: str
    :param folder: Working folder. Optional.
    :type folder: str
    """
    make_offset(
        cap,
        firstfile,
        secondfile,
        thirdfile,
        fourthfile,
        fifthfile,
        sixthfile,
        folder)

    filecount = 0
    filelist = [
        firstfile,
        secondfile,
        thirdfile,
        fourthfile,
        fifthfile,
        sixthfile]
    for i in filelist:
        if i:
            filecount += 1
    try:
        with open(os.path.join(os.path.abspath(folder),
                               filename), "wb") as autoloader:
            try:
                with open(os.path.normpath(cap), "rb") as capfile:
                    print("WRITING CAP VERSION", _capversion + "...")
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


def file_exists(file):
    """
    Check if file exists. Used for parsing file inputs from command line.
    :param file: \\path\\to\\file.ext
    :type file: str
    """
    if not os.path.exists(file):
        raise argparse.ArgumentError("{0} does not exist".format(file))
    return file


def update_check(version):
    """
    Check GitHub for script updates.
    :param version: Local version. Defined in _version.
    :type version: str
    """
    update = False
    updatesite = _updatesite
    print("LOCAL VERSION:", version)
    # silence warnings about no SSL
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # don't use SSL until I figure it out
    get = requests.get(updatesite, verify=False)
    remote = str(get.text).strip()
    print("REMOTE VERSION:", remote)
    if (get.status_code != 404):
        if version != remote:
            update = True
        else:
            update = False
    return update


class Downloader(threading.Thread):

    """
    Downloads files attached to supplied threads from DownloadManager.
    Based on:
    http://pipe-devnull.com/2012/09/13/queued-threaded-http-downloader-in-python.html
    """

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
            print(
                "Downloaded " +
                url +
                " in " +
                str(t_elapsed_proper) +
                " seconds")
            f.close()
        else:
            print("* Thread: " + self.name + " Bad URL: " + url)
            return


class DownloadManager():

    """
    Class that handles queued downloads.
    Based on:
    http://pipe-devnull.com/2012/09/13/queued-threaded-http-downloader-in-python.html
    """

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


def str2bool(v):
    """
    Parse bool from string input.
    :param v: String to check if it means True or False.
    :type v: str
    """
    return str(v).lower() in ("yes", "true", "t", "1", "y")


def is_amd64():
    """
    Returns true if script is running on an AMD64 system
    """
    amd64 = platform.machine().endswith("64")
    return amd64


def is_windows():
    """
    Returns true if script is running on Windows.
    """
    windows = platform.system() == "Windows"
    return windows


def is_mac():
    """
    Returns true if script is running on OSX.
    """
    mac = platform.system() == "Darwin"
    return mac


def is_linux():
    """
    Returns true if script is running on Linux.
    """
    linux = platform.system() == "Linux"
    return linux


def get_seven_zip(talkative=False):
    """
    Return name of 7-Zip executable.
    On POSIX, it MUST be 7za.
    On Windows, it can be installed or supplied with the script.
    win_seven_zip() is used to determine if it's installed.
    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    if is_windows():
        smeg = win_seven_zip(talkative)
        return smeg
    else:
        return "7za"


def win_seven_zip(talkative=False):
    """
    For Windows, checks where 7-Zip is.
    Consults registry first for any installed instances of 7-Zip.
    If it's not there, it falls back onto the supplied executables.
    :param talkative: Whether to output to screen. False by default.
    :type talkative: bool
    """
    if talkative:
        print("CHECKING INSTALLED FILES...")
    try:
        import winreg  # windows registry
        hk7z = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\7-Zip")
        path = winreg.QueryValueEx(hk7z, "Path")
    except Exception as e:
        if talkative:
            print("SOMETHING WENT WRONG")
            print(str(e))
            print("TRYING LOCAL FILES...")
        listdir = os.listdir(os.getcwd())
        filecount = 0
        for i in listdir:
            if i == "7za.exe" or i == "7za64.exe":
                filecount += 1
        if filecount == 2:
            if talkative:
                print("7ZIP USING LOCAL FILES")
            if is_amd64():
                return "7za64.exe"
            else:
                return "7za.exe"
        else:
            if talkative:
                print("NO LOCAL FILES")
            return "error"
    else:
        if talkative:
            print("7ZIP USING INSTALLED FILES")
        return '"' + os.path.join(path[0], "7z.exe") + '"'


def get_core_count():
    """
    Find out how many CPU cores this system has.
    Good for multicore compression.
    """
    cores = str(os.cpu_count())  # thank you Python 3.4
    if os.cpu_count() is None:
        cores = str(1)
    return cores


def prep_seven_zip():
    """
    Check for presence of 7-Zip.
    On POSIX, checks for p7zip.
    On Windows, checks for 7-Zip.
    False if not found, True if found.
    """
    if is_mac():
        path = shutil.which("7za")
        if path is None:
            print("NO 7ZIP")
            print("PLEASE INSTALL p7zip FROM SOURCE/HOMEBREW/MACPORTS")
            return False
        else:
            print("7ZIP FOUND AT", path)
            return True
    elif is_linux():
        path = shutil.which("7za")
        if path is None:
            print("NO 7ZIP")
            print("PLEASE INSTALL p7zip AND ANY RELATED PACKAGES")
            print("CONSULT YOUR PACKAGE MANAGER, OR GOOGLE IT")
            return False
        else:
            print("7ZIP FOUND AT", path)
            return True
    elif is_windows():
        smeg = get_seven_zip(True)
        if smeg == "error":
            return False
        else:
            return True


def extract_bars(filepath):
    """
    Extract .signed files from .bar files.
    Use system zlib.
    :param filepath: \\path\\to\\bar_files
    :type filepath: str
    """
    for file in os.listdir(filepath):
        if file.endswith(".bar"):
            try:
                z = zipfile.ZipFile(file, 'r')
                names = z.namelist()
                for name in names:
                    if str(name).endswith(".signed"):
                        z.extract(name, filepath)
            except Exception:
                print("EXTRACTION FAILURE")
                print("DID IT DOWNLOAD PROPERLY?")
                return


def reset(tarinfo):
    """
    Filter for TAR compression.
    :param tarinfo: TarInfo instance to use.
    From provided TarFile, when used as filter.
    :type tarinfo: TarInfo
    """
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo


def compress(filepath, method="7z", szexe="7za.exe"):
    """
    Compress all autoloader files in a given folder, with a given method.
    :param filepath: Working directory. Required.
    :type filepath: str
    :param method: Compression type.
    Can be:
    - "7z" - 7-Zip, LZMA2
    - "txz" - TAR, LZMA (xz)
    - "tbz" - TAR, BZip2 (bz2)
    - "tgz" - TAR, GZip (gz)
    - "zip" - ZIP, DEFLATE
    Default is "7z".
    :type method: str
    :param szexe: Path to 7z executable, if needed.
    Default is local dir\\7za.exe.
    :type szexe: str
    """
    for file in os.listdir(filepath):
        if file.endswith(".exe") and file.startswith(
                ("Q10", "Z10", "Z30", "Z3", "Passport")):
            filename = os.path.splitext(os.path.basename(file))[0]
            fileloc = os.path.join(filepath, filename)
            print("COMPRESSING: " + filename + ".exe")
            if is_amd64():
                strength = 9  # ultra compression
            else:
                strength = 5  # normal compression
            if method == "7z":
                starttime = time.clock()
                subprocess.call(
                    szexe +
                    " a -mx" +
                    str(strength) +
                    " -m0=lzma2 -mmt" +
                    get_core_count() +
                    " " +
                    fileloc +
                    '.7z' +
                    " " +
                    os.path.join(
                        filepath,
                        file),
                    shell=True)
                endtime = time.clock() - starttime
                endtime_proper = math.ceil(endtime * 100) / 100
                print("COMPLETED IN " + str(endtime_proper) + " SECONDS")
            elif method == "tgz":
                with tarfile.open(fileloc + '.tar.gz',
                                  'w:gz',
                                  compresslevel=strength) as gzfile:
                    starttime = time.clock()
                    gzfile.add(file, filter=reset)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")
            elif method == "txz":
                with tarfile.open(fileloc + '.tar.xz',
                                  'w:xz') as xzfile:
                    starttime = time.clock()
                    xzfile.add(file, filter=reset)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")
            elif method == "tbz":
                with tarfile.open(fileloc + '.tar.bz2',
                                  'w:bz2',
                                  compresslevel=strength) as bzfile:
                    starttime = time.clock()
                    bzfile.add(file, filter=reset)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")
            elif method == "zip":
                with zipfile.ZipFile(fileloc + '.zip',
                                     'w',
                                     zipfile.ZIP_DEFLATED) as zfile:
                    starttime = time.clock()
                    zfile.write(file)
                    endtime = time.clock() - starttime
                    endtime_proper = math.ceil(endtime * 100) / 100
                    print("COMPLETED IN " + str(endtime_proper) + " SECONDS")


def availability(url):
    """
    Check HTTP status code of given URL.
    200 or 301-308 is OK, else is not.
    :param url: URL to check.
    :type url: http://site.to/check/
    """
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


def remove_empty_folders(a_folder):
    """
    Remove empty folders in a given folder using os.walk().
    :param a_folder: Target folder.
    :type a_folder: \\path\\to\\a\path
    """
    for curdir, subdirs, files in os.walk(a_folder):
        while True:
            try:
                if len(subdirs) == 0 and len(files) == 0:
                    os.rmdir(curdir)
            except:
                continue
            break


def generate_loaders(
        osversion, radioversion, radios=True,
        cap="cap.exe", localdir=os.getcwd()):
    """
    Create and properly label autoloaders.
    Leverages Python implementation of cap.exe.
    :param osversion: OS version, 10.x.y.zzzz.
    Autoconverted to 10.x.0y.zzzz if need be.
    :type osversion: str
    :param radioversion: Radio version, 10.x.y.zzzz.
    Autoconverted to 10.x.0y.zzzz if need be.
    :type radioversion: str
    :param radios: Whether to make radios or not. True by default.
    :type radios: bool
    :param cap: Path to cap.exe. Default is local dir\\cap.exe.
    :type cap: str
    :param localdir: Working path. Default is local dir.
    :type localdir: str
    """
    # #OS Images
    # 8960
    try:
        os_8960 = glob.glob(
            os.path.join(
                localdir,
                "*qc8960*_sfi.desktop*.signed"))[0]
    except IndexError:
        print("No 8960 image found")

    # 8x30 (10.3.1 MR+)
    try:
        os_8x30 = glob.glob(
            os.path.join(
                localdir,
                "*qc8x30*desktop*.signed"))[0]
    except IndexError:
        print("No 8x30 image found")

    # 8974
    try:
        os_8974 = glob.glob(
            os.path.join(
                localdir,
                "*qc8974*desktop*.signed"))[0]
    except IndexError:
        print("No 8974 image found")

    # OMAP (incl. 10.3.1)
    try:
        os_ti = glob.glob(os.path.join(localdir, "*winchester*.signed"))[0]
    except IndexError:
        print("No OMAP image found")

    # Radio files
    # STL100-1
    try:
        radio_z10_ti = glob.glob(
            os.path.join(
                localdir,
                "*radio.m5730*.signed"))[0]
    except IndexError:
        print("No OMAP radio found")

    # STL100-X
    try:
        radio_z10_qcm = glob.glob(
            os.path.join(
                localdir,
                "*radio.qc8960.BB*.signed"))[0]
    except IndexError:
        print("No 8960 radio found")

    # STL100-4
    try:
        radio_z10_vzw = glob.glob(
            os.path.join(
                localdir,
                "*radio.qc8960*omadm*.signed"))[0]
    except IndexError:
        print("No Verizon 8960 radio found")

    # Q10/Q5
    try:
        radio_q10 = glob.glob(os.path.join(localdir, "*8960*wtr.*.signed"))[0]
    except IndexError:
        print("No Q10/Q5 radio found")

    # Z30/Classic
    try:
        radio_z30 = glob.glob(os.path.join(localdir, "*8960*wtr5*.signed"))[0]
    except IndexError:
        print("No Z30/Classic radio found")

    # Z3
    try:
        radio_z3 = glob.glob(os.path.join(localdir, "*8930*wtr5*.signed"))[0]
    except IndexError:
        print("No Z3 radio found")

    # Passport
    try:
        radio_8974 = glob.glob(os.path.join(localdir, "*8974*wtr2*.signed"))[0]
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
        make_autoloader(
            filename="Z10_" +
            osversion +
            "_STL100-1.exe",
            cap=cap,
            firstfile=os_ti,
            secondfile=radio_z10_ti,
            folder=localdir)
    except Exception:
        print("Could not create STL100-1 OS/radio loader")
    if radios:
        print("Creating OMAP Z10 radio...")
        try:
            make_autoloader(
                "Z10_" +
                radioversion +
                "_STL100-1.exe",
                cap=cap,
                firstfile=radio_z10_ti,
                folder=localdir)
        except Exception:
            print("Could not create STL100-1 radio loader")

    # STL100-X
    try:
        print("Creating Qualcomm Z10 OS...")
        make_autoloader(
            "Z10_" +
            osversion +
            "_STL100-2-3.exe",
            cap=cap,
            firstfile=os_8960,
            secondfile=radio_z10_qcm,
            folder=localdir)
    except Exception:
        print("Could not create Qualcomm Z10 OS/radio loader")
    if radios:
        print("Creating Qualcomm Z10 radio...")
        try:
            make_autoloader(
                "Z10_" +
                radioversion +
                "_STL100-2-3.exe",
                cap=cap,
                firstfile=radio_z10_qcm,
                folder=localdir)
        except Exception:
            print("Could not create Qualcomm Z10 radio loader")

    # STL100-4
    try:
        print("Creating Verizon Z10 OS...")
        make_autoloader(
            "Z10_" +
            osversion +
            "_STL100-4.exe",
            cap=cap,
            firstfile=os_8960,
            secondfile=radio_z10_vzw,
            folder=localdir)
    except Exception:
        print("Could not create Verizon Z10 OS/radio loader")
    if radios:
        print("Creating Verizon Z10 radio...")
        try:
            make_autoloader(
                "Z10_" +
                radioversion +
                "_STL100-4.exe",
                cap=cap,
                firstfile=radio_z10_vzw,
                folder=localdir)
        except Exception:
            print("Could not create Verizon Z10 radio loader")

    # Q10/Q5
    try:
        print("Creating Q10/Q5 OS...")
        make_autoloader(
            "Q10_" +
            osversion +
            "_SQN100-1-2-3-4-5.exe",
            cap=cap,
            firstfile=os_8960,
            secondfile=radio_q10,
            folder=localdir)
    except Exception:
        print("Could not create Q10/Q5 OS/radio loader")
    if radios:
        print("Creating Q10/Q5 radio...")
        try:
            make_autoloader(
                "Q10_" +
                radioversion +
                "_SQN100-1-2-3-4-5.exe",
                cap=cap,
                firstfile=radio_q10,
                folder=localdir)
        except Exception:
            print("Could not create Q10/Q5 radio loader")

    # Z30/Classic
    try:
        print("Creating Z30/Classic OS...")
        make_autoloader(
            "Z30_" +
            osversion +
            "_STA100-1-2-3-4-5-6.exe",
            cap=cap,
            firstfile=os_8960,
            secondfile=radio_z30,
            folder=localdir)
    except Exception:
        print("Could not create Z30/Classic OS/radio loader")
    if radios:
        print("Creating Z30/Classic radio...")
        try:
            make_autoloader(
                "Z30_" +
                radioversion +
                "_STA100-1-2-3-4-5-6.exe",
                cap=cap,
                firstfile=radio_z30,
                folder=localdir)
        except Exception:
            print("Could not create Z30/Classic radio loader")

    # Z3
    try:
        print("Creating Z3 OS...")
        make_autoloader(
            "Z3_" +
            osversion +
            "_STJ100-1-2.exe",
            cap=cap,
            firstfile=os_8x30,
            secondfile=radio_z3,
            folder=localdir)
    except Exception:
        print("Could not create Z3 OS/radio loader (8x30)")
    if radios:
        print("Creating Z3 radio...")
        try:
            make_autoloader(
                "Z3_" +
                radioversion +
                "_STJ100-1-2.exe",
                cap=cap,
                firstfile=radio_z3,
                folder=localdir)
        except Exception:
            print("Could not create Z3 radio loader")

    # Passport
    try:
        print("Creating Passport OS...")
        make_autoloader(
            "Passport_" +
            osversion +
            "_SQW100-1-2-3.exe",
            cap=cap,
            firstfile=os_8974,
            secondfile=radio_8974,
            folder=localdir)
    except Exception:
        print("Could not create Passport OS/radio loader")
    if radios:
        print("Creating Passport radio...")
        try:
            make_autoloader(
                "Passport_" +
                radioversion +
                "_SQW100-1-2-3.exe",
                cap=cap,
                firstfile=radio_8974,
                folder=localdir)
        except Exception:
            print("Could not create Passport radio loader")


def move_loaders(localdir,
                 loaderdir_os, loaderdir_radio,
                 zipdir_os, zipdir_radio):
    """
    Move autoloaders to zipped and loaders directories in localdir.
    :param localdir: Local directory, containing files you wish to move.
    :type localdir: str
    :param loaderdir_os: Large autoloader .exe destination.
    :type loaderdir_os: str
    :param loaderdir_radio: Small autoloader .exe destination.
    :type loaderdir_radio: str
    :param zipdir_os: Large autoloader archive destination.
    :type zipdir_os: str
    :param zipdir_radio: Small autoloader archive destination.
    :type zipdir_radio: str
    """
    for files in os.listdir(localdir):
        if files.endswith(
                          ".exe"
                          ) and files.startswith(
                          ("Q10", "Z10", "Z30", "Z3", "Passport")):
            print("MOVING: " + files)
            loaderdest_os = os.path.join(loaderdir_os, files)
            loaderdest_radio = os.path.join(loaderdir_radio, files)
            # even the fattest radio is less than 90MB
            if os.path.getsize(os.path.join(localdir, files)) > 90000000:
                try:
                    shutil.move(os.path.join(localdir, files), loaderdir_os)
                except shutil.Error:
                    os.remove(loaderdest_os)
            else:
                try:
                    shutil.move(os.path.join(localdir, files), loaderdir_radio)
                except shutil.Error:
                    os.remove(loaderdest_radio)
        if files.endswith(
            (".7z", ".tar.xz", ".tar.bz2", ".tar.gz", ".zip")
            ) and files.startswith(
                ("Q10", "Z10", "Z30", "Z3", "Passport")):
            print("MOVING: " + files)
            zipdest_os = os.path.join(zipdir_os, files)
            zipdest_radio = os.path.join(zipdir_radio, files)
            # even the fattest radio is less than 90MB
            if os.path.getsize(os.path.join(localdir, files)) > 90000000:
                try:
                    shutil.move(os.path.join(localdir, files), zipdir_os)
                except shutil.Error:
                    os.remove(zipdest_os)
            else:
                try:
                    shutil.move(os.path.join(localdir, files), zipdir_radio)
                except shutil.Error:
                    os.remove(zipdest_radio)


def do_magic(osversion, radioversion, softwareversion,
             localdir, radios=True, compressed=True, deleted=True,
             hashed=True, crc32=False, adler32=False,
             sha1=True, sha224=False, sha256=False,
             sha384=False, sha512=False, md5=True,
             md4=False, ripemd160=False, cappath="cap.exe",
             download=True, extract=True, loaders=True, signed=True,
             compmethod="7z"):
    """
    Actual meat of the program. Tie everything together.
    Some combination of creating, downloading, hashing,
    compressing and moving autoloaders.
    :param osversion: OS version, 10.x.y.zzzz.
    :type osversion: str
    :param radioversion: Radio version, 10.x.y.zzzz.
    Usually OS version + 1.
    :type radioversion: str
    :param softwareversion: Software release, 10.x.y.zzzz.
    :type softwareversion: str
    :param localdir: Working directory. Required.
    :type localdir: str
    :param radios: Whether to create radio autoloaders. True by default.
    :type radios: bool
    :param compressed: Whether to compress files. True by default.
    :type compressed: bool
    :param deleted: Whether to delete uncompressed files. True by default.
    :type deleted: bool
    :param hashed: Whether to hash files. True by default.
    :type hashed: bool
    :param crc32: Whether to use CRC32. False by default.
    :type crc32: bool
    :param adler32: Whether to use Adler-32. False by default.
    :type adler32: bool
    :param sha1: Whether to use SHA-1. True by default.
    :type sha1: bool
    :param sha224: Whether to use SHA-224. False by default.
    :type sha224: bool
    :param sha256: Whether to use SHA-256. False by default.
    :type sha256: bool
    :param sha384: Whether to use SHA-384. False by default.
    :type sha384: bool
    :param sha512: Whether to use SHA-512. False by default.
    :type sha512: bool
    :param md5: Whether to use MD5. True by default.
    :type md5: bool
    :param md4: Whether to use MD4. False by default. Dependent on
    system OpenSSL implementation (not in stdlib).
    :type md4: bool
    :param ripemd160: Whether to use RIPEMD160. False by default. Dependent on
    system OpenSSL implementation (not in stdlib).
    :type ripemd160: bool
    :param cappath: Path to cap.exe. Default is local dir\\cap.exe.
    :type cappath: str
    :param download: Whether to download bar files. True by default.
    :type download: bool
    :param extract: Whether to extract bar files. True by default.
    :type extract: bool
    :param loaders: Whether to create autoloaders. True by default.
    :type loaders: bool
    :param signed: Whether to delete signed files. True by default.
    :type signed: bool
    :param compmethod: Compression method. Default is "7z".
    :type compmethod: str
    """
    starttime = time.clock()
    version = _version  # update as needed
    release = _release

    print("~~~ARCHIVIST VERSION", version + "~~~")
    print("OS VERSION:", osversion)
    print("RADIO VERSION:", radioversion)
    print("SOFTWARE VERSION:", softwareversion)

    print("\nCHECKING FOR UPDATES...")
    update = update_check(version)
    if update:
        print("UPDATE AVAILABLE!")
        invoke = str2bool(input("DOWNLOAD UPDATE? Y/N: "))
        if invoke:
            webbrowser.open(release)
            print("CLOSING...")
            raise SystemExit  # bye
        else:
            pass
    else:
        print("NO UPDATE AVAILABLE")

    if compmethod == "7z":
        print("\nCHECKING PRESENCE OF 7ZIP...")
        psz = prep_seven_zip()
        if psz:
            print("7ZIP OK")
            szexe = get_seven_zip()
        else:
            szexe = ""
            print("7ZIP NOT FOUND")
            cont = str2bool(input("CONTINUE? Y/N "))
            if cont:
                pass
            else:
                print("\nEXITING...")
                raise SystemExit  # bye bye
    else:
        szexe = ""

    # Hash software version
    swhash = hashlib.sha1(softwareversion.encode('utf-8'))
    hashedsoftwareversion = swhash.hexdigest()

    # Root of all urls
    baseurl = "http://cdn.fs.sl.blackberry.com/fs/qnx/production/" + \
        hashedsoftwareversion

    # List of OS urls
    osurls = [baseurl + "/winchester.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8960.factory_sfi.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8960.factory_sfi_hybrid_qc8x30.desktop-" +
              osversion + "-nto+armle-v7+signed.bar",
              baseurl + "/qc8960.factory_sfi_hybrid_qc8974.desktop-" +
              osversion + "-nto+armle-v7+signed.bar"]

    # List of radio urls
    radiourls = [baseurl + "/m5730-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960.omadm-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960.wtr-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8960.wtr5-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8930.wtr5-" + radioversion +
                 "-nto+armle-v7+signed.bar",
                 baseurl + "/qc8974.wtr2-" + radioversion +
                 "-nto+armle-v7+signed.bar"]

    # Add URLs to dict, programmatically
    osdict = {}
    radiodict = {}
    for i in osurls:
        osdict[str(i)] = i
    for i in radiourls:
        radiodict[str(i)] = i

    # Check availability of software release
    print("\nCHECKING SOFTWARE RELEASE AVAILABILITY...")
    av = availability(baseurl)
    if av:
        print("SOFTWARE RELEASE", softwareversion, "EXISTS")
    else:
        print("SOFTWARE RELEASE", softwareversion, "NOT FOUND")
        cont = str2bool(input("CONTINUE? Y/N "))
        if cont:
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
    if download:
        print("\nBEGIN DOWNLOADING...")
        download_manager = DownloadManager(radiodict, localdir, 5)
        download_manager.begin_downloads()
        download_manager.download_dict = osdict
        download_manager.begin_downloads()

    # Extract bar files
    if extract:
        print("\nEXTRACTING...")
        extract_bars(localdir)

    # Move bar files
    print("\nMOVING .bar FILES...")
    for files in os.listdir(localdir):
        if files.endswith(".bar"):
            print("MOVING: " + files)
            bardest_os = os.path.join(bardir_os, files)
            bardest_radio = os.path.join(bardir_radio, files)
            # even the fattest radio is less than 90MB
            if os.path.getsize(os.path.join(localdir, files)) > 90000000:
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
    if loaders:
        print("\nGENERATING LOADERS...\n")
        generate_loaders(osversion, radioversion, radios, cappath, localdir)

    # Remove .signed files
    if signed:
        print("\nREMOVING .signed FILES...")
        for file in os.listdir(localdir):
            if os.path.join(localdir, file).endswith(".signed"):
                print("REMOVING: " + file)
                os.remove(os.path.join(localdir, file))

    # If compression = true, compress
    if compressed:
        print("\nCOMPRESSING...")
        compress(localdir, compmethod, szexe)
    else:
        pass

    # Move zipped/unzipped loaders
    print("\nMOVING...")
    move_loaders(localdir,
                 loaderdir_os, loaderdir_radio,
                 zipdir_os, zipdir_radio)

    # Get hashes (if specified)
    if hashed:
        print("\nHASHING LOADERS...")
        print(
            "ADLER32:",
            adler32,
            "CRC32:",
            crc32,
            "MD4:",
            md4,
            "\nMD5:",
            md5,
            "SHA1:",
            sha1,
            "SHA224:",
            sha224,
            "\nSHA256:",
            sha256,
            "SHA384:",
            sha384,
            "SHA512:",
            sha512,
            "\nRIPEMD160:",
            ripemd160,
            "\n")
        blocksize = 32 * 1024 * 1024
        if compressed:
            verifier(
                zipdir_os,
                blocksize,
                crc32,
                adler32,
                sha1,
                sha224,
                sha256,
                sha384,
                sha512,
                md5,
                md4,
                ripemd160)
            if radios:
                verifier(
                    zipdir_radio,
                    blocksize,
                    crc32,
                    adler32,
                    sha1,
                    sha224,
                    sha256,
                    sha384,
                    sha512,
                    md5,
                    md4,
                    ripemd160)
        if not deleted:
            verifier(
                loaderdir_os,
                blocksize,
                crc32,
                adler32,
                sha1,
                sha224,
                sha256,
                sha384,
                sha512,
                md5,
                md4,
                ripemd160)
            if radios:
                verifier(
                    loaderdir_radio,
                    blocksize,
                    crc32,
                    adler32,
                    sha1,
                    sha224,
                    sha256,
                    sha384,
                    sha512,
                    md5,
                    md4,
                    ripemd160)

    # Remove uncompressed loaders (if specified)
    if deleted:
        print("\nDELETING UNCOMPRESSED LOADERS...")
        shutil.rmtree(loaderdir)

    # Delete empty folders
    print("\nREMOVING EMPTY FOLDERS...")
    remove_empty_folders(localdir)

    print("\nFINISHED!")
    endtime = time.clock() - starttime
    endtime_proper = math.ceil(endtime * 100) / 100
    print("\nCompleted in " + str(endtime_proper) + " seconds\n")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            prog="archivist",
            description="Download bar files, create autoloaders.",
            epilog="http://github.com/thurask/archivist")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " +
            _version)
        parser.add_argument("os", help="OS version, 10.x.y.zzzz")
        parser.add_argument("radio", help="Radio version, 10.x.y.zzzz")
        parser.add_argument("swrelease", help="Software version, 10.x.y.zzzz")
        parser.add_argument(
            "-f",
            "--folder",
            type=file_exists,
            dest="folder",
            help="Working folder",
            default=os.getcwd(),
            metavar="DIR")
        parser.add_argument(
            "-c",
            "--cap",
            type=file_exists,
            dest="cappath",
            help="Path to cap.exe",
            default=os.path.join(
                os.getcwd(),
                "cap.exe"),
            metavar="PATH")
        negategroup = parser.add_argument_group(
            "negators",
            "Disable program functionality")
        negategroup.add_argument(
            "-no",
            "--no-download",
            dest="download",
            help="Don't download files",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nx",
            "--no-extract",
            dest="extract",
            help="Don't extract bar files",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nl",
            "--no-loaders",
            dest="loaders",
            help="Don't create autoloaders",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nr",
            "--no-radios",
            dest="radloaders",
            help="Don't make radio autoloaders",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-ns",
            "--no-rmsigned",
            dest="signed",
            help="Don't remove signed files",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nc",
            "--no-compress",
            dest="compress",
            help="Don't compress loaders",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nd",
            "--no-delete",
            dest="delete",
            help="Don't delete uncompressed loaders",
            action="store_false",
            default=True)
        negategroup.add_argument(
            "-nv",
            "--no-verify",
            dest="verify",
            help="Don't verify created loaders",
            action="store_false",
            default=True)
        hashgroup = parser.add_argument_group(
            "verifiers",
            "Verification methods")
        hashgroup.add_argument(
            "--crc32",
            dest="crc32",
            help="Enable CRC32 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--adler32",
            dest="adler32",
            help="Enable Adler-32 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--md4",
            dest="md4",
            help="Enable MD4 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--sha224",
            dest="sha224",
            help="Enable SHA-224 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--sha384",
            dest="sha384",
            help="Enable SHA-384 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--sha512",
            dest="sha512",
            help="Enable SHA-512 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--ripemd160",
            dest="ripemd160",
            help="Enable RIPEMD-160 verification",
            action="store_true",
            default=False)
        hashgroup.add_argument(
            "--no-sha1",
            dest="sha1",
            help="Disable SHA-1 verification",
            action="store_false",
            default=True)
        hashgroup.add_argument(
            "--no-sha256",
            dest="sha256",
            help="Disable SHA-256 verification",
            action="store_false",
            default=True)
        hashgroup.add_argument(
            "--no-md5",
            dest="md5",
            help="Disable MD5 verification",
            action="store_false",
            default=True)
        comps = parser.add_argument_group("compressors", "Compression methods")
        compgroup = comps.add_mutually_exclusive_group()
        compgroup.add_argument(
            "--7z",
            dest="compmethod",
            help="Compress with 7z, LZMA2",
            action="store_const",
            const="7z")
        compgroup.add_argument(
            "--tgz",
            dest="compmethod",
            help="Compress with tar, GZIP",
            action="store_const",
            const="tgz")
        compgroup.add_argument(
            "--tbz",
            dest="compmethod",
            help="Compress with tar, BZIP2",
            action="store_const",
            const="tbz")
        compgroup.add_argument(
            "--txz",
            dest="compmethod",
            help="Compress with tar, LZMA",
            action="store_const",
            const="txz")
        compgroup.add_argument(
            "--zip",
            dest="compmethod",
            help="Compress with zip, DEFLATE",
            action="store_const",
            const="zip")
        parser.set_defaults(compmethod="7z")
        args = parser.parse_args(sys.argv[1:])
        do_magic(args.os, args.radio, args.swrelease,
                 args.folder, args.radloaders,
                 args.compress, args.delete, args.verify,
                 args.crc32, args.adler32, args.sha1, args.sha224, args.sha256,
                 args.sha384, args.sha512, args.md5, args.md4, args.ripemd160,
                 args.cappath, args.download, args.extract, args.loaders,
                 args.signed, args.compmethod)
    else:
        localdir = os.getcwd()
        osversion = input("OS VERSION: ")
        radioversion = input("RADIO VERSION: ")
        softwareversion = input("SOFTWARE RELEASE: ")
        radios = str2bool(input("CREATE RADIO LOADERS? Y/N: "))
        compressed = str2bool(input("COMPRESS LOADERS? Y/N: "))
        if compressed:
            deleted = str2bool(input("DELETE UNCOMPRESSED? Y/N: "))
        else:
            deleted = False
        hashed = str2bool(input("GENERATE HASHES? Y/N: "))
        print(" ")
        do_magic(osversion, radioversion, softwareversion,
                 localdir, radios, compressed, deleted, hashed,
                 False, False, True, False, False,
                 False, False, True, False, False,
                 "cap.exe", True, True, True, True, "7z")
    smeg = input("Press Enter to exit")
