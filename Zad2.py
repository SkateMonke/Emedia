import sympy
from math import gcd as bltin_gcd
from random import randrange, randint
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import shutil
import rsa
import tifffile as tiff
import numpy as np

baseline_tags = {
    "NewSubfileType": 254,
    "SubfileType": 255,
    "ImageWidth": 256,
    "ImageLength": 257,
    "BitsPerSample": 258,
    "Compression": 259,
    "PhotometricInterpretation": 262,
    "Threshholding": 263,
    "CellWidth": 264,
    "CellLength": 265,
    "FillOrder": 266,
    "ImageDescription": 270,
    "Make": 271,
    "Model": 272,
    "StripOffsets": 273,
    "Orientation": 274,
    "SamplesPerPixel": 277,
    "RowsPerStrip": 278,
    "StripByteCount": 279,
    "MinSampleValue": 280,
    "MaxSampleValue": 281,
    "XResolution": 282,
    "YResolution": 283,
    "PlanarConfiguration": 284,
    "FreeOffsets": 288,
    "FreeByteCounts": 289,
    "GrayResponseUnit": 290,
    "GrayResponseCurve": 291,
    "ResolutionUnit": 296,
    "Software": 305,
    "DateTime": 306,
    "Artist": 315,
    "HostComputer": 316,
    "ColorMap": 320,
    "ExtraSamples": 338,
    "Copyright": 33432
}
baseline_tags = {v: k for k, v in baseline_tags.items()}

type_dict = {
    "1": 1,
    "2": 1,
    "3": 2,
    "4": 4,
    "5": 8,
    "6": 1,
    "7": 1,
    "8": 2,
    "9": 4,
    "10": 8,
    "11": 4,
    "12": 8
}

stripoffsets = None
stripcount = None
def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def FindCoPrime(a, b):
    while True:
        if bltin_gcd(a, b) == 1:
            return b
        else:
            b -= 1


def AreCoPrime(a, b):
    return bltin_gcd(a, b) == 1


