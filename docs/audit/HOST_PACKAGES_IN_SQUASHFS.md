# Audit of Host Binaries and Libraries in rootfs.squashfs

**Audit Date:** 2026-11-19  
**Source Image:** uild/v2/rootfs.squashfs (built by scripts/build_systemd_rootfs.py)  
**Total ELF binaries / libraries:** 418  
**Total host Ubuntu packages matched:** 77  
**Total files traced to host packages via dpkg -S:** 375  

## Package Breakdown

| Package | Version | File Count | Sample Files |
| :--- | :--- | :--- | :--- |
| bash | 5.2.21-2ubuntu4 | 2 | bin/bash, usr/bin/bash |
| btrfs-progs | 6.6.3-1.1build2 | 1 | bin/btrfs |
| busybox-static | 1:1.36.1-6ubuntu3.1 | 1 | bin/busybox |
| coreutils | 9.4-3ubuntu6.3 | 37 | bin/cat, bin/chmod, bin/chown (+34 more) |
| dash | 0.5.12-6ubuntu5 | 1 | bin/sh |
| diversion by libc6 from |  | 1 | lib64/ld-linux-x86-64.so.2 |
| findutils | 4.9.0-5build1 | 1 | bin/find |
| gawk | 1:5.2.1-2ubuntu0.1 | 1 | bin/awk |
| grep | 3.11-4build1 | 1 | bin/grep |
| hostname | 3.23+nmu2ubuntu2 | 1 | bin/hostname |
| kmod | 31+20240202-2ubuntu7.2 | 2 | bin/lsmod, sbin/insmod |
| libacl1 | 2.3.2-1build1.1 | 4 | lib/x86_64-linux-gnu/libacl.so.1, lib/x86_64-linux-gnu/libacl.so.1.1.2302, usr/lib/x86_64-linux-gnu/libacl.so.1 (+1 more) |
| libapparmor1 | 4.0.1really4.0.1-0ubuntu0.24.04.7 | 4 | lib/x86_64-linux-gnu/libapparmor.so.1, lib/x86_64-linux-gnu/libapparmor.so.1.17.2, usr/lib/x86_64-linux-gnu/libapparmor.so.1 (+1 more) |
| libargon2-1 | 0~20190702+dfsg-4build1 | 2 | lib/x86_64-linux-gnu/libargon2.so.1, usr/lib/x86_64-linux-gnu/libargon2.so.1 |
| libaudit1 | 1:3.1.2-2.1build1.1 | 4 | lib/x86_64-linux-gnu/libaudit.so.1, lib/x86_64-linux-gnu/libaudit.so.1.0.0, usr/lib/x86_64-linux-gnu/libaudit.so.1 (+1 more) |
| libblkid1 | 2.39.3-9ubuntu6.6 | 4 | lib/x86_64-linux-gnu/libblkid.so.1, lib/x86_64-linux-gnu/libblkid.so.1.1.0, usr/lib/x86_64-linux-gnu/libblkid.so.1 (+1 more) |
| libbz2-1.0 | 1.0.8-5.1ubuntu0.1 | 1 | lib/x86_64-linux-gnu/libbz2.so.1.0 |
| libc6 | 2.39-0ubuntu8.12 | 10 | lib/x86_64-linux-gnu/ld-linux-x86-64.so.2, lib/x86_64-linux-gnu/libc.so.6, lib/x86_64-linux-gnu/libm.so.6 (+7 more) |
| libcap-ng0 | 0.8.4-2build2 | 4 | lib/x86_64-linux-gnu/libcap-ng.so.0, lib/x86_64-linux-gnu/libcap-ng.so.0.0.0, usr/lib/x86_64-linux-gnu/libcap-ng.so.0 (+1 more) |
| libcap2 | 1:2.66-5ubuntu2.4 | 4 | lib/x86_64-linux-gnu/libcap.so.2, lib/x86_64-linux-gnu/libcap.so.2.66, usr/lib/x86_64-linux-gnu/libcap.so.2 (+1 more) |
| libcom-err2 | 1.47.0-2.4~exp1ubuntu4.1 | 4 | lib/x86_64-linux-gnu/libcom_err.so.2, lib/x86_64-linux-gnu/libcom_err.so.2.1, usr/lib/x86_64-linux-gnu/libcom_err.so.2 (+1 more) |
| libcrypt1 | 1:4.4.36-4build1 | 4 | lib/x86_64-linux-gnu/libcrypt.so.1, lib/x86_64-linux-gnu/libcrypt.so.1.1.0, usr/lib/x86_64-linux-gnu/libcrypt.so.1 (+1 more) |
| libcryptsetup12 | 2:2.7.0-1ubuntu4.2 | 2 | lib/x86_64-linux-gnu/libcryptsetup.so.12, lib/x86_64-linux-gnu/libcryptsetup.so.12.10.0 |
| libdevmapper1.02.1 | 2:1.02.185-3ubuntu3.2 | 2 | lib/x86_64-linux-gnu/libdevmapper.so.1.02.1, usr/lib/x86_64-linux-gnu/libdevmapper.so.1.02.1 |
| libexpat1 | 2.6.1-2ubuntu0.6 | 4 | lib/x86_64-linux-gnu/libexpat.so.1, lib/x86_64-linux-gnu/libexpat.so.1.9.1, usr/lib/x86_64-linux-gnu/libexpat.so.1 (+1 more) |
| libfdisk1 | 2.39.3-9ubuntu6.6 | 4 | lib/x86_64-linux-gnu/libfdisk.so.1, lib/x86_64-linux-gnu/libfdisk.so.1.1.0, usr/lib/x86_64-linux-gnu/libfdisk.so.1 (+1 more) |
| libffi8 | 3.4.6-1build1 | 4 | lib/x86_64-linux-gnu/libffi.so.8, lib/x86_64-linux-gnu/libffi.so.8.1.4, usr/lib/x86_64-linux-gnu/libffi.so.8 (+1 more) |
| libgcc-s1 | 14.2.0-4ubuntu2~24.04.1 | 2 | lib/x86_64-linux-gnu/libgcc_s.so.1, usr/lib/x86_64-linux-gnu/libgcc_s.so.1 |
| libgcrypt20 | 1.10.3-2ubuntu0.2 | 4 | lib/x86_64-linux-gnu/libgcrypt.so.20, lib/x86_64-linux-gnu/libgcrypt.so.20.4.3, usr/lib/x86_64-linux-gnu/libgcrypt.so.20 (+1 more) |
| libglib2.0-0t64 | 2.80.0-6ubuntu3.9 | 16 | lib/x86_64-linux-gnu/libgio-2.0.so.0, lib/x86_64-linux-gnu/libgio-2.0.so.0.8000.0, lib/x86_64-linux-gnu/libglib-2.0.so.0 (+13 more) |
| libgpg-error0 | 1.47-3build2.1 | 4 | lib/x86_64-linux-gnu/libgpg-error.so.0, lib/x86_64-linux-gnu/libgpg-error.so.0.34.0, usr/lib/x86_64-linux-gnu/libgpg-error.so.0 (+1 more) |
| libgssapi-krb5-2 | 1.20.1-6ubuntu2.8 | 4 | lib/x86_64-linux-gnu/libgssapi_krb5.so.2, lib/x86_64-linux-gnu/libgssapi_krb5.so.2.2, usr/lib/x86_64-linux-gnu/libgssapi_krb5.so.2 (+1 more) |
| libjson-c5 | 0.17-1build1 | 4 | lib/x86_64-linux-gnu/libjson-c.so.5, lib/x86_64-linux-gnu/libjson-c.so.5.3.0, usr/lib/x86_64-linux-gnu/libjson-c.so.5 (+1 more) |
| libk5crypto3 | 1.20.1-6ubuntu2.8 | 4 | lib/x86_64-linux-gnu/libk5crypto.so.3, lib/x86_64-linux-gnu/libk5crypto.so.3.1, usr/lib/x86_64-linux-gnu/libk5crypto.so.3 (+1 more) |
| libkeyutils1 | 1.6.3-3build1 | 4 | lib/x86_64-linux-gnu/libkeyutils.so.1, lib/x86_64-linux-gnu/libkeyutils.so.1.10, usr/lib/x86_64-linux-gnu/libkeyutils.so.1 (+1 more) |
| libkmod2 | 31+20240202-2ubuntu7.2 | 4 | lib/x86_64-linux-gnu/libkmod.so.2, lib/x86_64-linux-gnu/libkmod.so.2.4.1, usr/lib/x86_64-linux-gnu/libkmod.so.2 (+1 more) |
| libkrb5-3 | 1.20.1-6ubuntu2.8 | 4 | lib/x86_64-linux-gnu/libkrb5.so.3, lib/x86_64-linux-gnu/libkrb5.so.3.3, usr/lib/x86_64-linux-gnu/libkrb5.so.3 (+1 more) |
| libkrb5support0 | 1.20.1-6ubuntu2.8 | 4 | lib/x86_64-linux-gnu/libkrb5support.so.0, lib/x86_64-linux-gnu/libkrb5support.so.0.1, usr/lib/x86_64-linux-gnu/libkrb5support.so.0 (+1 more) |
| liblz4-1 | 1.9.4-1build1.1 | 4 | lib/x86_64-linux-gnu/liblz4.so.1, lib/x86_64-linux-gnu/liblz4.so.1.9.4, usr/lib/x86_64-linux-gnu/liblz4.so.1 (+1 more) |
| liblzma5 | 5.6.1+really5.4.5-1ubuntu0.4 | 4 | lib/x86_64-linux-gnu/liblzma.so.5, lib/x86_64-linux-gnu/liblzma.so.5.4.5, usr/lib/x86_64-linux-gnu/liblzma.so.5 (+1 more) |
| liblzo2-2 | 2.10-2build4 | 2 | lib/x86_64-linux-gnu/liblzo2.so.2, lib/x86_64-linux-gnu/liblzo2.so.2.0.0 |
| libmount1 | 2.39.3-9ubuntu6.6 | 4 | lib/x86_64-linux-gnu/libmount.so.1, lib/x86_64-linux-gnu/libmount.so.1.1.0, usr/lib/x86_64-linux-gnu/libmount.so.1 (+1 more) |
| libnetplan1 | 1.1.2-8ubuntu1~24.04.2 | 2 | lib/x86_64-linux-gnu/libnetplan.so.1, usr/lib/x86_64-linux-gnu/libnetplan.so.1 |
| libpam0g | 1.5.3-5ubuntu5.7 | 8 | lib/x86_64-linux-gnu/libpam.so.0, lib/x86_64-linux-gnu/libpam.so.0.85.1, lib/x86_64-linux-gnu/libpam_misc.so.0 (+5 more) |
| libpcre2-8-0 | 10.42-4ubuntu2.2 | 4 | lib/x86_64-linux-gnu/libpcre2-8.so.0, lib/x86_64-linux-gnu/libpcre2-8.so.0.11.2, usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 (+1 more) |
| libproc2-0 | 2:4.0.4-4ubuntu3.3 | 4 | lib/x86_64-linux-gnu/libproc2.so.0, lib/x86_64-linux-gnu/libproc2.so.0.0.2, usr/lib/x86_64-linux-gnu/libproc2.so.0 (+1 more) |
| libpython3.12-dev | 3.12.3-1ubuntu0.17 | 1 | usr/lib/python3.12/config-3.12-x86_64-linux-gnu/python.o |
| libpython3.12-minimal | 3.12.3-1ubuntu0.17 | 2 | usr/lib/python3.12/lib-dynload/_hashlib.cpython-312-x86_64-linux-gnu.so, usr/lib/python3.12/lib-dynload/_ssl.cpython-312-x86_64-linux-gnu.so |
| libpython3.12-stdlib | 3.12.3-1ubuntu0.17 | 44 | usr/lib/python3.12/lib-dynload/audioop.cpython-312-x86_64-linux-gnu.so, usr/lib/python3.12/lib-dynload/mmap.cpython-312-x86_64-linux-gnu.so, usr/lib/python3.12/lib-dynload/ossaudiodev.cpython-312-x86_64-linux-gnu.so (+41 more) |
| libpython3.12t64 | 3.12.3-1ubuntu0.17 | 1 | usr/lib/python3.12/config-3.12-x86_64-linux-gnu/libpython3.12.so |
| libseccomp2 | 2.5.5-1ubuntu3.1 | 4 | lib/x86_64-linux-gnu/libseccomp.so.2, lib/x86_64-linux-gnu/libseccomp.so.2.5.5, usr/lib/x86_64-linux-gnu/libseccomp.so.2 (+1 more) |
| libselinux1 | 3.5-2ubuntu2.1 | 2 | lib/x86_64-linux-gnu/libselinux.so.1, usr/lib/x86_64-linux-gnu/libselinux.so.1 |
| libsmartcols1 | 2.39.3-9ubuntu6.6 | 4 | lib/x86_64-linux-gnu/libsmartcols.so.1, lib/x86_64-linux-gnu/libsmartcols.so.1.1.0, usr/lib/x86_64-linux-gnu/libsmartcols.so.1 (+1 more) |
| libssl3t64 | 3.0.13-0ubuntu3.16 | 4 | lib/x86_64-linux-gnu/libcrypto.so.3, lib/x86_64-linux-gnu/libssl.so.3, usr/lib/x86_64-linux-gnu/libcrypto.so.3 (+1 more) |
| libsystemd-shared | 255.4-1ubuntu8.18 | 2 | usr/lib/x86_64-linux-gnu/systemd/libsystemd-core-255.so, usr/lib/x86_64-linux-gnu/systemd/libsystemd-shared-255.so |
| libsystemd0 | 255.4-1ubuntu8.18 | 4 | lib/x86_64-linux-gnu/libsystemd.so.0, lib/x86_64-linux-gnu/libsystemd.so.0.38.0, usr/lib/x86_64-linux-gnu/libsystemd.so.0 (+1 more) |
| libtinfo6 | 6.4+20240113-1ubuntu2.2 | 4 | lib/x86_64-linux-gnu/libtinfo.so.6, lib/x86_64-linux-gnu/libtinfo.so.6.4, usr/lib/x86_64-linux-gnu/libtinfo.so.6 (+1 more) |
| libudev1 | 255.4-1ubuntu8.18 | 4 | lib/x86_64-linux-gnu/libudev.so.1, lib/x86_64-linux-gnu/libudev.so.1.7.8, usr/lib/x86_64-linux-gnu/libudev.so.1 (+1 more) |
| libuuid1 | 2.39.3-9ubuntu6.6 | 4 | lib/x86_64-linux-gnu/libuuid.so.1, lib/x86_64-linux-gnu/libuuid.so.1.3.0, usr/lib/x86_64-linux-gnu/libuuid.so.1 (+1 more) |
| libyaml-0-2 | 0.2.5-1build1 | 4 | lib/x86_64-linux-gnu/libyaml-0.so.2, lib/x86_64-linux-gnu/libyaml-0.so.2.0.9, usr/lib/x86_64-linux-gnu/libyaml-0.so.2 (+1 more) |
| libzstd1 | 1.5.5+dfsg2-2build1.1 | 4 | lib/x86_64-linux-gnu/libzstd.so.1, lib/x86_64-linux-gnu/libzstd.so.1.5.5, usr/lib/x86_64-linux-gnu/libzstd.so.1 (+1 more) |
| login | 1:4.13+dfsg1-4ubuntu3.2 | 2 | bin/login, usr/bin/login |
| mount | 2.39.3-9ubuntu6.6 | 2 | bin/mount, bin/umount |
| ncurses-bin | 6.4+20240113-1ubuntu2.2 | 1 | bin/clear |
| netplan-generator | 1.1.2-8ubuntu1~24.04.2 | 1 | usr/libexec/netplan/generate |
| procps | 2:4.0.4-4ubuntu3.3 | 5 | bin/free, bin/kill, bin/ps (+2 more) |
| python3-gdbm | 3.12.3-0ubuntu1 | 1 | usr/lib/python3.12/lib-dynload/_gdbm.cpython-312-x86_64-linux-gnu.so |
| python3-minimal | 3.12.3-0ubuntu2.1 | 1 | usr/bin/python3 |
| python3-yaml | 6.0.1-2build2 | 1 | usr/lib/python3/dist-packages/yaml/_yaml.cpython-312-x86_64-linux-gnu.so |
| python3.12-minimal | 3.12.3-1ubuntu0.17 | 2 | bin/python3, usr/bin/python3.12 |
| sed | 4.9-2ubuntu0.24.04.1 | 1 | bin/sed |
| systemd | 255.4-1ubuntu8.18 | 60 | bin/systemctl, sbin/init, sbin/poweroff (+57 more) |
| systemd-resolved | 255.4-1ubuntu8.18 | 1 | usr/lib/systemd/systemd-resolved |
| systemd-timesyncd | 255.4-1ubuntu8.18 | 1 | usr/lib/systemd/systemd-timesyncd |
| udev | 255.4-1ubuntu8.18 | 2 | usr/bin/udevadm, usr/lib/systemd/systemd-udevd |
| util-linux | 2.39.3-9ubuntu6.6 | 6 | bin/findmnt, bin/lsblk, sbin/agetty (+3 more) |
| zlib1g | 1:1.3.dfsg-3.1ubuntu2.3 | 4 | lib/x86_64-linux-gnu/libz.so.1, lib/x86_64-linux-gnu/libz.so.1.3, usr/lib/x86_64-linux-gnu/libz.so.1 (+1 more) |

