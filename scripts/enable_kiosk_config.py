#!/usr/bin/env python3
import subprocess

config_path = "/home/manas/lazy-build/output/.config"
symbols = [
    "BR2_PACKAGE_MESA3D=y",
    "BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_SWRAST=y",
    "BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_VIRGL=y",
    "BR2_PACKAGE_MESA3D_OPENGL_EGL=y",
    "BR2_PACKAGE_MESA3D_OPENGL_ES=y",
    "BR2_PACKAGE_LIBGBM=y",
    "BR2_PACKAGE_WAYLAND=y",
    "BR2_PACKAGE_WAYLAND_PROTOCOLS=y",
    "BR2_PACKAGE_LIBXKBCOMMON=y",
    "BR2_PACKAGE_WLROOTS=y",
    "BR2_PACKAGE_CAGE=y",
    "BR2_PACKAGE_WPEBACKEND_FDO=y",
    "BR2_PACKAGE_WPEWEBKIT=y",
    "BR2_PACKAGE_COG=y",
    "BR2_PACKAGE_COG_PLATFORM_FDO=y",
    'BR2_PACKAGE_COG_PROGRAMS_HOME_URI="http://127.0.0.1:8765"',
]

with open(config_path, "a") as f:
    f.write("\n# Kiosk packages\n")
    for s in symbols:
        f.write(s + "\n")

print("Appended kiosk symbols to", config_path)
cmd = "export PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' && make -C /mnt/c/Users/len/OS/build/buildroot-2024.02 O=/home/manas/lazy-build/output BR2_EXTERNAL=/mnt/c/Users/len/OS/lazy-br2/ olddefconfig"
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("Returncode:", res.returncode)
print("Stdout:", res.stdout[-300:] if res.stdout else "")
print("Stderr:", res.stderr[-300:] if res.stderr else "")
