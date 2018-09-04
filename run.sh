#!/usr/bin/env bash
docker run -d --rm -v $(pwd)/data:/app/data --name telegram_bot telegram_bot
