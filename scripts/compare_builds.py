import os
b1 = set(os.listdir("/mnt/c/Users/len/OS/build/br2-output/build"))
b2 = set(os.listdir("/home/manas/lazy-build/output/build"))
print("In br2-output but not in lazy-build:")
for x in sorted(b1 - b2):
    if "host-" in x:
        print(" ", x)
