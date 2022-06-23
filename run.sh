#!/usr/bin/env sh

set -e

PATH=$PATH:$HOME/.poetry/bin/

make migrate
hivemind
