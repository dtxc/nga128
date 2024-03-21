# Copyright (c) 2024, dtxc


# NOTE: this is not a highly secure algorithm. do NOT use it for production

import re
import sys
import random
import binascii

from math import log2, floor


data = input("enter a string to hash: ")

# theoretically, there is no input length limit but longer inputs can significantly increase hashing time
if not re.match(r"^[ -~]{4,}$", data):
    print("invalid data")
    exit()

ret = bytearray() # 128 bit hash

s = sum([ord(x) for x in data])
avg = int(s / len(data)) << 2 # avg <= 0x4ec0 (~ = 126)

# randomness CAN be used for a hashing algorithm as long as the seed for the string remains the same
# NOTE: seed is always a really large number which exceeds the 64-bit limit
random.seed(len(data) | (1 << avg) + s)

ret += avg.to_bytes(2, sys.byteorder) # 0xFF < avg < 0x7FFF

# random unsigned 32-bit integer
res = random.randint(1, 1 << 32) # 4 byte integer (10 bytes left)

last = ord(data[::-1][0])


# TODO: include n-1, n+1 in the function to increase output diversity (?)
for i in range(len(data)):
    crt = ord(data[i])

    if i % 2 == 0:
        # res = n OR (floor(n / 3) << floor(log2(n)) OR (n OR l << 2))
        res -= crt | (int(crt // 3) << int(log2(crt))) | (crt | last << 2)
    else:
        res += (crt << 1) & (crt % 2)

# set the length to the maximum possible so that output length is always 16 bytes
ret += res.to_bytes(4, sys.byteorder) # 0xFFFF < res < 0xFFFFFFFF

res = random.randint(1 << 32, 1 << 64) # 8 byte integer (2 bytes left)

# in this loop only the 2^n characters will be used
arr = [2 ** x for x in range(floor(log2(len(data))))]

def f(x: int) -> int:
    # p, q, r are large prime numbers.
    p = 15731
    q = 789221
    r = 2038074743

    # this introduces non-linearity to the function
    # a small change in x will result in a large change in this variable
    # left shift by 13 is random but is large enough to create the large changes
    a = (x << 13) ^ x

    # this ensures non-linearity in the function
    # the prime numbers p, q and r are choosen to avoid repeating patterns in the output
    # and to increase diversity
    b = (a * (a * a * p + q) + r) & ((1 << 64) - 1)

    # discard high bits
    c = (b >> 32) ^ b

    return c

for i in range(len(arr)):
    crt = ord(data[arr[i]-1])
    res |= f(i)

ret += res.to_bytes(8, sys.byteorder) # 0xFFFFFFFF < res <= 0xFFFFFFFFFFFFFFFF

# another non-linear function
def g(x: int) -> int:
    # complex asf shit
    a = ((x << 7) & 0xFFFF) ^ ((x >> 3) & 0xFFFF) | ((x << 2) & 0xFFFF) ^ ((x >> 5) & 0xFFFF)
    a = ((a << 8) & 0xFFFF) ^ ((a >> 4) & 0xFFFF)
    
    return a

res = random.randint(1, 65535)

for i in range(len(data)):
    if i % 2 != 0:
        res |= g(i)

ret += res.to_bytes(2, sys.byteorder) # 0x00 < res <= 0xFFFF

tp = binascii.hexlify(ret)
print(f"0x{tp.decode()}")
