IFD = list()

with open("monke.tiff", "rb") as f:
    header = f.read(8)

    if header[:2] == b'II':
        endian = "little"
    else:
        endian = "big"

    offset_0 = int.from_bytes(header[4:], endian)
    i = offset_0

    while i != 0:
        f.seek(i)
        num_entries = int.from_bytes(f.read(2), endian)
        ifd_size = (num_entries * 12) + 6
        ifd_data = f.read(ifd_size)

        next_ifd_offset = int.from_bytes(f.read(4), endian)

        IFD.append(ifd_data)

        i = next_ifd_offset

IFD = IFD[:-1]

print("Number of IFD:", len(IFD))
for elem in IFD:
    print(elem)

# header = bajty[:8]
#
# # wykrywanie w jaki sposob bajty sa zapisywane
# if header[0] == b'I' and header[1] == b'I':
#     endian = "little"
# else:
#     endian = "big"
#
# sekcje = list()
# sekcje.append(header)
#
# offset_0 = int.from_bytes(header[4] + header[5] + header[6] + header[7], endian)
# i = offset_0
#
# while i != 0:
#     liczba_sekcji_b = b'0'
#
#     for j in range(i, i + 2):  # zczytywanie ile sekcji idf jest w kolejnych bajtach
#         liczba_sekcji_b += bajty[j]
#     liczba_sekcji = int.from_bytes(liczba_sekcji_b, endian)
#
#     k = 0
#     for j in range(i, 6 + (liczba_sekcji * 12)):  # zczytywanie sekcji idf do nastepnego offsetu
#         sekcja = []
#         for h in range(j + k + 2, j + k + 12 + 2):  # zczytywanie pojedynczej sekcji
#             sekcja.append(bajty[h])
#         sekcje.append(sekcja)
#         print(h, sekcja)
#         k += 11
#
#     offset = int.from_bytes(bajty[i + 2 + (liczba_sekcji * 12)] + bajty[i + 3 + (liczba_sekcji * 12)], endian)
#     i += i + 2 + (liczba_sekcji * 12) + offset
#
# for i in range(1, 10):
#     print(sekcje[i])
#
# print(offset_0)
# print(int.from_bytes(sekcje[1][2] + sekcje[1][3], endian))
