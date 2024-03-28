IFD = list()
dirEntry = []

with open("monke.tiff", "rb") as f:
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
            tmpList.append(
                {
                    "tag": int.from_bytes(ifd_data[j:j + 2], endian),
                    "type": int.from_bytes(ifd_data[j + 2:j + 4], endian),
                    "count": int.from_bytes(ifd_data[j + 4:j + 8], endian),
                    "valueOffset": int.from_bytes(ifd_data[j + 8:j + 12], endian)
                }
            )
        dirEntry.append(tmpList)

print("Number of IFD:", len(IFD))
for elem in IFD:
    print(elem)

for elem in dirEntry:
    for xd in elem:
        print(xd)
