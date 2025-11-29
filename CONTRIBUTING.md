# Contributing

Thanks for wanting to help — this file is short and practical.

What to read first

- Read the main `README.md` to understand project goals and how to run the app.
- Keep changes small and focused.

Report issues

- Open an issue on the GitHub repository describing the bug or feature with steps to reproduce and any logs or screenshots.

Submit a pull request

1. Fork the repository and create a feature branch from `main`.
2. Make small, well-scoped commits with clear messages.
3. Run the app and any tests locally.
4. Push your branch and open a PR describing the change, motivation, and testing done.

Style & tests

- Follow PEP 8 for Python code.
- Keep CLI behavior backward compatible when possible.
- If you add or change functionality, include or update a small test in `tools/` where appropriate.

Versioning and releases

- The project version is stored in the `VERSION` file at the repo root. If your change requires a version bump (e.g. new feature/fix), update `VERSION` to the new semantic version and mention it in the PR description.
- The release process uses PyInstaller to build a single-file EXE; see `DOWNLOAD.md` for details.

Local development tips

- Use a virtual environment:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

- Run the app interactively while developing:

```cmd
python main.py
```

Code of Conduct

- Be respectful. Keep interactions constructive and focused on improving the project.

Thank you for contributing! 🎉

