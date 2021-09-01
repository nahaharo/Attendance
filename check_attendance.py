import csv
import argparse
import os
import datetime
import shutil
from typing import *

def today():
    return datetime.date.today().strftime('%Y-%d-%m')

class Attendance:
    header: List[str]
    def __init__(self, file):
        self.file = file
        attendance_reader = csv.reader(file, delimiter=",")
        attendances = [[col for col in row] for row in attendance_reader]
        if not attendances[0][0] == "Name":
            raise ValueError("Header of first column must be 'Name'")
        for h in attendances[0][1:]:
            try:
                a = datetime.datetime.strptime(h, '%Y-%d-%m')
            except ValueError:
                raise ValueError("Date format in csv is '%Y-%d-%m'")

        self.header = attendances[0][1:]
        self.name = [row[0] for row in attendances[1:]]
        self.attendance = [row[1:] for row in attendances[1:]]
        self.name2idx = {name: idx for idx, name in enumerate(self.name)}
    
    def find_and_check(self, name):
        if not today() in self.header:
            self._add_today()
        if name in self.name2idx:
            self.attendance[self.name2idx[name]][-1] = "O"
            print(name, 'checked')
        else:
            recommand = self._recommand(name)[:5]
            print("Reomandations:", *recommand)

    def _recommand(self, name):
        ans = []
        for len_split in range(len(name), 0, -1):
            for start_idx in range(0, len(name)-len_split+1):
                split = name[start_idx:start_idx+len_split]
                for N in self.name:
                    if split in N:
                        if not N in ans:
                            ans.append(N)
        return ans


    def _add_today(self):
        date = today()
        self.header.append(date)
        for row in self.attendance:
            row.append("X")
        

    def _save(self):
        self.file.seek(0)
        self.file.truncate(0)
        writer = csv.writer(self.file, delimiter=",")
        writer.writerow(["Name"]+self.header)
        for name, attendance in zip(self.name, self.attendance):
            writer.writerow([name]+attendance)

    def _print_checked(self):
        for name, check in zip(self.name, [row[-1] for row in self.attendance]):
            if check == "O":
                print(name)

    def _del_student(self, name):
        idx = self.name2idx[name]
        if not idx:
            return
        del self.name[idx]
        del self.attendance[idx]
        return

    def _print_status(self):
        print("Total:", len(self.name), ", checked:", len([row[-1] for row in self.attendance if row[-1]=="O"]))


def main(file):
    attendance = Attendance(file)
    try:
        while True:
            i = input()
            if len(i) == 0:
                continue
            if i[0] == ".":
                args = i.split()
                if args[0] == ".exit":
                    attendance._save()
                    print("Attendance saved")
                    return
                if args[0] == ".show":
                    attendance._print_checked()
                elif args[0] == ".del":
                    if len(args) == 1:
                        print("Need name")
                    else:
                        attendance._del_student(args[1])
                elif args[0] == ".status":
                    attendance._print_status()
                else:
                    print("Can not find any related command.")
            else:
                attendance.find_and_check(i)
    except KeyboardInterrupt:
        attendance._save()
        print("Attendance saved")
        print("Byebye")



if __name__ == "__main__":
    parser = argparse.ArgumentParser("Program for attendance check.")
    parser.add_argument('--csv', required=False, default="attendance.csv", help="path to csv")
    args = parser.parse_args()
    date = today()
    shutil.copy(args.csv, date+".csv")
    f = open(args.csv, "r+", encoding="UTF-8", newline='')
    main(f)
    f.close()