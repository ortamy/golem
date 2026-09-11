# Изолированная Свива «Алефи»

Контейнер запускается через отдельную внутреннюю Docker-сеть. Из основной ОС наружу опубликован только SSH на `127.0.0.1:2222`; сетевые соединения между контейнером и внешним миром отключены (`internal: true`). Исходники доступны внутри как `/workspace/project`, зашифрованное рабочее хранилище — как `/workspace/secure`.

## Первый запуск

В Linux/macOS или в WSL из корня проекта:

```sh
mkdir -p .alephy-secrets
ssh-keygen -t ed25519 -f .alephy-secrets/alephy_ed25519 -N ''
cp .alephy-secrets/alephy_ed25519.pub .alephy-secrets/authorized_keys
openssl rand -base64 48 > .alephy-secrets/luks_passphrase
chmod 700 .alephy-secrets
chmod 600 .alephy-secrets/alephy_ed25519 .alephy-secrets/luks_passphrase
docker compose up -d --build
```

Подключение:

```sh
ssh -i .alephy-secrets/alephy_ed25519 -p 2222 alephy@127.0.0.1
```

Размер LUKS-тома по умолчанию — 1 ГБ. До первого запуска его можно изменить: `ALEPHY_LUKS_SIZE=10G docker compose up -d`.

## Ограничения

- Для LUKS Docker получает `SYS_ADMIN`, `MKNOD`, `/dev/loop-control` и `apparmor=unconfined`. Это необходимый минимум для монтирования зашифрованного loop-тома; такой контейнер нельзя считать полностью недоверенным sandbox’ом ядра.
- Пароль LUKS и SSH-ключ не попадают в образ: они передаются как Compose secrets. Каталог `.alephy-secrets/` не следует коммитить.
- LUKS защищает данные при извлечении тома/файла, но открытый том доступен процессам контейнера во время работы.
- На Docker Desktop для Windows LUKS работает внутри Linux VM Docker Desktop; `SYS_ADMIN` относится к этой VM, не даёт контейнеру прямого доступа к ядру Windows.