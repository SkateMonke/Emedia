from PIL import Image
from PIL.TiffTags import TAGS


# with Image.open("monke.tiff") as img:
#     meta_dict = {TAGS[key] : img.tag[key] for key in img.tag_v2}
#
# print(meta_dict)

bajty = []
i = 0

with open("monke.tiff", "rb") as f:
    while(byte := f.read(1)):
        i += 1
        bajty.append(byte)

header = bajty[:8]
#wykrywanie w jaki sposob bajty sa zapisywane
if header[0] == b'I' and header[1] == b'I':
    endian = "little"
else:
    endian = "big"

sekcje = []
sekcje.append(header)

offset_0 = int.from_bytes(header[4] + header[5] + header[6] + header[7], endian)
i = offset_0

while i < len(bajty):
    liczba_sekcji_b = b'0'
    for j in range(i, i + 2):                                    #zczytywanie ile sekcji idf jest w kolejnych bajtach
        liczba_sekcji_b += bajty[j]
    liczba_sekcji = int.from_bytes(liczba_sekcji_b, endian)
    k = 0
    for j in range(i, i+2+(liczba_sekcji*12)):                   #zczytywanie sekcji idf do nastepnego offsetu
        sekcja = []
        for h in range(j + k + 2, j + k + 12 + 2):                       #zczytywanie pojedynczej sekcji
            sekcja.append(bajty[h])
        sekcje.append(sekcja)
        print(h, sekcja)
        k += 11
    offset = int.from_bytes(bajty[i+2+(liczba_sekcji*12)] + bajty[i+3+(liczba_sekcji*12)], endian)
    i += i+2+(liczba_sekcji*12) + offset

for i in range(1, 10):
    print(sekcje[i])
# sekcja = []
# for j in bajty:
#     if i == 18:
#         sekcje.append(sekcja)
#         i = 0
#         sekcja = []
#     sekcja.append(j)
#     i += 1
#
# for i in sekcje:
#     print(i)
print(offset_0)
print(int.from_bytes(sekcje[1][2] + sekcje[1][3], endian))
