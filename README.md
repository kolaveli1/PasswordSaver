# Password Manager

A **local password manager** built with **Python** and **PyQt6** that securely stores your passwords using **AES-256 encryption**.

## Features
- **Secure Encryption**: Uses **AES-256** via the `cryptography` library to encrypt and store passwords.
- **Organized Storage**: Categorize passwords into groups (e.g., "Social Media", "Banking").
- **Easy Access**: Quickly copy usernames and passwords with one click.
- **Edit & Delete**: Update or remove passwords directly from the interface.
- **Local Storage**: Passwords are stored locally in an **SQLite database** (not cloud-based).
- **Master Key Protection**: Uses a securely stored encryption key (`secret.key`).


