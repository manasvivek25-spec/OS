import os, shutil
src = "/mnt/c/Users/len/OS/build/br2-output/build"
dst = "/home/manas/lazy-build/output/build"
synced = 0
for d in os.listdir(src):
    if d.startswith("host-"):
        s_d = os.path.join(src, d)
        d_d = os.path.join(dst, d)
        os.makedirs(d_d, exist_ok=True)
        for f in os.listdir(s_d):
            if f.startswith(".stamp_"):
                shutil.copy2(os.path.join(s_d, f), os.path.join(d_d, f))
                synced += 1
print(f"Synced {synced} host stamps.")
