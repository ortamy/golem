#!/bin/sh
set -eu

readonly LUKS_IMAGE=/var/lib/golem/secure.luks
readonly MAPPER_NAME=golem-secure
readonly MOUNT_POINT=/workspace/secure
readonly KEY_FILE=/home/golem/.ssh/authorized_keys

fail() { echo "golem: $*" >&2; exit 1; }

[ -s /run/secrets/ssh_authorized_keys ] || fail "SSH public key secret is empty"
[ -s /run/secrets/luks_passphrase ] || fail "LUKS passphrase secret is empty"

install -d -m 0700 /home/golem/.ssh
install -m 0600 /run/secrets/ssh_authorized_keys "$KEY_FILE"
chown -R golem:golem /home/golem/.ssh

# Create and initialise the encrypted payload only on the first start.
if [ ! -e "$LUKS_IMAGE" ]; then
    truncate -s "${GOLEM_LUKS_SIZE:-1G}" "$LUKS_IMAGE"
    chmod 0600 "$LUKS_IMAGE"
    printf '%s' "$(cat /run/secrets/luks_passphrase)" | cryptsetup luksFormat \
        --batch-mode --type luks2 --key-file=- "$LUKS_IMAGE"
fi

if ! cryptsetup status "$MAPPER_NAME" >/dev/null 2>&1; then
    printf '%s' "$(cat /run/secrets/luks_passphrase)" | cryptsetup open \
        --type luks --key-file=- "$LUKS_IMAGE" "$MAPPER_NAME"
fi

if ! blkid "/dev/mapper/$MAPPER_NAME" >/dev/null 2>&1; then
    mkfs.ext4 -L golem-secure "/dev/mapper/$MAPPER_NAME"
fi

install -d -o golem -g golem "$MOUNT_POINT"
mountpoint -q "$MOUNT_POINT" || mount "/dev/mapper/$MAPPER_NAME" "$MOUNT_POINT"
chown golem:golem "$MOUNT_POINT"

exec /usr/sbin/sshd -D -e