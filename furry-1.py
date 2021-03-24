# Designed with love by Aloe - A Non Deterministic Hybrid Wolf
# Copyright © 2020 Aloe
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar.

# Overview furry-1 is a 512 bit hashing function
# furry-1 starts at wikepedia.org and does the following
# 1) Reads how many links are on the current page and reads that 
#     ceil(log2(# of links)) from the content (in the event there are not enough bytes, 
#     the bits are padded w/ the nessecary number of bits start from left from the following 
#     binary string `0110011001110101011100100111001001111001`)
# 2) We construct the number from the bits using small endian format
# 3) We download that page and XOR it w/ the previous page making sure to make XOR of the smaller size
# 4) We go back to 1 until the data read is exhausted
# 5) We construct the hash:
#    Case 1: < 512 bits we append some number and bit of `0110011001110101011100100111001001111001` until we reach 512 bits and output
#    Case 2: = 512 bits, we output as is
#    Case 3L > 512 bits, we take total size of file floor((in bits) % 512) and let that be n
#               We take every n'th bit and construct hash using this 

# Precheck

import sys
import os
import requests
import math 
from bs4 import BeautifulSoup
from bitstring import ConstBitStream
import binascii

# Forward declaration of function
def sanitzeLink(link,parentLink=None):
    if(link[:2] == '//'):
        return "https:"+link
    elif(link[:1] == '/'):
        parentLink[:-1] + link
    else:
        return link
# Actual start of program 

# Testing

if(sys.byteorder != 'little'):
    print("Unsupported byte order")
    exit(1)

# Main variables
site = "https://wikepedia.org/"
file = "toCreateHash.txt"
tempFile0 = "file0.tmp"
tempFile1 = "file1.tmp"
rollingXOR = "output.tmp"
isTemp0 = False
padding = bytearray(b'furries')
linksNumber = 0
size = os.path.getsize(file) * 8 #Number of bits
currentBitsRead = 0
#Easiest way to deal with out of scope padding to write 'furries' to the end a total of 8 times
paddingMode = open(file, 'ab')
for i in range(18):
    paddingMode.write(padding)
paddingMode.close()


# Setting up
res = requests.get(site)

soup = BeautifulSoup(res.text, 'html.parser')

links = soup.find_all("a")

linksNumber = len(links)
bitsRead = math.ceil(math.log2(linksNumber))
currentBitsRead = currentBitsRead + size

b = ConstBitStream(open(file, 'rb').read())
linkTarget = b.read(bitsRead).uint
if(linkTarget > linksNumber):
    linkTarget = (linksTarget - linksNumber)

link = sanitzeLink(links[linkTarget]['href'],site)

res = requests.get(link)

file = open(rollingXOR,'w')
file.write(res.text)
while(currentBitsRead <= size):
    soup = BeautifulSoup(res.text, 'lxml')
    links = soup.find_all("a")
    linksNumber = len(links)
    bitsRead = math.ceil(math.log2(linksNumber))
    linkTarget = b.read(bitsRead).uint

    if(linkTarget > linksNumber):
        linkTarget = (linkTarget - linksNumber)
        link = sanitzeLink(links[linkTarget]['href'])

    if(isTemp0):
        file = open(tempFile0,'w')
        file.write(res.text)
        isTemp0 = False
    else:
        file = open(tempFile1,'w')
        file.write(res.text)
        isTemp0 = True
    
    # XOR borrowed w/ <3 from 
    # https://www.megabeets.net/xor-files-python/
    file1_b = bytearray(open(rollingXOR, 'rb').read())
    if(isTemp0):
        file2_b = bytearray(open(tempFile0, 'rb').read())
    else:
        file2_b = bytearray(open(tempFile1, 'rb').read())

    size = len(file1_b) if len(file1_b) < len(file2_b) else len(file2_b)
    xord_byte_array = bytearray(size)

    for i in range(size):
	    xord_byte_array[i] = file1_b[i] ^ file2_b[i]

    open(rollingXOR, 'wb').write(xord_byte_array)

    res = requests.get(link)

    currentBitsRead = currentBitsRead + bitsRead

# Outputting the hash <3

fileSize = os.path.getsize(rollingXOR) * 8 

if(fileSize < 512):
    raise("Error haven't yet implemented this")
elif(fileSize == 512):
    contents = bytearray(open(rollingXOR, 'rb').read())
    print(binascii.hexlify(contents))








