#!/usr/bin/env sh

set -e

PATH=$PATH:$HOME/.local/bin/

make migrate
hivemind
