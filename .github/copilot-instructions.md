Purpose
-------
This file gives concise, actionable instructions for an AI coding agent to become productive in this repository. The workspace currently contains no discoverable project files, so these steps prioritize fast discovery, safe edits, and updating this document with any repository-specific rules you find.

Quick discovery checklist
- Look for language/build manifests (presence indicates toolchain): package.json, pyproject.toml, requirements.txt, Pipfile, setup.py, go.mod, Cargo.toml, pom.xml, build.gradle, Makefile, Dockerfile, .devcontainer/devcontainer.json.
- Inspect CI/workflows: .github/workflows/*.yml to learn build/test commands and environment matrix.
- Identify entry points and services: search for src/, app/, server/, cmd/, frontend/, web/, services/, Dockerfile, or main.go/manage.py/index.js.
- Locate tests: tests/, spec/, __tests__/, *_test.go, pytest.ini, or jest.config.js.

How to detect build & test commands (examples)
- Node: if package.json present, run `npm ci` then `npm test` or inspect `scripts` for `build`, `test`, `start`.
- Python: if pyproject.toml or requirements.txt present, create a venv and run `pip install -r requirements.txt` then `pytest` when tests found.
- Go: if go.mod present, use `go test ./...` and `go build ./...`.
- Rust: if Cargo.toml present, use `cargo test` and `cargo build`.
- If there is a Makefile or .github/workflows/*, prefer those targets/commands.

Editing rules for the agent
- Make minimal, focused changes. Prefer small patches that compile/tests pass.
- Use the repository's declared workflow (Makefile targets, npm scripts, etc.) instead of inventing commands.
- After making changes: run the appropriate test/build command and include results in your message.
- When modifying code, update any nearby README/usage notes and add a short rationale in the commit/patch message.

Documenting discovered conventions
- When you encounter a project-specific convention, add a short bullet to this file under "Repository notes" with a file reference and an example command. Example format:
  - Found: Flask app at [app.py](app.py) — run with: `python -m venv .venv && .venv\Scripts\pip install -r requirements.txt && python app.py`.

Merge guidance
- If a .github/copilot-instructions.md already exists, merge preserving existing bullets. Keep only factual, discoverable conventions — do not add speculative guidelines.

Safety & verification
- Never run destructive commands (eg rm -rf /, db drop without backup) without explicit user approval.
- If the repository contains infra (Terraform, Kubernetes manifests, docker-compose.yml), do not apply/plan/deploy; only read and note commands to run locally for testing.

If you are reading this and the repo is non-empty
- Replace the top section "Quick discovery checklist" with concrete findings and add a short "Repository notes" section listing detected build, test, run commands, and important directories.

Next steps for you (human or agent)
- If you'd like, I can: detect manifests now, run the top-level build/test commands, or open the first-pass architecture summary. Tell me which.
