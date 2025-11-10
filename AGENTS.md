---
Repository Guidelines
======================

This document describes the conventions and tools used in the
`llm-toolcall-proxy` project.  Follow it when adding code, tests, or
documentation to keep the repo consistent and maintainable.

## Project Structure & Module Organization
------------------------------------------
```
├── app.py                  # Flask entry point
├── config.py               # Environment‑based settings
├── converters/             # Tool‑call conversion logic
│   ├── base.py             # Abstract converter API
│   ├── factory.py          # Converter factory & registry
│   ├── openai.py
│   ├── claude.py
│   └── glm.py
├── tests/                  # Pytest test suites
├── requirements.txt
└── README.md
```
All source files are Python 3.7+ modules.  Tests live in `tests/` and follow
the same naming convention as the modules they exercise.

## Build, Test, and Development Commands
----------------------------------------
* `pip install -r requirements.txt` – install runtime dependencies.
* `python -m pytest` – run the full test suite.
* `python -m pytest tests/test_<name>.py` – run a single test module.
* `python app.py` – start the proxy locally (defaults to port 5000).
* `flask run` – alternative way to start the app, honors `FLASK_ENV`.

All commands assume the current working directory is the repository root.

## Coding Style & Naming Conventions
-------------------------------------
* **PEP 8** is the style guide; run `black . && isort .` before committing.
* Functions and methods use `snake_case`.
* Classes use `PascalCase` and derive from `ToolCallConverter` when implementing
  a new converter.
* Module names are lowercase with underscores; e.g. `glm.py`.
* Variables and attributes are typed with `typing` hints where useful.

Linting is performed with `ruff` – run `ruff check .` to validate.

## Testing Guidelines
----------------------
* The project uses **pytest** with the `pytest-cov` plugin.
* Test files are named `test_*.py` and reside in `tests/`.
* Coverage should be ≥ 85 % for new code paths.
* Test names follow `test_<feature>_<scenario>`.
* Run `pytest --cov=.` to generate a coverage report.

## Commit & Pull Request Guidelines
------------------------------------
* Commit messages follow the Conventional Commits format:
  ````
  type(scope?): subject
  ```
  * `feat`, `fix`, `refactor`, `test`, `docs`
* Pull requests should:
  1. Reference a GitHub issue (`Closes #123`).
  2. Include a brief description of the change.
  3. Add screenshots or examples if the change affects user‑visible behavior.
  4. Pass all tests (`python -m pytest`).
  5. Pass linting (`ruff check .`).

## Security & Configuration Tips
---------------------------------
* All configurable options are exposed via environment variables.  See
  `config.py` for defaults.
* The proxy disables tool‑call conversion by default in non‑production
  environments (`ENABLE_TOOL_CALL_CONVERSION=false`).
* Do not commit secrets – use a `.env` file ignored by `.gitignore`.

Feel free to raise an issue if any convention needs clarification.
---
