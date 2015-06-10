#!/bin/bash
set -e

help() {
    cat <<EOF
Usage: $(basename $0) SUITE TARGET_DIR [MIRROR]

    A script to download and install just enough packages to create a minimal
    Debian / Ubuntu chroot environment suitable for local braid testing.

    The OS can be booted using eg sudo systemd-nspawn -boot

    SUITE: The version of Debian / Ubuntu to install. One of:
           $(ls -1 /usr/share/debootstrap/scripts/ | xargs)

    TARGET_DIR: The absolute or relative path to a directory into
                which the packages should be installed.
                (eg /tmp/ubuntu-image)

    MIRROR: The url of a mirror from which packages will be downloaded.
            Default: http://archive.ubuntu.com/ubuntu

    Options
    -h | --help: Print this help message
    -f | --force-download: Force packages to be downloaded rather than read from a cache file.
${1-}
EOF
}

FORCE_DOWNLOAD="FALSE"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h | --help)
            help
            exit 0
            ;;
        -f | --force-download)
            FORCE_DOWNLOAD="TRUE"
            shift
            break
            ;;
        --)
            shift
            break
            ;;
        -*)
            help "ERROR: Unknown option: $1" >&2
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

SUITE=${1:?"Error: Missing parameter 1:SUITE"}
TARGET_DIR=${2:?"Error: Missing parameter 2:TARGET_DIR"}
MIRROR=${3:-"http://archive.ubuntu.com/ubuntu"}
PACKAGE_CACHE_PATH="${HOME}/.cache/braid/debootstrapper_package_cache.tgz"

mkdir -p "$(dirname $PACKAGE_CACHE_PATH)"

debootstrap_args="--no-check-gpg --arch=amd64 --include=openssh-server,language-pack-en,aptitude"

if [[ ! -e "$PACKAGE_CACHE_PATH" || "$FORCE_DOWNLOAD" == "TRUE" ]]; then
    sudo debootstrap --make-tarball="$PACKAGE_CACHE_PATH" $debootstrap_args $SUITE $TARGET_DIR $MIRROR
fi
sudo debootstrap --unpack-tarball="$PACKAGE_CACHE_PATH" $debootstrap_args $SUITE $TARGET_DIR $MIRROR

cd "$TARGET_DIR"
# Add the local user SSH key to the root user
sudo mkdir root/.ssh
sudo tee root/.ssh/authorized_keys < ~/.ssh/id_rsa.pub
# systemd-nspawn expects this file to be present
sudo touch etc/os-release
# On Ubuntu resolv.conf is a symlink, but that prevents systemd-nspawn from bind
# mounting it to the resolv.conf of the host.
sudo rm etc/resolv.conf
sudo touch etc/resolv.conf
# Enable the universe and multiverse repositories
echo "deb $MIRROR $SUITE main universe multiverse" | sudo tee etc/apt/sources.list
# Set the system locale
# https://help.ubuntu.com/community/Locale
sudo chroot . update-locale LANG=en_US.UTF-8