def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def rsa_ecb_tiff(p, q, e, block_size):
    global stripoffsets
    global stripcount
    global fileend
    n = p * q
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    filename = askopenfilename(parent=root)
    shutil.copy(filename, './img/RSAecb_tif.tif')
    IFD = list()
    dirEntry = []
    with open('./img/RSAecb_tif.tif', 'rb') as f:
        header = f.read(8)
        if header[:2] == b'II':
            endian = "little"
        else:
            endian = "big"

        offset_0 = int.from_bytes(header[4:], endian)
        i = offset_0
        ifd_size = None

        while i != 0:
            f.seek(i)
            num_entries = int.from_bytes(f.read(2), endian)

            if not num_entries:
                break

            ifd_size = (num_entries * 12) + 6
            ifd_data = f.read(ifd_size)
            next_ifd_offset = int.from_bytes(f.read(4), endian)

            IFD.append(ifd_data)

            i = next_ifd_offset

            tmpList = list()
            for j in range(0, ifd_size - 6, 12):
                type_tmp = int.from_bytes(ifd_data[j + 2:j + 4], endian)
                count_tmp = int.from_bytes(ifd_data[j + 4:j + 8], endian)
                tmp_val = count_tmp * type_dict[str(type_tmp)]

                if count_tmp == 1 or tmp_val > 4:
                    valueOffset_tmp = int.from_bytes(ifd_data[j + 8:j + 12], endian)
                elif count_tmp <= 4 and tmp_val <= 4:
                    valueOffset_tmp = (split_list(ifd_data[j + 8:j + 12], 4 // count_tmp))
                    for h in range(0, len(valueOffset_tmp)):
                        valueOffset_tmp[h] = int.from_bytes(valueOffset_tmp[h], endian)

                tmpList.append(
                    {
                        "tag": baseline_tags[int.from_bytes(ifd_data[j:j + 2], endian)],
                        "type": type_tmp,
                        "count": count_tmp,
                        "values": valueOffset_tmp
                    }
                )

                if tmp_val > 4:
                    tmpList[-1]["offset"] = tmpList[-1]["values"]
                    f.seek(tmpList[-1]["values"])

                    tmp_val_list = list()
                    for _ in range(count_tmp):
                        tmp_val_list.append(int.from_bytes(f.read(type_dict[str(type_tmp)]), endian))

                    tmpList[-1]["values"] = tmp_val_list

            dirEntry = tmpList

    for i in dirEntry:
        if i["tag"] == "StripOffsets":
            stripoffsets = i["values"]
        if i["tag"] == "StripByteCount":
            stripcount = i["values"]

    with open('./img/RSAecb_tif.tif', 'rb+') as f_out:
        plik = f_out.read()
        fileend = len(plik)
        fileend_tmp = fileend
        ktory_offset = 0
        for offsets in stripoffsets:
            tmp = 0
            while tmp + block_size < stripcount[ktory_offset]:
                if tmp + block_size < stripcount[ktory_offset]:
                    plain_bytes = plik[offsets + tmp: offsets + tmp + block_size]
                    plain_int = int.from_bytes(plain_bytes, endian)
                    cipher_int = pow(plain_int, e, n)
                    cipher_byte = cipher_int.to_bytes(block_size + 1, endian)
                    f_out.seek(offsets + tmp)
                    f_out.write(cipher_byte[:-1])
                    f_out.seek(fileend_tmp)
                    f_out.write(cipher_byte[-1].to_bytes(1, endian))
                    tmp += block_size
                    fileend_tmp += 1
                else:
                    tmp += block_size
            ktory_offset += 1


def ecb_decipher(p, q, e, block_size, fileend):
    n = p * q
    phi_n = (p - 1) * (q - 1)
    d = pow(e, -1, phi_n)
    shutil.copy('./img/RSAecb_tif.tif', './img/RSAecb_tif_decrypted.tif')
    with open('./img/RSAecb_tif_decrypted.tif', 'rb+') as f_out:
        plik = f_out.read()
        header = plik[:8]
        if header[:2] == b'II':
            endian = "little"
        else:
            endian = "big"
        ktory_offset = 0
        for offsets in stripoffsets:
            tmp = 0
            while tmp + block_size < stripcount[ktory_offset]:
                if tmp + block_size < stripcount[ktory_offset]:
                    byte_tmp = plik[fileend: fileend + 1]
                    # byte_tmp = int_tmp.to_bytes(5 - block_size, endian)
                    cipher_bytes = plik[offsets + tmp: offsets + tmp + block_size] + byte_tmp
                    cipher_int = int.from_bytes(cipher_bytes, endian)
                    plain_int = pow(cipher_int, d, n)
                    plain_bytes = plain_int.to_bytes(block_size, endian)
                    f_out.seek(offsets + tmp)
                    f_out.write(plain_bytes)
                    tmp += block_size
                    fileend += 1
                else:
                    tmp += block_size
            ktory_offset += 1

def cfb_cypher(p, q, e, block_size, iv):
    global stripoffsets
    global stripcount
    n = p * q
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    filename = askopenfilename(parent=root)
    shutil.copy(filename, './img/RSAcfb_tif.tif')
    IFD = list()
    dirEntry = []
    with open('./img/RSAcfb_tif.tif', 'rb') as f:
        header = f.read(8)
        if header[:2] == b'II':
            endian = "little"
        else:
            endian = "big"

        offset_0 = int.from_bytes(header[4:], endian)
        i = offset_0
        ifd_size = None

        while i != 0:
            f.seek(i)
            num_entries = int.from_bytes(f.read(2), endian)

            if not num_entries:
                break

            ifd_size = (num_entries * 12) + 6
            ifd_data = f.read(ifd_size)
            next_ifd_offset = int.from_bytes(f.read(4), endian)

            IFD.append(ifd_data)

            i = next_ifd_offset

            tmpList = list()
            for j in range(0, ifd_size - 6, 12):
                type_tmp = int.from_bytes(ifd_data[j + 2:j + 4], endian)
                count_tmp = int.from_bytes(ifd_data[j + 4:j + 8], endian)
                tmp_val = count_tmp * type_dict[str(type_tmp)]

                if count_tmp == 1 or tmp_val > 4:
                    valueOffset_tmp = int.from_bytes(ifd_data[j + 8:j + 12], endian)
                elif count_tmp <= 4 and tmp_val <= 4:
                    valueOffset_tmp = (split_list(ifd_data[j + 8:j + 12], 4 // count_tmp))
                    for h in range(0, len(valueOffset_tmp)):
                        valueOffset_tmp[h] = int.from_bytes(valueOffset_tmp[h], endian)

                tmpList.append(
                    {
                        "tag": baseline_tags[int.from_bytes(ifd_data[j:j + 2], endian)],
                        "type": type_tmp,
                        "count": count_tmp,
                        "values": valueOffset_tmp
                    }
                )

                if tmp_val > 4:
                    tmpList[-1]["offset"] = tmpList[-1]["values"]
                    f.seek(tmpList[-1]["values"])

                    tmp_val_list = list()
                    for _ in range(count_tmp):
                        tmp_val_list.append(int.from_bytes(f.read(type_dict[str(type_tmp)]), endian))

                    tmpList[-1]["values"] = tmp_val_list

            dirEntry = tmpList

    for i in dirEntry:
        if i["tag"] == "StripOffsets":
            stripoffsets = i["values"]
        if i["tag"] == "StripByteCount":
            stripcount = i["values"]

    with open('./img/RSAcfb_tif.tif', 'rb+') as f_out:
        plik = f_out.read()
        tmp = 0
        tmp_cipher = pow(iv, e, n)
        tmp_cipher = tmp_cipher.to_bytes(block_size, endian)
        plain_bytes = plik[stripoffsets[0]: stripoffsets[0] + block_size]
        cipher_bytes = bytes(a ^ b for (a, b) in zip(plain_bytes, tmp_cipher))
        f_out.seek(stripoffsets[0])
        f_out.write(cipher_bytes)
        tmp += block_size
        while tmp + block_size < stripcount[0]:
            plain_bytes = plik[stripoffsets[0] + tmp: stripoffsets[0] + tmp + block_size]
            cipher_int = int.from_bytes(cipher_bytes, endian)
            tmp_cipher = pow(cipher_int, e, n)
            tmp_cipher = tmp_cipher.to_bytes(block_size, endian)
            cipher_bytes = bytes(a ^ b for (a, b) in zip(plain_bytes, tmp_cipher))
            f_out.seek(stripoffsets[0] + tmp)
            f_out.write(cipher_bytes)
            tmp += block_size
        ktory_offset = 1
        for offsets in stripoffsets[1:]:
            tmp = 0
            while tmp + block_size < stripcount[ktory_offset]:
                plain_bytes = plik[offsets + tmp: offsets + tmp + block_size]
                cipher_int = int.from_bytes(cipher_bytes, endian)
                tmp_cipher = pow(cipher_int, e, n)
                tmp_cipher = tmp_cipher.to_bytes(block_size, endian)
                cipher_bytes = bytes(a ^ b for (a, b) in zip(plain_bytes, tmp_cipher))
                f_out.seek(offsets + tmp)
                f_out.write(cipher_bytes)
                tmp += block_size
            ktory_offset += 1

def cfb_decipher(p, q, e, block_size, iv):
    n = p * q
    phi_n = (p - 1) * (q - 1)
    d = pow(e, -1, phi_n)
    shutil.copy('./img/RSAcfb_tif.tif', './img/RSAcfb_tif_decrypted.tif')
    with open('./img/RSAcfb_tif_decrypted.tif', 'rb+') as f_out:
        plik = f_out.read()
        header = plik[:8]
        if header[:2] == b'II':
            endian = "little"
        else:
            endian = "big"
        tmp = 0
        tmp_cipher = pow(iv, e, n)
        tmp_cipher = tmp_cipher.to_bytes(block_size, endian)
        cipher_bytes = plik[stripoffsets[0]: stripoffsets[0] + block_size]
        plain_bytes = bytes(a ^ b for (a, b) in zip(cipher_bytes, tmp_cipher))
        f_out.seek(stripoffsets[0])
        f_out.write(plain_bytes)
        tmp += block_size
        while tmp + block_size < stripcount[0]:
            tmp_cipher = int.from_bytes(cipher_bytes, endian)
            tmp_cipher = pow(tmp_cipher, e, n)
            tmp_cipher = tmp_cipher.to_bytes(block_size, endian)
            cipher_bytes = plik[stripoffsets[0] + tmp: stripoffsets[0] + tmp + block_size]
            plain_bytes = bytes(a ^ b for (a, b) in zip(cipher_bytes, tmp_cipher))
            f_out.seek(stripoffsets[0] + tmp)
            f_out.write(plain_bytes)
            tmp += block_size
        ktory_offset = 1
        for offsets in stripoffsets[1:]:
            tmp = 0
            while block_size + tmp < stripcount[ktory_offset]:
                tmp_cipher = int.from_bytes(cipher_bytes, endian)
                tmp_cipher = pow(tmp_cipher, e, n)
                tmp_cipher = tmp_cipher.to_bytes(block_size, endian)
                cipher_bytes = plik[offsets + tmp: offsets + tmp + block_size]
                plain_bytes = bytes(a ^ b for (a, b) in zip(cipher_bytes, tmp_cipher))
                f_out.seek(offsets + tmp)
                f_out.write(plain_bytes)
                tmp += block_size
            ktory_offset += 1


def rsa_library(public, block_size):
    n, e = public.n, public.e
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    filename = askopenfilename(parent=root)
    shutil.copy(filename, './img/RSA_library.tif')
    tif = tiff.TiffFile('./img/RSA_library.tif')
    page = tif.pages[0]
    im_arr = page.asarray()
    col, row, _ = im_arr.shape
    for i in range(col):
        for j in range(row):
            for k in range(3):
                tmp = im_arr[i][j][k]
                tmp = int(tmp)
                tmp = tmp.to_bytes(1, 'little')
                tmp_cipher = rsa.encrypt(tmp, public)
                tmp_cipher = int.from_bytes(tmp_cipher, 'little')
                im_arr[i][j][k] = tmp_cipher % 255
    tiff.imwrite('./img/RSA_library.tif', im_arr)


p = sympy.randprime(2 ** 10, 2 ** 20)
q = sympy.randprime(2 ** 10, 2 ** 20)
n = p * q
e = FindCoPrime((p - 1) * (q - 1), randrange(int(n / 2), n - 1))
phi_n = (p - 1) * (q - 1)
d = pow(e, -1, phi_n)
ecb_block_size = 4
cfb_block_size = 5
iv = random_with_N_digits(cfb_block_size)
public_key, private_key = rsa.newkeys(128)



# rsa_ecb_tiff(p, q, e, ecb_block_size)
# ecb_decipher(p, q, e, ecb_block_size, fileend)
# cfb_cypher(p, q, e, cfb_block_size, iv)
# cfb_decipher(p, q, e, cfb_block_size, iv)
rsa_library(public_key, ecb_block_size)
