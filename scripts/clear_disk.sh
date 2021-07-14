#!/bin/bash

function clear_disk() {
  # Zap the disk to a fresh, usable state (zap-all is important, b/c MBR has to be clean)

  # You will have to run this step for all disks.
  sgdisk --zap-all $DISK

  # Clean hdds with dd
  dd if=/dev/zero of="$DISK" bs=1M count=100 oflag=direct,dsync

  # Clean disks such as ssd with blkdiscard instead of dd
  blkdiscard $DISK

  # Inform the OS of partition table changes
  partprobe $DISK
}

DISK="/dev/${1}"

echo "将清空${DISK}"

read -r -p "请确认是否进行操作 [Y/n] " input

case $input in
    [yY][eE][sS]|[yY])
    clear_disk
		;;

    [nN][oO]|[nN])
		exit 0
    ;;

    *)
		echo "输入错误"
		exit 1
		;;
esac
