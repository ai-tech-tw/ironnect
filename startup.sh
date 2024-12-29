#!/bin/sh
# startup.sh - Start the application server
# SPDX-License-Identifier: MIT
# (c) Taiwan Web Technology Promotion Organization

if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi

if [ -z "$APP_HOST" ]; then
    APP_HOST="127.0.0.1"
fi

if [ -z "$APP_PORT" ]; then
    APP_PORT="8000"
fi

if [ -z "$APP_WORKERS" ]; then
    APP_WORKERS="6"
fi

gunicorn \
    --bind="$APP_HOST:$APP_PORT" \
    --workers="$APP_WORKERS" \
    "app:app"
