![Main Foodgram workflow](https://github.com/vyalko/foodgram/actions/workflows/main.yml/badge.svg)
# Foodgram

## Описание

Foodgram — социальная сеть для публикации любимых рецептов.

## Основные параметры:

* Автоматизация деплоя: CI/CD
* GitHub Actions

## Стек

* Django 4.2.14
* djangorestframework  3.15.2
* pytest 6.2.4
* Python 3.9
* PyYAML 6.0
* JavaScript
* Nginx
* CI/CD

## Установка

1. Клонируйте репозиторий на свой компьютер:

```
git clone git@github.com:vyalko/foodgram.git
```
```
cd foodgram
```

2. Создайте файл .env. Пример находится в корневой директории .env.example

## Запуск проекта

1. Подключитесь к удаленному серверу.
```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
```
2. Cоздайте папку проекта foodgram и перейдите в неё:
```
mkdir foodgram
cd foodgram
```
3. Установите docker compose на сервер:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
4. Скопируйте в дирректорию проекта файлы docker-compose.production.yml и .env
```
scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
scp -i path_to_SSH/SSH_name .env username@server_ip:/home/username/foodgram/.env
```
5. Запустите docker compose в режиме демона:
```
sudo docker compose -f docker-compose.production.yml up -d
```
6. Выполните миграции, соберите статику бэкенда.
7. Отредактируйте конфиг Nginx на сервере, убедитесь в работоспособности и перезапустите Nginx.

## Настройка CI/CD

1. Файл workflow уже готов и находится в .github/workflows/main.yml
2. Заполните секреты в GitHub Actions.

## Проект доступен по адресу: https://bestfoodgram.duckdns.org/

Release
0.0.1

Date
August 17, 2024

Saraev Ivan
