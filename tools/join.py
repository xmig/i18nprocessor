#!/usr/bin/env python

"""
A trivial tool for joining two files line by line
"""

import sys


def loadfile(file_name_1):
    res = []
    with open(file_name_1, "r") as fh:
        lines = fh.readlines()
        for l in lines:
            l = l[:-2]
            res.append(l)
    return res
    

def main(file_name_1, file_name_2):
    l1 = loadfile(file_name_1)
    l2 = loadfile(file_name_2)
    for i in range(0, len(l1)):
        print("{};{}".format(l1[i], l2[i]))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage ./join.py <FileName1> <FileName2>")
        exit(1)
    main(sys.argv[1], sys.argv[2])