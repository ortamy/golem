#!/bin/sh
set -eu

readonly LUKS_IMAGE=/var/lib/alephy/secure.luks
readonly MAPPER_NAME=alephy-secure
readonly MOUNT_POINT=/workspace/secure
readonly KEY_FILE=/home/alephy/.ssh/authorized_keys

fail() { echo "alephy: $*" >&2; exit 1; }

[ -s /run/secrets/ssh_authorized_keys ] || fail "SSH public key secret is empty"
[ -s /run/secrets/luks_passphrase ] || fail "LUKS passphrase secret is empty"

install -d -m 0700 /home/alephy/.ssh
install -m 0600 /run/secrets/ssh_authorized_keys "$KEY_FILE"
chown -R alephy:alephy /home/alephy/.ssh

# Create and initialise the encrypted payload only on the first start.
if [ ! -e "$LUKS_IMAGE" ]; then
    truncate -s "${ALEPHY_LUKS_SIZE:-1G}" "$LUKS_IMAGE"
    chmod 0600 "$LUKS_IMAGE"
    printf '%s' "$(cat /run/secrets/luks_passphrase)" | cryptsetup luksFormat \
        --batch-mode --type luks2 --key-file=- "$LUKS_IMAGE"
fi

if ! cryptsetup status "$MAPPER_NAME" >/dev/null 2>&1; then
    printf '%s' "$(cat /run/secrets/luks_passphrase)" | cryptsetup open \
        --type luks --key-file=- "$LUKS_IMAGE" "$MAPPER_NAME"
fi

if ! blkid "/dev/mapper/$MAPPER_NAME" >/dev/null 2>&1; then
    mkfs.ext4 -L alephy-secure "/dev/mapper/$MAPPER_NAME"
fi

install -d -o alephy -g alephy "$MOUNT_POINT"
mountpoint -q "$MOUNT_POINT" || mount "/dev/mapper/$MAPPER_NAME" "$MOUNT_POINT"
chown alephy:alephy "$MOUNT_POINT"

exec /usr/sbin/sshd -D -e