#!/bin/bash
black ./backend
isort ./backend
flake8 ./backend
mypy ./backend