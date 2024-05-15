#TODO
#szyfrowanie bloakmi działa dopóki bloki są maksymalnie rozmiaru 4
#Napraw to debilul

import sympy
from math import gcd as bltin_gcd
from random import randrange
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def FindCoPrime(a, b):
    while True:
        if bltin_gcd(a, b) == 1:
            return b
        else:
            b -= 1

def AreCoPrime(a, b):
    return bltin_gcd(a, b) == 1


p = sympy.randprime(2 ** 10, 2 ** 20)
q = sympy.randprime(2 ** 10, 2 ** 20)
n = p * q

print("P: " + str(p))
print("Q: " + str(q))
print("N: " + str(n))

e = FindCoPrime((p-1)*(q-1), randrange(int(n/2), n - 1))
print("E: " + str(e))

phi_n = (p - 1) * (q - 1)
d = pow(e, -1, phi_n)
print("D: " + str(d))
#
# public_key = (e, n)
# private_key = (d, n)
# plain_text = "Gongaga"
# plain_int = [ord(x) for x in plain_text]
# plain_bytes = [x.to_bytes(1, 'little') for x in plain_int]
#
# cipher_int = [pow(x, e, n) for x in plain_int]
# cipher_bytes = [x.to_bytes(5, 'little') for x in cipher_int]
#
# decipher_int = [pow(x, d, n) for x in cipher_int]
#
# print(plain_int)
# print(plain_bytes)
# print(cipher_int)
# print(cipher_bytes)
# print(decipher_int)


root = Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)

print("Phi: " + str((e*d) % phi_n))

filename = askopenfilename(parent=root)

#rozmiar bloku do zaszyfrowanaia podawany w bajtach
block_size = 5

#inp = input('Zaszyfrowac plik" [enter to skip]: ')
inp = "dsafagag123$"
if inp:
    with open(filename, "rb") as f_in:
        with open("./img/RSA_ECB.tif", "wb") as f_out:
            plik = f_in.read()
            header = plik[:8]
            if header[:2] == b'II':
                endian = "little"
            else:
                endian = "big"
            f_out.write(header)
            i = 8
            while i < len(plik):
                # plain_int = int.from_bytes(plik[i], endian)
                if block_size == 1:
                    plain_int = plik[i]
                else:
                    if i + (1 * block_size) > len(plik):
                        plain_int = int.from_bytes(plik[i: len(plik)], endian)
                    else:
                        plain_int = int.from_bytes(plik[i: i + block_size], endian)
                cipher_int = pow(plain_int, e, n)
                cipher_byte = cipher_int.to_bytes(5 * block_size, endian)
                f_out.write(cipher_byte)
                i += (1 * block_size)

with open("./img/RSA_ECB.tif", "rb") as f_in:
    with open("./img/RSA_ECB_decypher.tif", "wb") as f_out:
        plik = f_in.read()
        header = plik[:8]
        if header[:2] == b'II':
            endian = "little"
        else:
            endian = "big"
        f_out.write(header)
        i = 8
        while i < len(plik):
            if i + (5 * block_size) < len(plik):
                zaszyfrowane_bajty = plik[i: i + (5 * block_size)]
                zaszyfrowana_liczba = int.from_bytes(zaszyfrowane_bajty, endian)
                odszyfrowana_liczba = pow(zaszyfrowana_liczba, d, n)
                odszyfrowane_bajty = int(odszyfrowana_liczba).to_bytes(1 * block_size, endian)
            else:
                zaszyfrowane_bajty = plik[i: len(plik)]
                zaszyfrowana_liczba = int.from_bytes(zaszyfrowane_bajty, endian)
                odszyfrowana_liczba = pow(zaszyfrowana_liczba, d, n)
                odszyfrowane_bajty = int(odszyfrowana_liczba).to_bytes(int((len(plik) - i - 1)/5), endian)

            print("Zaszyfrowane bajty: " + str(zaszyfrowane_bajty))
            print("Zaszyfrowana liczba: " + str(zaszyfrowana_liczba))
            print("Odszyfrowana liczba: " + str(odszyfrowana_liczba))
            print("Odszyfrowane bajty: " + str(odszyfrowane_bajty))
            print("I: " + str(i))

            f_out.write(odszyfrowane_bajty)
            i += (5 * block_size)