## Full Inventory of Files Copied from Host

| Target Path in Rootfs | Host Path (/) | Origin Package | Package Version |
| :--- | :--- | :--- | :--- |
| bin/bash | /usr/bin/bash | bash | 5.2.21-2ubuntu4 |
| usr/bin/bash | /usr/bin/bash | bash | 5.2.21-2ubuntu4 |
| bin/btrfs | /bin/btrfs | btrfs-progs | 6.6.3-1.1build2 |
| bin/busybox | /usr/bin/busybox | busybox-static | 1:1.36.1-6ubuntu3.1 |
| bin/cat | /usr/bin/cat | coreutils | 9.4-3ubuntu6.3 |
| bin/chmod | /usr/bin/chmod | coreutils | 9.4-3ubuntu6.3 |
| bin/chown | /usr/bin/chown | coreutils | 9.4-3ubuntu6.3 |
| bin/cp | /usr/bin/cp | coreutils | 9.4-3ubuntu6.3 |
| bin/cut | /usr/bin/cut | coreutils | 9.4-3ubuntu6.3 |
| bin/date | /usr/bin/date | coreutils | 9.4-3ubuntu6.3 |
| bin/df | /usr/bin/df | coreutils | 9.4-3ubuntu6.3 |
| bin/echo | /usr/bin/echo | coreutils | 9.4-3ubuntu6.3 |
| bin/env | /usr/bin/env | coreutils | 9.4-3ubuntu6.3 |
| bin/false | /usr/bin/false | coreutils | 9.4-3ubuntu6.3 |
| bin/head | /usr/bin/head | coreutils | 9.4-3ubuntu6.3 |
| bin/id | /usr/bin/id | coreutils | 9.4-3ubuntu6.3 |
| bin/ls | /usr/bin/ls | coreutils | 9.4-3ubuntu6.3 |
| bin/mkdir | /usr/bin/mkdir | coreutils | 9.4-3ubuntu6.3 |
| bin/mknod | /usr/bin/mknod | coreutils | 9.4-3ubuntu6.3 |
| bin/mv | /usr/bin/mv | coreutils | 9.4-3ubuntu6.3 |
| bin/pwd | /usr/bin/pwd | coreutils | 9.4-3ubuntu6.3 |
| bin/rm | /usr/bin/rm | coreutils | 9.4-3ubuntu6.3 |
| bin/rmdir | /usr/bin/rmdir | coreutils | 9.4-3ubuntu6.3 |
| bin/sleep | /usr/bin/sleep | coreutils | 9.4-3ubuntu6.3 |
| bin/sort | /usr/bin/sort | coreutils | 9.4-3ubuntu6.3 |
| bin/sync | /usr/bin/sync | coreutils | 9.4-3ubuntu6.3 |
| bin/tail | /usr/bin/tail | coreutils | 9.4-3ubuntu6.3 |
| bin/tee | /usr/bin/tee | coreutils | 9.4-3ubuntu6.3 |
| bin/test | /usr/bin/test | coreutils | 9.4-3ubuntu6.3 |
| bin/touch | /usr/bin/touch | coreutils | 9.4-3ubuntu6.3 |
| bin/tr | /usr/bin/tr | coreutils | 9.4-3ubuntu6.3 |
| bin/true | /usr/bin/true | coreutils | 9.4-3ubuntu6.3 |
| bin/uname | /usr/bin/uname | coreutils | 9.4-3ubuntu6.3 |
| bin/uniq | /usr/bin/uniq | coreutils | 9.4-3ubuntu6.3 |
| bin/wc | /usr/bin/wc | coreutils | 9.4-3ubuntu6.3 |
| bin/whoami | /usr/bin/whoami | coreutils | 9.4-3ubuntu6.3 |
| usr/bin/cat | /usr/bin/cat | coreutils | 9.4-3ubuntu6.3 |
| usr/bin/env | /usr/bin/env | coreutils | 9.4-3ubuntu6.3 |
| usr/bin/mkdir | /usr/bin/mkdir | coreutils | 9.4-3ubuntu6.3 |
| usr/bin/touch | /usr/bin/touch | coreutils | 9.4-3ubuntu6.3 |
| usr/bin/uname | /usr/bin/uname | coreutils | 9.4-3ubuntu6.3 |
| bin/sh | /usr/bin/dash | dash | 0.5.12-6ubuntu5 |
| lib64/ld-linux-x86-64.so.2 | /lib64/ld-linux-x86-64.so.2 | diversion by libc6 from |  |
| bin/find | /usr/bin/find | findutils | 4.9.0-5build1 |
| bin/awk | /usr/bin/gawk | gawk | 1:5.2.1-2ubuntu0.1 |
| bin/grep | /usr/bin/grep | grep | 3.11-4build1 |
| bin/hostname | /usr/bin/hostname | hostname | 3.23+nmu2ubuntu2 |
| bin/lsmod | /usr/bin/kmod | kmod | 31+20240202-2ubuntu7.2 |
| sbin/insmod | /usr/bin/kmod | kmod | 31+20240202-2ubuntu7.2 |
| lib/x86_64-linux-gnu/libacl.so.1 | /usr/lib/x86_64-linux-gnu/libacl.so.1.1.2302 | libacl1 | 2.3.2-1build1.1 |
| lib/x86_64-linux-gnu/libacl.so.1.1.2302 | /usr/lib/x86_64-linux-gnu/libacl.so.1.1.2302 | libacl1 | 2.3.2-1build1.1 |
| usr/lib/x86_64-linux-gnu/libacl.so.1 | /usr/lib/x86_64-linux-gnu/libacl.so.1 | libacl1 | 2.3.2-1build1.1 |
| usr/lib/x86_64-linux-gnu/libacl.so.1.1.2302 | /usr/lib/x86_64-linux-gnu/libacl.so.1.1.2302 | libacl1 | 2.3.2-1build1.1 |
| lib/x86_64-linux-gnu/libapparmor.so.1 | /usr/lib/x86_64-linux-gnu/libapparmor.so.1.17.2 | libapparmor1 | 4.0.1really4.0.1-0ubuntu0.24.04.7 |
| lib/x86_64-linux-gnu/libapparmor.so.1.17.2 | /usr/lib/x86_64-linux-gnu/libapparmor.so.1.17.2 | libapparmor1 | 4.0.1really4.0.1-0ubuntu0.24.04.7 |
| usr/lib/x86_64-linux-gnu/libapparmor.so.1 | /usr/lib/x86_64-linux-gnu/libapparmor.so.1 | libapparmor1 | 4.0.1really4.0.1-0ubuntu0.24.04.7 |
| usr/lib/x86_64-linux-gnu/libapparmor.so.1.17.2 | /usr/lib/x86_64-linux-gnu/libapparmor.so.1.17.2 | libapparmor1 | 4.0.1really4.0.1-0ubuntu0.24.04.7 |
| lib/x86_64-linux-gnu/libargon2.so.1 | /usr/lib/x86_64-linux-gnu/libargon2.so.1 | libargon2-1 | 0~20190702+dfsg-4build1 |
| usr/lib/x86_64-linux-gnu/libargon2.so.1 | /usr/lib/x86_64-linux-gnu/libargon2.so.1 | libargon2-1 | 0~20190702+dfsg-4build1 |
| lib/x86_64-linux-gnu/libaudit.so.1 | /usr/lib/x86_64-linux-gnu/libaudit.so.1.0.0 | libaudit1 | 1:3.1.2-2.1build1.1 |
| lib/x86_64-linux-gnu/libaudit.so.1.0.0 | /usr/lib/x86_64-linux-gnu/libaudit.so.1.0.0 | libaudit1 | 1:3.1.2-2.1build1.1 |
| usr/lib/x86_64-linux-gnu/libaudit.so.1 | /usr/lib/x86_64-linux-gnu/libaudit.so.1 | libaudit1 | 1:3.1.2-2.1build1.1 |
| usr/lib/x86_64-linux-gnu/libaudit.so.1.0.0 | /usr/lib/x86_64-linux-gnu/libaudit.so.1.0.0 | libaudit1 | 1:3.1.2-2.1build1.1 |
| lib/x86_64-linux-gnu/libblkid.so.1 | /usr/lib/x86_64-linux-gnu/libblkid.so.1.1.0 | libblkid1 | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libblkid.so.1.1.0 | /usr/lib/x86_64-linux-gnu/libblkid.so.1.1.0 | libblkid1 | 2.39.3-9ubuntu6.6 |
| usr/lib/x86_64-linux-gnu/libblkid.so.1 | /usr/lib/x86_64-linux-gnu/libblkid.so.1 | libblkid1 | 2.39.3-9ubuntu6.6 |
| usr/lib/x86_64-linux-gnu/libblkid.so.1.1.0 | /usr/lib/x86_64-linux-gnu/libblkid.so.1.1.0 | libblkid1 | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libbz2.so.1.0 | /usr/lib/x86_64-linux-gnu/libbz2.so.1.0.4 | libbz2-1.0 | 1.0.8-5.1ubuntu0.1 |
| lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 | /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 | libc6 | 2.39-0ubuntu8.12 |
| lib/x86_64-linux-gnu/libc.so.6 | /usr/lib/x86_64-linux-gnu/libc.so.6 | libc6 | 2.39-0ubuntu8.12 |
| lib/x86_64-linux-gnu/libm.so.6 | /usr/lib/x86_64-linux-gnu/libm.so.6 | libc6 | 2.39-0ubuntu8.12 |
| lib/x86_64-linux-gnu/libpthread.so.0 | /usr/lib/x86_64-linux-gnu/libpthread.so.0 | libc6 | 2.39-0ubuntu8.12 |
| lib/x86_64-linux-gnu/libresolv.so.2 | /usr/lib/x86_64-linux-gnu/libresolv.so.2 | libc6 | 2.39-0ubuntu8.12 |
| usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 | /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 | libc6 | 2.39-0ubuntu8.12 |
| usr/lib/x86_64-linux-gnu/libc.so.6 | /usr/lib/x86_64-linux-gnu/libc.so.6 | libc6 | 2.39-0ubuntu8.12 |
| usr/lib/x86_64-linux-gnu/libm.so.6 | /usr/lib/x86_64-linux-gnu/libm.so.6 | libc6 | 2.39-0ubuntu8.12 |
| usr/lib/x86_64-linux-gnu/libpthread.so.0 | /usr/lib/x86_64-linux-gnu/libpthread.so.0 | libc6 | 2.39-0ubuntu8.12 |
| usr/lib/x86_64-linux-gnu/libresolv.so.2 | /usr/lib/x86_64-linux-gnu/libresolv.so.2 | libc6 | 2.39-0ubuntu8.12 |
| lib/x86_64-linux-gnu/libcap-ng.so.0 | /usr/lib/x86_64-linux-gnu/libcap-ng.so.0.0.0 | libcap-ng0 | 0.8.4-2build2 |
| lib/x86_64-linux-gnu/libcap-ng.so.0.0.0 | /usr/lib/x86_64-linux-gnu/libcap-ng.so.0.0.0 | libcap-ng0 | 0.8.4-2build2 |
| usr/lib/x86_64-linux-gnu/libcap-ng.so.0 | /usr/lib/x86_64-linux-gnu/libcap-ng.so.0 | libcap-ng0 | 0.8.4-2build2 |
| usr/lib/x86_64-linux-gnu/libcap-ng.so.0.0.0 | /usr/lib/x86_64-linux-gnu/libcap-ng.so.0.0.0 | libcap-ng0 | 0.8.4-2build2 |
| lib/x86_64-linux-gnu/libcap.so.2 | /usr/lib/x86_64-linux-gnu/libcap.so.2.66 | libcap2 | 1:2.66-5ubuntu2.4 |
| lib/x86_64-linux-gnu/libcap.so.2.66 | /usr/lib/x86_64-linux-gnu/libcap.so.2.66 | libcap2 | 1:2.66-5ubuntu2.4 |
| usr/lib/x86_64-linux-gnu/libcap.so.2 | /usr/lib/x86_64-linux-gnu/libcap.so.2 | libcap2 | 1:2.66-5ubuntu2.4 |
| usr/lib/x86_64-linux-gnu/libcap.so.2.66 | /usr/lib/x86_64-linux-gnu/libcap.so.2.66 | libcap2 | 1:2.66-5ubuntu2.4 |
| lib/x86_64-linux-gnu/libcom_err.so.2 | /usr/lib/x86_64-linux-gnu/libcom_err.so.2.1 | libcom-err2 | 1.47.0-2.4~exp1ubuntu4.1 |
| lib/x86_64-linux-gnu/libcom_err.so.2.1 | /usr/lib/x86_64-linux-gnu/libcom_err.so.2.1 | libcom-err2 | 1.47.0-2.4~exp1ubuntu4.1 |
| usr/lib/x86_64-linux-gnu/libcom_err.so.2 | /usr/lib/x86_64-linux-gnu/libcom_err.so.2 | libcom-err2 | 1.47.0-2.4~exp1ubuntu4.1 |
| usr/lib/x86_64-linux-gnu/libcom_err.so.2.1 | /usr/lib/x86_64-linux-gnu/libcom_err.so.2.1 | libcom-err2 | 1.47.0-2.4~exp1ubuntu4.1 |
| lib/x86_64-linux-gnu/libcrypt.so.1 | /usr/lib/x86_64-linux-gnu/libcrypt.so.1.1.0 | libcrypt1 | 1:4.4.36-4build1 |
| lib/x86_64-linux-gnu/libcrypt.so.1.1.0 | /usr/lib/x86_64-linux-gnu/libcrypt.so.1.1.0 | libcrypt1 | 1:4.4.36-4build1 |
| usr/lib/x86_64-linux-gnu/libcrypt.so.1 | /usr/lib/x86_64-linux-gnu/libcrypt.so.1 | libcrypt1 | 1:4.4.36-4build1 |
| usr/lib/x86_64-linux-gnu/libcrypt.so.1.1.0 | /usr/lib/x86_64-linux-gnu/libcrypt.so.1.1.0 | libcrypt1 | 1:4.4.36-4build1 |
| lib/x86_64-linux-gnu/libcryptsetup.so.12 | /lib/x86_64-linux-gnu/libcryptsetup.so.12 | libcryptsetup12 | 2:2.7.0-1ubuntu4.2 |
| lib/x86_64-linux-gnu/libcryptsetup.so.12.10.0 | /lib/x86_64-linux-gnu/libcryptsetup.so.12.10.0 | libcryptsetup12 | 2:2.7.0-1ubuntu4.2 |
| lib/x86_64-linux-gnu/libdevmapper.so.1.02.1 | /usr/lib/x86_64-linux-gnu/libdevmapper.so.1.02.1 | libdevmapper1.02.1 | 2:1.02.185-3ubuntu3.2 |
| usr/lib/x86_64-linux-gnu/libdevmapper.so.1.02.1 | /usr/lib/x86_64-linux-gnu/libdevmapper.so.1.02.1 | libdevmapper1.02.1 | 2:1.02.185-3ubuntu3.2 |
| lib/x86_64-linux-gnu/libexpat.so.1 | /usr/lib/x86_64-linux-gnu/libexpat.so.1.9.1 | libexpat1 | 2.6.1-2ubuntu0.6 |
| lib/x86_64-linux-gnu/libexpat.so.1.9.1 | /usr/lib/x86_64-linux-gnu/libexpat.so.1.9.1 | libexpat1 | 2.6.1-2ubuntu0.6 |
| usr/lib/x86_64-linux-gnu/libexpat.so.1 | /usr/lib/x86_64-linux-gnu/libexpat.so.1 | libexpat1 | 2.6.1-2ubuntu0.6 |
| usr/lib/x86_64-linux-gnu/libexpat.so.1.9.1 | /usr/lib/x86_64-linux-gnu/libexpat.so.1.9.1 | libexpat1 | 2.6.1-2ubuntu0.6 |
| lib/x86_64-linux-gnu/libfdisk.so.1 | /usr/lib/x86_64-linux-gnu/libfdisk.so.1.1.0 | libfdisk1 | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libfdisk.so.1.1.0 | /usr/lib/x86_64-linux-gnu/libfdisk.so.1.1.0 | libfdisk1 | 2.39.3-9ubuntu6.6 |
| usr/lib/x86_64-linux-gnu/libfdisk.so.1 | /usr/lib/x86_64-linux-gnu/libfdisk.so.1 | libfdisk1 | 2.39.3-9ubuntu6.6 |
| usr/lib/x86_64-linux-gnu/libfdisk.so.1.1.0 | /usr/lib/x86_64-linux-gnu/libfdisk.so.1.1.0 | libfdisk1 | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libffi.so.8 | /usr/lib/x86_64-linux-gnu/libffi.so.8.1.4 | libffi8 | 3.4.6-1build1 |
| lib/x86_64-linux-gnu/libffi.so.8.1.4 | /usr/lib/x86_64-linux-gnu/libffi.so.8.1.4 | libffi8 | 3.4.6-1build1 |
| usr/lib/x86_64-linux-gnu/libffi.so.8 | /usr/lib/x86_64-linux-gnu/libffi.so.8 | libffi8 | 3.4.6-1build1 |
| usr/lib/x86_64-linux-gnu/libffi.so.8.1.4 | /usr/lib/x86_64-linux-gnu/libffi.so.8.1.4 | libffi8 | 3.4.6-1build1 |
| lib/x86_64-linux-gnu/libgcc_s.so.1 | /usr/lib/x86_64-linux-gnu/libgcc_s.so.1 | libgcc-s1 | 14.2.0-4ubuntu2~24.04.1 |
| usr/lib/x86_64-linux-gnu/libgcc_s.so.1 | /usr/lib/x86_64-linux-gnu/libgcc_s.so.1 | libgcc-s1 | 14.2.0-4ubuntu2~24.04.1 |
| lib/x86_64-linux-gnu/libgcrypt.so.20 | /usr/lib/x86_64-linux-gnu/libgcrypt.so.20.4.3 | libgcrypt20 | 1.10.3-2ubuntu0.2 |
| lib/x86_64-linux-gnu/libgcrypt.so.20.4.3 | /usr/lib/x86_64-linux-gnu/libgcrypt.so.20.4.3 | libgcrypt20 | 1.10.3-2ubuntu0.2 |
| usr/lib/x86_64-linux-gnu/libgcrypt.so.20 | /usr/lib/x86_64-linux-gnu/libgcrypt.so.20 | libgcrypt20 | 1.10.3-2ubuntu0.2 |
| usr/lib/x86_64-linux-gnu/libgcrypt.so.20.4.3 | /usr/lib/x86_64-linux-gnu/libgcrypt.so.20.4.3 | libgcrypt20 | 1.10.3-2ubuntu0.2 |
| lib/x86_64-linux-gnu/libgio-2.0.so.0 | /usr/lib/x86_64-linux-gnu/libgio-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| lib/x86_64-linux-gnu/libgio-2.0.so.0.8000.0 | /usr/lib/x86_64-linux-gnu/libgio-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| lib/x86_64-linux-gnu/libglib-2.0.so.0 | /usr/lib/x86_64-linux-gnu/libglib-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| lib/x86_64-linux-gnu/libglib-2.0.so.0.8000.0 | /usr/lib/x86_64-linux-gnu/libglib-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| lib/x86_64-linux-gnu/libgmodule-2.0.so.0 | /usr/lib/x86_64-linux-gnu/libgmodule-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| lib/x86_64-linux-gnu/libgmodule-2.0.so.0.8000.0 | /usr/lib/x86_64-linux-gnu/libgmodule-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| lib/x86_64-linux-gnu/libgobject-2.0.so.0 | /usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| lib/x86_64-linux-gnu/libgobject-2.0.so.0.8000.0 | /usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| usr/lib/x86_64-linux-gnu/libgio-2.0.so.0 | /usr/lib/x86_64-linux-gnu/libgio-2.0.so.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| usr/lib/x86_64-linux-gnu/libgio-2.0.so.0.8000.0 | /usr/lib/x86_64-linux-gnu/libgio-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| usr/lib/x86_64-linux-gnu/libglib-2.0.so.0 | /usr/lib/x86_64-linux-gnu/libglib-2.0.so.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| usr/lib/x86_64-linux-gnu/libglib-2.0.so.0.8000.0 | /usr/lib/x86_64-linux-gnu/libglib-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| usr/lib/x86_64-linux-gnu/libgmodule-2.0.so.0 | /usr/lib/x86_64-linux-gnu/libgmodule-2.0.so.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| usr/lib/x86_64-linux-gnu/libgmodule-2.0.so.0.8000.0 | /usr/lib/x86_64-linux-gnu/libgmodule-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0 | /usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0.8000.0 | /usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0.8000.0 | libglib2.0-0t64 | 2.80.0-6ubuntu3.9 |
| lib/x86_64-linux-gnu/libgpg-error.so.0 | /usr/lib/x86_64-linux-gnu/libgpg-error.so.0.34.0 | libgpg-error0 | 1.47-3build2.1 |
| lib/x86_64-linux-gnu/libgpg-error.so.0.34.0 | /usr/lib/x86_64-linux-gnu/libgpg-error.so.0.34.0 | libgpg-error0 | 1.47-3build2.1 |
| usr/lib/x86_64-linux-gnu/libgpg-error.so.0 | /usr/lib/x86_64-linux-gnu/libgpg-error.so.0 | libgpg-error0 | 1.47-3build2.1 |
| usr/lib/x86_64-linux-gnu/libgpg-error.so.0.34.0 | /usr/lib/x86_64-linux-gnu/libgpg-error.so.0.34.0 | libgpg-error0 | 1.47-3build2.1 |
| lib/x86_64-linux-gnu/libgssapi_krb5.so.2 | /usr/lib/x86_64-linux-gnu/libgssapi_krb5.so.2.2 | libgssapi-krb5-2 | 1.20.1-6ubuntu2.8 |
| lib/x86_64-linux-gnu/libgssapi_krb5.so.2.2 | /usr/lib/x86_64-linux-gnu/libgssapi_krb5.so.2.2 | libgssapi-krb5-2 | 1.20.1-6ubuntu2.8 |
| usr/lib/x86_64-linux-gnu/libgssapi_krb5.so.2 | /usr/lib/x86_64-linux-gnu/libgssapi_krb5.so.2 | libgssapi-krb5-2 | 1.20.1-6ubuntu2.8 |
| usr/lib/x86_64-linux-gnu/libgssapi_krb5.so.2.2 | /usr/lib/x86_64-linux-gnu/libgssapi_krb5.so.2.2 | libgssapi-krb5-2 | 1.20.1-6ubuntu2.8 |
| lib/x86_64-linux-gnu/libjson-c.so.5 | /usr/lib/x86_64-linux-gnu/libjson-c.so.5.3.0 | libjson-c5 | 0.17-1build1 |
| lib/x86_64-linux-gnu/libjson-c.so.5.3.0 | /usr/lib/x86_64-linux-gnu/libjson-c.so.5.3.0 | libjson-c5 | 0.17-1build1 |
| usr/lib/x86_64-linux-gnu/libjson-c.so.5 | /usr/lib/x86_64-linux-gnu/libjson-c.so.5 | libjson-c5 | 0.17-1build1 |
| usr/lib/x86_64-linux-gnu/libjson-c.so.5.3.0 | /usr/lib/x86_64-linux-gnu/libjson-c.so.5.3.0 | libjson-c5 | 0.17-1build1 |
| lib/x86_64-linux-gnu/libk5crypto.so.3 | /usr/lib/x86_64-linux-gnu/libk5crypto.so.3.1 | libk5crypto3 | 1.20.1-6ubuntu2.8 |
| lib/x86_64-linux-gnu/libk5crypto.so.3.1 | /usr/lib/x86_64-linux-gnu/libk5crypto.so.3.1 | libk5crypto3 | 1.20.1-6ubuntu2.8 |
| usr/lib/x86_64-linux-gnu/libk5crypto.so.3 | /usr/lib/x86_64-linux-gnu/libk5crypto.so.3 | libk5crypto3 | 1.20.1-6ubuntu2.8 |
| usr/lib/x86_64-linux-gnu/libk5crypto.so.3.1 | /usr/lib/x86_64-linux-gnu/libk5crypto.so.3.1 | libk5crypto3 | 1.20.1-6ubuntu2.8 |
| lib/x86_64-linux-gnu/libkeyutils.so.1 | /usr/lib/x86_64-linux-gnu/libkeyutils.so.1.10 | libkeyutils1 | 1.6.3-3build1 |
| lib/x86_64-linux-gnu/libkeyutils.so.1.10 | /usr/lib/x86_64-linux-gnu/libkeyutils.so.1.10 | libkeyutils1 | 1.6.3-3build1 |
| usr/lib/x86_64-linux-gnu/libkeyutils.so.1 | /usr/lib/x86_64-linux-gnu/libkeyutils.so.1 | libkeyutils1 | 1.6.3-3build1 |
| usr/lib/x86_64-linux-gnu/libkeyutils.so.1.10 | /usr/lib/x86_64-linux-gnu/libkeyutils.so.1.10 | libkeyutils1 | 1.6.3-3build1 |
| lib/x86_64-linux-gnu/libkmod.so.2 | /usr/lib/x86_64-linux-gnu/libkmod.so.2.4.1 | libkmod2 | 31+20240202-2ubuntu7.2 |
| lib/x86_64-linux-gnu/libkmod.so.2.4.1 | /usr/lib/x86_64-linux-gnu/libkmod.so.2.4.1 | libkmod2 | 31+20240202-2ubuntu7.2 |
| usr/lib/x86_64-linux-gnu/libkmod.so.2 | /usr/lib/x86_64-linux-gnu/libkmod.so.2 | libkmod2 | 31+20240202-2ubuntu7.2 |
| usr/lib/x86_64-linux-gnu/libkmod.so.2.4.1 | /usr/lib/x86_64-linux-gnu/libkmod.so.2.4.1 | libkmod2 | 31+20240202-2ubuntu7.2 |
| lib/x86_64-linux-gnu/libkrb5.so.3 | /usr/lib/x86_64-linux-gnu/libkrb5.so.3.3 | libkrb5-3 | 1.20.1-6ubuntu2.8 |
| lib/x86_64-linux-gnu/libkrb5.so.3.3 | /usr/lib/x86_64-linux-gnu/libkrb5.so.3.3 | libkrb5-3 | 1.20.1-6ubuntu2.8 |
| usr/lib/x86_64-linux-gnu/libkrb5.so.3 | /usr/lib/x86_64-linux-gnu/libkrb5.so.3 | libkrb5-3 | 1.20.1-6ubuntu2.8 |
| usr/lib/x86_64-linux-gnu/libkrb5.so.3.3 | /usr/lib/x86_64-linux-gnu/libkrb5.so.3.3 | libkrb5-3 | 1.20.1-6ubuntu2.8 |
| lib/x86_64-linux-gnu/libkrb5support.so.0 | /usr/lib/x86_64-linux-gnu/libkrb5support.so.0.1 | libkrb5support0 | 1.20.1-6ubuntu2.8 |
| lib/x86_64-linux-gnu/libkrb5support.so.0.1 | /usr/lib/x86_64-linux-gnu/libkrb5support.so.0.1 | libkrb5support0 | 1.20.1-6ubuntu2.8 |
| usr/lib/x86_64-linux-gnu/libkrb5support.so.0 | /usr/lib/x86_64-linux-gnu/libkrb5support.so.0 | libkrb5support0 | 1.20.1-6ubuntu2.8 |
| usr/lib/x86_64-linux-gnu/libkrb5support.so.0.1 | /usr/lib/x86_64-linux-gnu/libkrb5support.so.0.1 | libkrb5support0 | 1.20.1-6ubuntu2.8 |
| lib/x86_64-linux-gnu/liblz4.so.1 | /usr/lib/x86_64-linux-gnu/liblz4.so.1.9.4 | liblz4-1 | 1.9.4-1build1.1 |
| lib/x86_64-linux-gnu/liblz4.so.1.9.4 | /usr/lib/x86_64-linux-gnu/liblz4.so.1.9.4 | liblz4-1 | 1.9.4-1build1.1 |
| usr/lib/x86_64-linux-gnu/liblz4.so.1 | /usr/lib/x86_64-linux-gnu/liblz4.so.1 | liblz4-1 | 1.9.4-1build1.1 |
| usr/lib/x86_64-linux-gnu/liblz4.so.1.9.4 | /usr/lib/x86_64-linux-gnu/liblz4.so.1.9.4 | liblz4-1 | 1.9.4-1build1.1 |
| lib/x86_64-linux-gnu/liblzma.so.5 | /usr/lib/x86_64-linux-gnu/liblzma.so.5.4.5 | liblzma5 | 5.6.1+really5.4.5-1ubuntu0.4 |
| lib/x86_64-linux-gnu/liblzma.so.5.4.5 | /usr/lib/x86_64-linux-gnu/liblzma.so.5.4.5 | liblzma5 | 5.6.1+really5.4.5-1ubuntu0.4 |
| usr/lib/x86_64-linux-gnu/liblzma.so.5 | /usr/lib/x86_64-linux-gnu/liblzma.so.5 | liblzma5 | 5.6.1+really5.4.5-1ubuntu0.4 |
| usr/lib/x86_64-linux-gnu/liblzma.so.5.4.5 | /usr/lib/x86_64-linux-gnu/liblzma.so.5.4.5 | liblzma5 | 5.6.1+really5.4.5-1ubuntu0.4 |
| lib/x86_64-linux-gnu/liblzo2.so.2 | /lib/x86_64-linux-gnu/liblzo2.so.2 | liblzo2-2 | 2.10-2build4 |
| lib/x86_64-linux-gnu/liblzo2.so.2.0.0 | /lib/x86_64-linux-gnu/liblzo2.so.2.0.0 | liblzo2-2 | 2.10-2build4 |
| lib/x86_64-linux-gnu/libmount.so.1 | /usr/lib/x86_64-linux-gnu/libmount.so.1.1.0 | libmount1 | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libmount.so.1.1.0 | /usr/lib/x86_64-linux-gnu/libmount.so.1.1.0 | libmount1 | 2.39.3-9ubuntu6.6 |
| usr/lib/x86_64-linux-gnu/libmount.so.1 | /usr/lib/x86_64-linux-gnu/libmount.so.1 | libmount1 | 2.39.3-9ubuntu6.6 |
| usr/lib/x86_64-linux-gnu/libmount.so.1.1.0 | /usr/lib/x86_64-linux-gnu/libmount.so.1.1.0 | libmount1 | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libnetplan.so.1 | /usr/lib/x86_64-linux-gnu/libnetplan.so.1 | libnetplan1 | 1.1.2-8ubuntu1~24.04.2 |
| usr/lib/x86_64-linux-gnu/libnetplan.so.1 | /usr/lib/x86_64-linux-gnu/libnetplan.so.1 | libnetplan1 | 1.1.2-8ubuntu1~24.04.2 |
| lib/x86_64-linux-gnu/libpam.so.0 | /usr/lib/x86_64-linux-gnu/libpam.so.0.85.1 | libpam0g | 1.5.3-5ubuntu5.7 |
| lib/x86_64-linux-gnu/libpam.so.0.85.1 | /usr/lib/x86_64-linux-gnu/libpam.so.0.85.1 | libpam0g | 1.5.3-5ubuntu5.7 |
| lib/x86_64-linux-gnu/libpam_misc.so.0 | /usr/lib/x86_64-linux-gnu/libpam_misc.so.0.82.1 | libpam0g | 1.5.3-5ubuntu5.7 |
| lib/x86_64-linux-gnu/libpam_misc.so.0.82.1 | /usr/lib/x86_64-linux-gnu/libpam_misc.so.0.82.1 | libpam0g | 1.5.3-5ubuntu5.7 |
| usr/lib/x86_64-linux-gnu/libpam.so.0 | /usr/lib/x86_64-linux-gnu/libpam.so.0 | libpam0g | 1.5.3-5ubuntu5.7 |
| usr/lib/x86_64-linux-gnu/libpam.so.0.85.1 | /usr/lib/x86_64-linux-gnu/libpam.so.0.85.1 | libpam0g | 1.5.3-5ubuntu5.7 |
| usr/lib/x86_64-linux-gnu/libpam_misc.so.0 | /usr/lib/x86_64-linux-gnu/libpam_misc.so.0 | libpam0g | 1.5.3-5ubuntu5.7 |
| usr/lib/x86_64-linux-gnu/libpam_misc.so.0.82.1 | /usr/lib/x86_64-linux-gnu/libpam_misc.so.0.82.1 | libpam0g | 1.5.3-5ubuntu5.7 |
| lib/x86_64-linux-gnu/libpcre2-8.so.0 | /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0.11.2 | libpcre2-8-0 | 10.42-4ubuntu2.2 |
| lib/x86_64-linux-gnu/libpcre2-8.so.0.11.2 | /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0.11.2 | libpcre2-8-0 | 10.42-4ubuntu2.2 |
| usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 | /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 | libpcre2-8-0 | 10.42-4ubuntu2.2 |
| usr/lib/x86_64-linux-gnu/libpcre2-8.so.0.11.2 | /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0.11.2 | libpcre2-8-0 | 10.42-4ubuntu2.2 |
| lib/x86_64-linux-gnu/libproc2.so.0 | /usr/lib/x86_64-linux-gnu/libproc2.so.0.0.2 | libproc2-0 | 2:4.0.4-4ubuntu3.3 |
| lib/x86_64-linux-gnu/libproc2.so.0.0.2 | /usr/lib/x86_64-linux-gnu/libproc2.so.0.0.2 | libproc2-0 | 2:4.0.4-4ubuntu3.3 |
| usr/lib/x86_64-linux-gnu/libproc2.so.0 | /usr/lib/x86_64-linux-gnu/libproc2.so.0 | libproc2-0 | 2:4.0.4-4ubuntu3.3 |
| usr/lib/x86_64-linux-gnu/libproc2.so.0.0.2 | /usr/lib/x86_64-linux-gnu/libproc2.so.0.0.2 | libproc2-0 | 2:4.0.4-4ubuntu3.3 |
| usr/lib/python3.12/config-3.12-x86_64-linux-gnu/python.o | /usr/lib/python3.12/config-3.12-x86_64-linux-gnu/python.o | libpython3.12-dev | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_hashlib.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_hashlib.cpython-312-x86_64-linux-gnu.so | libpython3.12-minimal | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_ssl.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_ssl.cpython-312-x86_64-linux-gnu.so | libpython3.12-minimal | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_asyncio.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_asyncio.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_bz2.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_bz2.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_codecs_cn.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_codecs_cn.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_codecs_hk.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_codecs_hk.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_codecs_iso2022.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_codecs_iso2022.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_codecs_jp.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_codecs_jp.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_codecs_kr.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_codecs_kr.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_codecs_tw.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_codecs_tw.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_contextvars.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_contextvars.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_crypt.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_crypt.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_ctypes.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_ctypes.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_ctypes_test.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_ctypes_test.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_curses.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_curses.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_curses_panel.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_curses_panel.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_dbm.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_dbm.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_decimal.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_decimal.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_json.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_json.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_lsprof.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_lsprof.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_lzma.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_lzma.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_multibytecodec.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_multibytecodec.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_multiprocessing.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_multiprocessing.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_posixshmem.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_posixshmem.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_queue.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_queue.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_sqlite3.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_sqlite3.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_testbuffer.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_testbuffer.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_testcapi.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_testcapi.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_testclinic.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_testclinic.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_testimportmultiple.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_testimportmultiple.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_testinternalcapi.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_testinternalcapi.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_testmultiphase.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_testmultiphase.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_testsinglephase.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_testsinglephase.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_xxinterpchannels.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_xxinterpchannels.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_xxsubinterpreters.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_xxsubinterpreters.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_xxtestfuzz.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_xxtestfuzz.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/_zoneinfo.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_zoneinfo.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/audioop.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/audioop.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/mmap.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/mmap.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/ossaudiodev.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/ossaudiodev.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/readline.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/readline.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/resource.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/resource.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/termios.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/termios.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/xxlimited.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/xxlimited.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/xxlimited_35.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/xxlimited_35.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/lib-dynload/xxsubtype.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/xxsubtype.cpython-312-x86_64-linux-gnu.so | libpython3.12-stdlib | 3.12.3-1ubuntu0.17 |
| usr/lib/python3.12/config-3.12-x86_64-linux-gnu/libpython3.12.so | /usr/lib/python3.12/config-3.12-x86_64-linux-gnu/libpython3.12.so | libpython3.12t64 | 3.12.3-1ubuntu0.17 |
| lib/x86_64-linux-gnu/libseccomp.so.2 | /usr/lib/x86_64-linux-gnu/libseccomp.so.2.5.5 | libseccomp2 | 2.5.5-1ubuntu3.1 |
| lib/x86_64-linux-gnu/libseccomp.so.2.5.5 | /usr/lib/x86_64-linux-gnu/libseccomp.so.2.5.5 | libseccomp2 | 2.5.5-1ubuntu3.1 |
| usr/lib/x86_64-linux-gnu/libseccomp.so.2 | /usr/lib/x86_64-linux-gnu/libseccomp.so.2 | libseccomp2 | 2.5.5-1ubuntu3.1 |
| usr/lib/x86_64-linux-gnu/libseccomp.so.2.5.5 | /usr/lib/x86_64-linux-gnu/libseccomp.so.2.5.5 | libseccomp2 | 2.5.5-1ubuntu3.1 |
| lib/x86_64-linux-gnu/libselinux.so.1 | /usr/lib/x86_64-linux-gnu/libselinux.so.1 | libselinux1 | 3.5-2ubuntu2.1 |
| usr/lib/x86_64-linux-gnu/libselinux.so.1 | /usr/lib/x86_64-linux-gnu/libselinux.so.1 | libselinux1 | 3.5-2ubuntu2.1 |
| lib/x86_64-linux-gnu/libsmartcols.so.1 | /usr/lib/x86_64-linux-gnu/libsmartcols.so.1.1.0 | libsmartcols1 | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libsmartcols.so.1.1.0 | /usr/lib/x86_64-linux-gnu/libsmartcols.so.1.1.0 | libsmartcols1 | 2.39.3-9ubuntu6.6 |
| usr/lib/x86_64-linux-gnu/libsmartcols.so.1 | /usr/lib/x86_64-linux-gnu/libsmartcols.so.1 | libsmartcols1 | 2.39.3-9ubuntu6.6 |
| usr/lib/x86_64-linux-gnu/libsmartcols.so.1.1.0 | /usr/lib/x86_64-linux-gnu/libsmartcols.so.1.1.0 | libsmartcols1 | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libcrypto.so.3 | /usr/lib/x86_64-linux-gnu/libcrypto.so.3 | libssl3t64 | 3.0.13-0ubuntu3.16 |
| lib/x86_64-linux-gnu/libssl.so.3 | /usr/lib/x86_64-linux-gnu/libssl.so.3 | libssl3t64 | 3.0.13-0ubuntu3.16 |
| usr/lib/x86_64-linux-gnu/libcrypto.so.3 | /usr/lib/x86_64-linux-gnu/libcrypto.so.3 | libssl3t64 | 3.0.13-0ubuntu3.16 |
| usr/lib/x86_64-linux-gnu/libssl.so.3 | /usr/lib/x86_64-linux-gnu/libssl.so.3 | libssl3t64 | 3.0.13-0ubuntu3.16 |
| usr/lib/x86_64-linux-gnu/systemd/libsystemd-core-255.so | /usr/lib/x86_64-linux-gnu/systemd/libsystemd-core-255.so | libsystemd-shared | 255.4-1ubuntu8.18 |
| usr/lib/x86_64-linux-gnu/systemd/libsystemd-shared-255.so | /usr/lib/x86_64-linux-gnu/systemd/libsystemd-shared-255.so | libsystemd-shared | 255.4-1ubuntu8.18 |
| lib/x86_64-linux-gnu/libsystemd.so.0 | /usr/lib/x86_64-linux-gnu/libsystemd.so.0.38.0 | libsystemd0 | 255.4-1ubuntu8.18 |
| lib/x86_64-linux-gnu/libsystemd.so.0.38.0 | /usr/lib/x86_64-linux-gnu/libsystemd.so.0.38.0 | libsystemd0 | 255.4-1ubuntu8.18 |
| usr/lib/x86_64-linux-gnu/libsystemd.so.0 | /usr/lib/x86_64-linux-gnu/libsystemd.so.0 | libsystemd0 | 255.4-1ubuntu8.18 |
| usr/lib/x86_64-linux-gnu/libsystemd.so.0.38.0 | /usr/lib/x86_64-linux-gnu/libsystemd.so.0.38.0 | libsystemd0 | 255.4-1ubuntu8.18 |
| lib/x86_64-linux-gnu/libtinfo.so.6 | /usr/lib/x86_64-linux-gnu/libtinfo.so.6.4 | libtinfo6 | 6.4+20240113-1ubuntu2.2 |
| lib/x86_64-linux-gnu/libtinfo.so.6.4 | /usr/lib/x86_64-linux-gnu/libtinfo.so.6.4 | libtinfo6 | 6.4+20240113-1ubuntu2.2 |
| usr/lib/x86_64-linux-gnu/libtinfo.so.6 | /usr/lib/x86_64-linux-gnu/libtinfo.so.6 | libtinfo6 | 6.4+20240113-1ubuntu2.2 |
| usr/lib/x86_64-linux-gnu/libtinfo.so.6.4 | /usr/lib/x86_64-linux-gnu/libtinfo.so.6.4 | libtinfo6 | 6.4+20240113-1ubuntu2.2 |
| lib/x86_64-linux-gnu/libudev.so.1 | /usr/lib/x86_64-linux-gnu/libudev.so.1.7.8 | libudev1 | 255.4-1ubuntu8.18 |
| lib/x86_64-linux-gnu/libudev.so.1.7.8 | /usr/lib/x86_64-linux-gnu/libudev.so.1.7.8 | libudev1 | 255.4-1ubuntu8.18 |
| usr/lib/x86_64-linux-gnu/libudev.so.1 | /usr/lib/x86_64-linux-gnu/libudev.so.1 | libudev1 | 255.4-1ubuntu8.18 |
| usr/lib/x86_64-linux-gnu/libudev.so.1.7.8 | /usr/lib/x86_64-linux-gnu/libudev.so.1.7.8 | libudev1 | 255.4-1ubuntu8.18 |
| lib/x86_64-linux-gnu/libuuid.so.1 | /usr/lib/x86_64-linux-gnu/libuuid.so.1.3.0 | libuuid1 | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libuuid.so.1.3.0 | /usr/lib/x86_64-linux-gnu/libuuid.so.1.3.0 | libuuid1 | 2.39.3-9ubuntu6.6 |
| usr/lib/x86_64-linux-gnu/libuuid.so.1 | /usr/lib/x86_64-linux-gnu/libuuid.so.1 | libuuid1 | 2.39.3-9ubuntu6.6 |
| usr/lib/x86_64-linux-gnu/libuuid.so.1.3.0 | /usr/lib/x86_64-linux-gnu/libuuid.so.1.3.0 | libuuid1 | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libyaml-0.so.2 | /usr/lib/x86_64-linux-gnu/libyaml-0.so.2.0.9 | libyaml-0-2 | 0.2.5-1build1 |
| lib/x86_64-linux-gnu/libyaml-0.so.2.0.9 | /usr/lib/x86_64-linux-gnu/libyaml-0.so.2.0.9 | libyaml-0-2 | 0.2.5-1build1 |
| usr/lib/x86_64-linux-gnu/libyaml-0.so.2 | /usr/lib/x86_64-linux-gnu/libyaml-0.so.2 | libyaml-0-2 | 0.2.5-1build1 |
| usr/lib/x86_64-linux-gnu/libyaml-0.so.2.0.9 | /usr/lib/x86_64-linux-gnu/libyaml-0.so.2.0.9 | libyaml-0-2 | 0.2.5-1build1 |
| lib/x86_64-linux-gnu/libzstd.so.1 | /usr/lib/x86_64-linux-gnu/libzstd.so.1.5.5 | libzstd1 | 1.5.5+dfsg2-2build1.1 |
| lib/x86_64-linux-gnu/libzstd.so.1.5.5 | /usr/lib/x86_64-linux-gnu/libzstd.so.1.5.5 | libzstd1 | 1.5.5+dfsg2-2build1.1 |
| usr/lib/x86_64-linux-gnu/libzstd.so.1 | /usr/lib/x86_64-linux-gnu/libzstd.so.1 | libzstd1 | 1.5.5+dfsg2-2build1.1 |
| usr/lib/x86_64-linux-gnu/libzstd.so.1.5.5 | /usr/lib/x86_64-linux-gnu/libzstd.so.1.5.5 | libzstd1 | 1.5.5+dfsg2-2build1.1 |
| bin/login | /usr/bin/login | login | 1:4.13+dfsg1-4ubuntu3.2 |
| usr/bin/login | /usr/bin/login | login | 1:4.13+dfsg1-4ubuntu3.2 |
| bin/mount | /usr/bin/mount | mount | 2.39.3-9ubuntu6.6 |
| bin/umount | /usr/bin/umount | mount | 2.39.3-9ubuntu6.6 |
| bin/clear | /usr/bin/clear | ncurses-bin | 6.4+20240113-1ubuntu2.2 |
| usr/libexec/netplan/generate | /usr/libexec/netplan/generate | netplan-generator | 1.1.2-8ubuntu1~24.04.2 |
| bin/free | /usr/bin/free | procps | 2:4.0.4-4ubuntu3.3 |
| bin/kill | /usr/bin/kill | procps | 2:4.0.4-4ubuntu3.3 |
| bin/ps | /usr/bin/ps | procps | 2:4.0.4-4ubuntu3.3 |
| usr/bin/free | /usr/bin/free | procps | 2:4.0.4-4ubuntu3.3 |
| usr/bin/ps | /usr/bin/ps | procps | 2:4.0.4-4ubuntu3.3 |
| usr/lib/python3.12/lib-dynload/_gdbm.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3.12/lib-dynload/_gdbm.cpython-312-x86_64-linux-gnu.so | python3-gdbm | 3.12.3-0ubuntu1 |
| usr/bin/python3 | /usr/bin/python3 | python3-minimal | 3.12.3-0ubuntu2.1 |
| usr/lib/python3/dist-packages/yaml/_yaml.cpython-312-x86_64-linux-gnu.so | /usr/lib/python3/dist-packages/yaml/_yaml.cpython-312-x86_64-linux-gnu.so | python3-yaml | 6.0.1-2build2 |
| bin/python3 | /usr/bin/python3.12 | python3.12-minimal | 3.12.3-1ubuntu0.17 |
| usr/bin/python3.12 | /usr/bin/python3.12 | python3.12-minimal | 3.12.3-1ubuntu0.17 |
| bin/sed | /usr/bin/sed | sed | 4.9-2ubuntu0.24.04.1 |
| bin/systemctl | /usr/bin/systemctl | systemd | 255.4-1ubuntu8.18 |
| sbin/init | /usr/lib/systemd/systemd | systemd | 255.4-1ubuntu8.18 |
| sbin/poweroff | /usr/bin/systemctl | systemd | 255.4-1ubuntu8.18 |
| sbin/reboot | /usr/bin/systemctl | systemd | 255.4-1ubuntu8.18 |
| usr/bin/systemctl | /usr/bin/systemctl | systemd | 255.4-1ubuntu8.18 |
| usr/bin/systemd-analyze | /usr/bin/systemd-analyze | systemd | 255.4-1ubuntu8.18 |
| usr/bin/systemd-cryptsetup | /usr/bin/systemd-cryptsetup | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/system-generators/systemd-fstab-generator | /usr/lib/systemd/system-generators/systemd-fstab-generator | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/system-generators/systemd-getty-generator | /usr/lib/systemd/system-generators/systemd-getty-generator | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd | /usr/lib/systemd/systemd | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-backlight | /usr/lib/systemd/systemd-backlight | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-battery-check | /usr/lib/systemd/systemd-battery-check | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-binfmt | /usr/lib/systemd/systemd-binfmt | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-boot-check-no-failures | /usr/lib/systemd/systemd-boot-check-no-failures | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-bsod | /usr/lib/systemd/systemd-bsod | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-cgroups-agent | /usr/lib/systemd/systemd-cgroups-agent | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-cryptsetup | /usr/lib/systemd/systemd-cryptsetup | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-executor | /usr/lib/systemd/systemd-executor | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-fsck | /usr/lib/systemd/systemd-fsck | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-fsckd | /usr/lib/systemd/systemd-fsckd | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-growfs | /usr/lib/systemd/systemd-growfs | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-hibernate-resume | /usr/lib/systemd/systemd-hibernate-resume | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-hostnamed | /usr/lib/systemd/systemd-hostnamed | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-initctl | /usr/lib/systemd/systemd-initctl | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-integritysetup | /usr/lib/systemd/systemd-integritysetup | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-journald | /usr/lib/systemd/systemd-journald | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-localed | /usr/lib/systemd/systemd-localed | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-logind | /usr/lib/systemd/systemd-logind | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-makefs | /usr/lib/systemd/systemd-makefs | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-measure | /usr/lib/systemd/systemd-measure | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-modules-load | /usr/lib/systemd/systemd-modules-load | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-network-generator | /usr/lib/systemd/systemd-network-generator | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-networkd | /usr/lib/systemd/systemd-networkd | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-networkd-wait-online | /usr/lib/systemd/systemd-networkd-wait-online | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-pcrextend | /usr/lib/systemd/systemd-pcrextend | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-pcrlock | /usr/lib/systemd/systemd-pcrlock | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-pstore | /usr/lib/systemd/systemd-pstore | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-quotacheck | /usr/lib/systemd/systemd-quotacheck | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-random-seed | /usr/lib/systemd/systemd-random-seed | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-remount-fs | /usr/lib/systemd/systemd-remount-fs | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-reply-password | /usr/lib/systemd/systemd-reply-password | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-rfkill | /usr/lib/systemd/systemd-rfkill | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-shutdown | /usr/lib/systemd/systemd-shutdown | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-sleep | /usr/lib/systemd/systemd-sleep | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-socket-proxyd | /usr/lib/systemd/systemd-socket-proxyd | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-storagetm | /usr/lib/systemd/systemd-storagetm | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-sulogin-shell | /usr/lib/systemd/systemd-sulogin-shell | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-sysctl | /usr/lib/systemd/systemd-sysctl | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-sysroot-fstab-check | /usr/lib/systemd/systemd-sysroot-fstab-check | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-sysupdate | /usr/lib/systemd/systemd-sysupdate | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-time-wait-sync | /usr/lib/systemd/systemd-time-wait-sync | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-timedated | /usr/lib/systemd/systemd-timedated | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-tpm2-setup | /usr/lib/systemd/systemd-tpm2-setup | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-update-done | /usr/lib/systemd/systemd-update-done | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-update-utmp | /usr/lib/systemd/systemd-update-utmp | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-user-runtime-dir | /usr/lib/systemd/systemd-user-runtime-dir | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-user-sessions | /usr/lib/systemd/systemd-user-sessions | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-veritysetup | /usr/lib/systemd/systemd-veritysetup | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-volatile-root | /usr/lib/systemd/systemd-volatile-root | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-xdg-autostart-condition | /usr/lib/systemd/systemd-xdg-autostart-condition | systemd | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-resolved | /usr/lib/systemd/systemd-resolved | systemd-resolved | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-timesyncd | /usr/lib/systemd/systemd-timesyncd | systemd-timesyncd | 255.4-1ubuntu8.18 |
| usr/bin/udevadm | /usr/bin/udevadm | udev | 255.4-1ubuntu8.18 |
| usr/lib/systemd/systemd-udevd | /usr/lib/systemd/systemd-udevd | udev | 255.4-1ubuntu8.18 |
| bin/findmnt | /usr/bin/findmnt | util-linux | 2.39.3-9ubuntu6.6 |
| bin/lsblk | /usr/bin/lsblk | util-linux | 2.39.3-9ubuntu6.6 |
| sbin/agetty | /usr/sbin/agetty | util-linux | 2.39.3-9ubuntu6.6 |
| usr/bin/findmnt | /usr/bin/findmnt | util-linux | 2.39.3-9ubuntu6.6 |
| usr/bin/lsblk | /usr/bin/lsblk | util-linux | 2.39.3-9ubuntu6.6 |
| usr/sbin/agetty | /usr/sbin/agetty | util-linux | 2.39.3-9ubuntu6.6 |
| lib/x86_64-linux-gnu/libz.so.1 | /usr/lib/x86_64-linux-gnu/libz.so.1.3 | zlib1g | 1:1.3.dfsg-3.1ubuntu2.3 |
| lib/x86_64-linux-gnu/libz.so.1.3 | /usr/lib/x86_64-linux-gnu/libz.so.1.3 | zlib1g | 1:1.3.dfsg-3.1ubuntu2.3 |
| usr/lib/x86_64-linux-gnu/libz.so.1 | /usr/lib/x86_64-linux-gnu/libz.so.1 | zlib1g | 1:1.3.dfsg-3.1ubuntu2.3 |
| usr/lib/x86_64-linux-gnu/libz.so.1.3 | /usr/lib/x86_64-linux-gnu/libz.so.1.3 | zlib1g | 1:1.3.dfsg-3.1ubuntu2.3 |
