from tkinter import Tk
from tkinter.filedialog import askopenfilename


def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


IFD = list()
dirEntry = []
geoKeys = []

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
    "12": 8,
    "848": 1
}

geokeys_dict = {
    1024: "GTModelTypeGeoKey",
    1025: "GTRasterTypeGeoKey",
    1026: "GTCitationGeoKey",
    2048: "GeographicTypeGeoKey",
    2049: "GeogCitationGeoKey",
    2050: "GeogGeodeticDatumGeoKey",
    2051: "GeogPrimeMeridianGeoKey",
    2061: "GeogPrimeMeridianLongGeoKey",
    2052: "GeogLinearUnitsGeoKey",
    2053: "GeogLinearUnitSizeGeoKey",
    2054: "GeogAngularUnitsGeoKey",
    2055: "GeogAngularUnitSizeGeoKey",
    2056: "GeogEllipsoidGeoKey",
    2057: "GeogSemiMajorAxisGeoKey",
    2058: "GeogSemiMinorAxisGeoKey",
    2059: "GeogInvFlatteningGeoKey",
    2060: "GeogAzimuthUnitsGeoKey",
    3072: "ProjectedCSTypeGeoKey",
    3073: "PCSCitationGeoKey",
    3074: "ProjectionGeoKey",
    3075: "ProjCoordTransGeoKey",
    3076: "ProjLinearUnitsGeoKey",
    3077: "ProjLinearUnitSizeGeoKey",
    3078: "ProjStdParallel1GeoKey",
    3079: "ProjStdParallel2GeoKey"
}

root = Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)

filename = askopenfilename(parent=root)

with open(filename, "rb") as f:
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
        val = len(ifd_data)
        next_ifd_offset = int.from_bytes(f.read(4), endian)

        IFD.append(ifd_data)

        i = next_ifd_offset

        tmpList = list()
        for j in range(0, ifd_size - 6, 12):
            tag = int.from_bytes(ifd_data[j:j + 2], endian)
            type_tmp = int.from_bytes(ifd_data[j + 2:j + 4], endian)
            count_tmp = int.from_bytes(ifd_data[j + 4:j + 8], endian)
            if type_tmp <= 12:
                tmp_val = count_tmp * type_dict[str(type_tmp)]
            else:
                tmp_val = 1

            if count_tmp == 1 or tmp_val > 4:
                valueOffset_tmp = int.from_bytes(ifd_data[j + 8:j + 12], endian)
            elif count_tmp <= 4 and tmp_val <= 4:
                valueOffset_tmp = (split_list(ifd_data[j + 8:j + 12], 4 // count_tmp))
                for h in range(0, len(valueOffset_tmp)):
                    valueOffset_tmp[h] = int.from_bytes(valueOffset_tmp[h], endian)

            tmpList.append(
                {
                    "tag": tag,
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

            if tmpList[-1]["tag"] == 34737:
                geoKeysValues = tmpList[-1]["values"]

            if tmpList[-1]["tag"] == 34735:
                for a in range(4, len(tmpList[-1]["values"]), 4):
                    geoKeys.append(
                        {
                            "key": tmpList[-1]["values"][a],
                            "type": tmpList[-1]["values"][a+1],
                            "count": tmpList[-1]["values"][a+2],
                            "values": tmpList[-1]["values"][a+3]
                        }
                    )

        dirEntry += tmpList

    for b in geoKeys:
        if b["type"] == 34737:
            tmp = []
            tmp = geoKeysValues[b["values"]: b["values"] + b["count"] - 1]
            b["values"] = [chr(x) for x in tmp]
            b["type"] = 2
        elif b["type"] == 0:
            b["type"] = 3
        b["key"] = geokeys_dict[b["key"]]

    print("Number of IFD:", len(IFD))
    for elem in IFD:
        print(elem)

    print("\nBaseline:")
    for elem in dirEntry:
        print(elem)

    print("GeoKeys:")
    for keys in geoKeys:
        print(keys)

