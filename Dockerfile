FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl cryptsetup git openssh-server openssl sudo vim \
        python3.12 python3.12-venv python3-pip util-linux \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && useradd --create-home --shell /bin/bash --uid 1000 alephy \
    && mkdir -p /run/sshd /workspace /workspace/secure /var/lib/alephy \
    && chown -R alephy:alephy /workspace /var/lib/alephy \
    && rm -rf /var/lib/apt/lists/*

COPY docker/sshd_config /etc/ssh/sshd_config
COPY docker/entrypoint.sh /usr/local/sbin/alephy-entrypoint
RUN chmod 0755 /usr/local/sbin/alephy-entrypoint \
    && ssh-keygen -A

WORKDIR /workspace
EXPOSE 22
VOLUME ["/var/lib/alephy"]

ENTRYPOINT ["/usr/local/sbin/alephy-entrypoint"]