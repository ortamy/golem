# Установка и запуск Docker-коробки «Алефи»

## Требования

- Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop/) с Linux-контейнерами.
- Linux/macOS: Docker Engine и Docker Compose plugin.
- Git для клонирования проекта.

## Docker Desktop на Windows

1. Откройте официальный сайт: <https://www.docker.com/products/docker-desktop/>.
2. Скачайте и установите Docker Desktop for Windows. Оставьте рекомендованные параметры, включая WSL 2.
3. Перезагрузите компьютер, запустите Docker Desktop и дождитесь сообщения `Docker Desktop is running`.
4. В PowerShell проверьте установку:

```powershell
docker --version
docker compose version
```

## Подготовка и запуск

Клонируйте проект и перейдите в папку, где находится `docker-compose.yml`:

```powershell
git clone https://github.com/ortamy/alephy.git
cd alephy
```

Создайте ключ и секрет LUKS, если их ещё нет:

```powershell
New-Item -ItemType Directory -Force .alephy-secrets
ssh-keygen -t ed25519 -f .alephy-secrets/alephy_ed25519 -N ""
Copy-Item .alephy-secrets/alephy_ed25519.pub .alephy-secrets/authorized_keys
openssl rand -base64 48 | Out-File -Encoding ascii .alephy-secrets/luks_passphrase
```

Не передавайте `.alephy-secrets/` и не добавляйте его в Git.

Запустите коробку:

```powershell
docker compose up -d --build
```

Первый build обычно занимает несколько минут: скачиваются Ubuntu, Python, Node.js и пакеты. Проверить состояние и логи:

```powershell
docker compose ps
docker compose logs -f alephy
```

`Ctrl+C` прекращает просмотр логов, но не останавливает контейнер.

## Подключение по SSH

```powershell
ssh -i .alephy-secrets/alephy_ed25519 -p 2222 alephy@127.0.0.1
```

При первом подключении введите `yes` для подтверждения fingerprint. Парольный вход отключён. Выйти и вернуться позже:

```text
exit
```

Затем снова выполните SSH-команду выше.

## Работа внутри

При первом запуске entrypoint автоматически создаёт LUKS2-том, открывает его и монтирует в `/workspace/secure`. Проверить его:

```bash
cryptsetup status alephy-secure
mount | grep /workspace/secure
df -h /workspace/secure
```

Вручную открыть том (обычно не требуется; выполняется от root):

```bash
cryptsetup open /var/lib/alephy/secure.luks alephy-secure
mount /dev/mapper/alephy-secure /workspace/secure
```

В образе уже есть Python 3.12, Node.js, Git, `vim`, `curl`, `openssl` и `cryptsetup`. Дополнительные инструменты устанавливаются так:

```bash
sudo apt update
sudo apt install -y имя-пакета
```

Сохраняйте данные в `/workspace/secure`: это volume `alephy-luks`, который сохраняется после `docker compose down`. Исходники проекта доступны только для чтения в `/workspace/project`.

## Остановка и очистка

Остановить контейнер, сохранив volume:

```powershell
docker compose down
```

Удалить также зашифрованный volume:

```powershell
docker compose down -v
```

Удалить все неиспользуемые образы и контейнеры Docker:

```powershell
docker system prune -a
```

Последняя команда действует на весь Docker Desktop, а не только на «Алефи».

## Перенос образа на флешке

Образ имеет имя `alephy:latest`. Сохранить его в TAR-файл:

```powershell
docker save -o alephy-image.tar alephy:latest
```

На другом компьютере загрузить образ:

```powershell
docker load -i alephy-image.tar
```

Для запуска также перенесите `docker-compose.yml`, `Dockerfile`, папку `docker/` и секреты:

```text
.alephy-secrets/authorized_keys
.alephy-secrets/luks_passphrase
```

Затем выполните в корне проекта:

```powershell
docker compose up -d
```

TAR-файл не содержит SSH-ключей, пароль LUKS и данные volume `alephy-luks`.