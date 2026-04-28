# sshmate

A simple terminal tool for managing SSH connections. Instead of remembering or typing out every host, you just pick from a list and it connects.

![screenshot](picture.png)

## Install

You need [pipx](https://pipx.pypa.io/stable/installation/) installed first, then:

```bash
pipx install git+https://github.com/yourusername/sshmate
```

## Usage

Just type `sshmate` anywhere in your terminal.

- Arrow keys to navigate
- `Enter` to connect
- `e` to edit a connection
- `d` to delete a connection
- `q` to quit

Your connections are saved in `~/.config/sshmate/connections.json` — not in the project folder, so nothing sensitive ends up on GitHub.

## Requirements

- Python 3.8+
- An SSH client (you already have one)
