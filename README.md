# Overview

This is a Discord chatbot that uses the Discord API to hold character contests in a server with **20,000+ users**. The bot schedules/organizes contests as well as facilitates/stores user submissions. This is done through a series of commands, dialogs, and a bunch of asynchronous Python code.

# Technologies Used
All of the code is written in **Python 3** and uses the `discord.py` library to access the Discord API. **PostgreSQL** through **PonyORM** is used to store and persist data. **Docker** is used to handle containerizing and deploying on a server (such as an AWS EC2 or Azure Linux machine).

# Installation

## Setup
Before installing, certain parameters need to be filled out. 

1. Update the `bot_owner` and `guild` fields in `settings.json` with your values (these are Discord's IDs)
2. Create a `.env` file with the fields provided in `.env.template`. Note that the database is PostgreSQL.

## Docker
A `Dockerfile` is provided to quickly create a Docker image. If you only need to build for your architecture, simply run:
```
docker build -t contest-bot:latest .
```
If you need to build for both `amd64` and `arm64` (e.g. you're using an M1 Mac), you will need a Docker repository to push to.
```
docker buildx create --use
docker buildx build --push --platform linux/amd64,linux/arm64 -t {Docker repo}:{tag} .
```
Once you have the image, simply use the following command to create a container:
```
docker run -d --env-file .env contest-bot:latest
```
