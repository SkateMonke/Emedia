import sys
from io import BytesIO
from PIL import Image


def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


IFD = list()
dirEntry = []
fileToWrite = None

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
    "Compression": 259,
    "PhotometricInterpretation": 262,
    "StripOffsets": 273,
    "RowsPerStrip": 278,
    "StripByteCount": 279,
    "XResolution": 282,
    "YResolution": 283,
    "ResolutionUnit": 296
}

with open("at3_1m4_01.tif", "rb") as f:
    header = f.read(8)
    print(f"Header: {header}")
    fileToWrite = header

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

        fileToWrite += num_entries.to_bytes(2, byteorder=endian)

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
                value = int.from_bytes(ifd_data[j + 8:j + 12], endian)
            elif count_tmp <= 4 and tmp_val <= 4:
                value = (split_list(ifd_data[j + 8:j + 12], 4//count_tmp))
                for h in range(0, len(value)):
                    value[h] = int.from_bytes(value[h], endian)

            tmpList.append(
                {
                    "tag": int.from_bytes(ifd_data[j:j + 2], endian),
                    "type": type_tmp,
                    "count": count_tmp,
                    "value": value
                }
            )

            if tmp_val > 4:
                f.seek(tmpList[-1]["value"])

                tmp_val_list = list()
                for _ in range(count_tmp):
                    tmp_val_list.append(int.from_bytes(f.read(type_dict[str(type_tmp)]), endian))

                tmpList[-1]["value"] = tmp_val_list
                tmpList[-1]["offset"] = int.from_bytes(ifd_data[j + 8:j + 12], endian)

        dirEntry = tmpList

print("Number of IFD:", len(IFD))
print(IFD)

print("\nTags:")
for entry in dirEntry:
    print(entry)

with open("output.tif", 'wb') as output_file:
    print("\nOutput file: ", fileToWrite)
    output_file.write(fileToWrite)

# .to_bytes(<ilosc_bitów>, endian=)
