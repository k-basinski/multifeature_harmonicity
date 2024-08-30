#!/bin/zsh

git fetch --all
git reset --hard origin/main
git pull
git status