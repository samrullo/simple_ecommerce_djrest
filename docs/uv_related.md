# How to pip-compile with uv

Run below command

```bash
uv pip compile requirements.in -o requirements.txt
```

to upgrade

```bash
uv pip compile --upgrade requirements.in -o requirements.txt
```

to add library to dependency and install simultaneously

```bash
uv add --find-links ./py_wheels python-dotenv
```