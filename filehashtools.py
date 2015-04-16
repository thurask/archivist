import zlib
import hashlib
import os


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
