# Deck Input - Task 4: Immutable Filesystem, OverlayFS & Transactional Undo

## Slide Metadata
- **Slide Title**: Immutable Read-Only Root, OverlayFS & Btrfs Snapshots
- **Topic**: Storage Architecture, WIC Partitioning & Rule F7 Undo
- **Time Allocation**: 2 Minutes

---

## Slide Content & Bullets

### 1. Storage Layout (`lazy-disk.wks`)
- **Partition 1 (EFI Boot)**: 64 MB `vfat` partition containing systemd-boot and EFI binaries.
- **Partition 2 (Rootfs `/`)**: Highly compressed, immutable **SquashFS** image mounted strictly **read-only**.
- **Partition 3 (Data `/data`)**: Writable **Btrfs** volume managing user data, state, and transactional snapshots.

### 2. First-Boot OverlayFS Architecture (`lazy-first-boot.service`)
- On first boot, the system initializes Btrfs subvolumes:
  - `@home`: Persistent user documents and code.
  - `@snapshots`: COW snapshots captured prior to every mutating task.
  - `@etc_upper` & `@var_upper`: OverlayFS upper layers providing writable `/etc` and `/var` without modifying lower SquashFS root.

### 3. Rule F7 Transactional Undo in Action
- Before executing any mutating operation (`fs.write`, `fs.delete`, `code.run`):
  1. `lazy-tasks` creates a zero-copy Btrfs snapshot: `snap-<task_id>-base`.
  2. The broker executes the intent inside the working tree.
  3. If user clicks "Undo" or the task fails: the snapshot is instantly restored in sub-millisecond time.

---

## Speaker Talking Points
1. "How do you make an autonomous agent trustworthy? You give the operating system an immutable anchor and an instant undo button."
2. "The root filesystem is a compressed read-only SquashFS image. Even root cannot modify the underlying system binaries. Changes to `/etc` and `/var` reside in Btrfs-backed OverlayFS layers."
3. "Our benchmark proves that Btrfs subvolume snapshots take less than 15 milliseconds to capture and restore, enabling seamless undo for file deletions, edits, and code generation."

---

## Evidence & Verification References
- [yocto/meta-lazy/wic/lazy-disk.wks](file:///c:/Users/len/OS/yocto/meta-lazy/wic/lazy-disk.wks): WIC kickstart disk layout.
- [src/lazy/tasks/manager.py](file:///c:/Users/len/OS/src/lazy/tasks/manager.py): Transactional snapshot manager.
- [tests/results/M1.3.log](file:///c:/Users/len/OS/tests/results/M1.3.log): Snapshot creation, rollback, and undo verification tests.
- [tests/results/M5.3.log](file:///c:/Users/len/OS/tests/results/M5.3.log): QEMU boot test and OverlayFS isolation test.
