# Tools

Reserved for development utilities and supporting scripts — environment setup,
log collection, diagnostics. Run them from the repository root so imports and
relative paths resolve consistently.

This directory is currently empty. Environment setup lives in `app/setup.py`:

```bash
python app/setup.py
```

That creates `.venv/` at the repository root and installs `requirements.txt`.
