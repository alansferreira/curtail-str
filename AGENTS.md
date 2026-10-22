# AI Agent Guidelines (`curtail-str`)

This document provides context, architecture rules, and specifications for AI coding assistants working in this repository.

## Repository Structure

- [`spec/algorithm.md`](./spec/algorithm.md) & [`spec/cases.json`](./spec/cases.json): Canonical specification and shared contract test cases for the `curtail-str` abbreviation algorithm across all runtimes.
- [`spec/e2e-tests.md`](./spec/e2e-tests.md): Canonical specification for standalone end-to-end console consumer projects in [`e2e-tests/`](./e2e-tests/).
- [`packages/`](./packages/): Source implementations, builds, and unit/contract tests for each runtime (`node`, `python`, `go`, `java`, `shell`).
- [`e2e-tests/`](./e2e-tests/): Standalone console applications that consume the published packages to validate real-world package installation and usage.
- [`playground/`](./playground/): Interactive browser playground for exploring the three abbreviation modes.
- [`docs/releases.md`](./docs/releases.md): Release workflow, versioning (`VERSION`), and `Makefile` targets.

## Strict Rules for `e2e-tests/`

When creating or modifying any project inside [`e2e-tests/`](./e2e-tests/):

1. **Console Only — No Unit Tests**:
   - Projects under `e2e-tests/<runtime>` MUST be simple console applications with a `main` entry point that prints output to `stdout`.
   - NEVER add unit test dependencies (such as JUnit, Jest, Mocha, `pytest`, etc.) or test runners to `e2e-tests/<runtime>`.
2. **Published Package Consumption**:
   - Declare only the `curtail-str` runtime dependency in the ecosystem manifest (`pom.xml`, `package.json`, `requirements.txt`, `go.mod`).
   - Do not import source files via relative paths from `../../packages/`.
3. **Standard 3-Mode Output**:
   - Every E2E console app MUST demonstrate the three modes (`universal`, `custom`, `configurable`) using the exact inputs and options defined in [`spec/e2e-tests.md`](./spec/e2e-tests.md) and print:
     ```text
     Universal: active-customer-code-in-the-stock -> actv-cstm-cd-the-stck
     Custom: customer-code -> cstm-cdg
     Configurable: customer -> cs
     ```
4. **Documentation**:
   - Each `e2e-tests/<runtime>` folder MUST have a `README.md` with its objective, file structure, execution commands (from the folder and from the repo root), and expected output.
   - Update [`e2e-tests/README.md`](./e2e-tests/README.md) and [`spec/e2e-tests.md`](./spec/e2e-tests.md) whenever a new runtime E2E project is added.

## Rules for `packages/`

- Any change to algorithm behavior MUST follow [`spec/algorithm.md`](./spec/algorithm.md) and pass all shared fixtures in [`spec/cases.json`](./spec/cases.json) across `node`, `python`, `go`, and `java` (`make test`).
- Runtime packages have zero runtime dependencies.
