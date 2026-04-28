# sshmate

A simple terminal tool for managing SSH connections. Instead of remembering or typing out every host, you just pick from a list and it connects.

<img width="954" height="523" alt="image" src="https://github.com/user-attachments/assets/14a2f62d-6317-4c6c-9cab-5acad81e030c" />

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

Your connections are saved in `~/.config/sshmate/connections.json` 

## Requirements

- Python 3.8+
- An SSH client
