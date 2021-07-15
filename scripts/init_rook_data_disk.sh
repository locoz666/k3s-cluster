#!/bin/bash

DISK="/dev/${1}"
ROOK_DATA_PATH="/var/lib/rook"

function mount_disk() {
  echo "挂载${DISK}至${ROOK_DATA_PATH}"
  mkdir -p ${ROOK_DATA_PATH}
  mount "${DISK}" ${ROOK_DATA_PATH}
  df -h | grep ${ROOK_DATA_PATH}
}

function set_auto_mount_disk() {
  echo "设置自动挂载${DISK}至${ROOK_DATA_PATH}"
  DISK_UUID=$(blkid "${DISK}" | sed 's/.* UUID="\(.*\)" TYPE.*/\1/g')
  echo "/dev/disk/by-uuid/${DISK_UUID} ${ROOK_DATA_PATH} xfs defaults 0 0" >> /etc/fstab
}

mount_disk
set_auto_mount_disk
