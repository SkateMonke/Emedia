from tkinter import Tk
from tkinter.filedialog import askopenfilename


def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


IFD = list()
dirEntry = []

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
            tmp_val = count_tmp * type_dict[str(type_tmp)]

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

        dirEntry = tmpList

    print("Number of IFD:", len(IFD))
    for elem in IFD:
        print(elem)

    print("\nBaseline:")
    for elem in dirEntry:
        print(elem)