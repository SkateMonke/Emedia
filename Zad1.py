IFD = list()
dirEntry = []


def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

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
    "FreeByteCounts":  289,
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

requiered_baseline = {
    "ImageWidth": 256,
    "ImageLength": 257,
    "BitsPerSample": 258,
    "Compression": 259,
    "PhotometricInterpretation": 262,
    "StripOffsets": 273,
    "RowsPerStrip": 278,
    "StripByteCount": 279,
    "XResolution": 282,
    "YResolution": 283,
    "ResolutionUnit": 296
}
try:
    with open("at3_1m4_01.tif", "rb") as f:
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
                    valueOffset_tmp = (split_list(ifd_data[j + 8:j + 12], 4//count_tmp))
                    for h in range(0, len(valueOffset_tmp)):
                        valueOffset_tmp[h] = int.from_bytes(valueOffset_tmp[h], endian)

                tmpList.append(
                    {
                        "tag": int.from_bytes(ifd_data[j:j + 2], endian),
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
except Exception as e:
    print(e)

print("Number of IFD:", len(IFD))
for elem in IFD:
    print(elem)

i = 0
print("\nRequiered baseline:")
for elem in dirEntry:
    if(elem["tag"] in requiered_baseline.values()):
        i += 1
        print(elem)

print("No req tags:", i)

i = 0
print("\nBaseline:")
for elem in dirEntry:
    if (elem["tag"] not in requiered_baseline.values()):
        i += 1
        print(elem)

print("No non req tags:", i, "\n")

with open("at3_1m4_01.tif", "rb") as f_in:
    with open("output.tif", "wb") as f_out:
        plik = f_in.read()
        header = plik[:8]
        if header[:2] == b'II':
            endian = "little"
        else:
            endian = "big"

        offset = int.from_bytes(header[4:], endian)
        A = offset
        B = int.from_bytes(plik[A:A+2], endian)

        offset += 2

        while offset < (A + 2 + (B * 12)):
            tag = int.from_bytes(plik[offset: offset + 2], endian)

            if tag in requiered_baseline.values():
                offset += 12
            else:
                # type
                plik = plik[:offset + 2] + (1).to_bytes(2, endian) + plik[offset + 4:]
                # count
                plik = plik[:offset + 4] + (1).to_bytes(4, endian) + plik[offset + 8:]
                # value
                plik = plik[:offset + 8] + (0).to_bytes(4, endian) + plik[offset + 12:]

                tmp = plik[offset:offset + 12]

                offset += 12
        f_out.write(plik)
