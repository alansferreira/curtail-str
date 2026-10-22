# E2E Console Tests Specification (`e2e-tests/`)

This specification defines the contract and structure for end-to-end (E2E) consumer projects under [`e2e-tests/`](../e2e-tests/). Future AI agents and contributors MUST follow these rules when creating or updating E2E projects for any runtime.

## 1. Objective and Constraints

- **External Consumer Simulation**: Each `e2e-tests/<runtime>` directory represents an isolated, standalone consumer project that installs and uses the published `curtail-str` package from its ecosystem registry (Maven/JitPack, npm, PyPI, Go module proxy, etc.).
- **Console Application Only**: Every E2E project MUST be a minimal command-line / console application with a single entry point (`main`).
- **No Unit Tests**: Do **NOT** add unit test frameworks (JUnit, Jest, Mocha, `node:test`, `pytest`, Go `testing`, etc.) or unit test files under `e2e-tests/`. Contract and unit tests belong exclusively in `packages/<runtime>`.
- **No Internal Source Imports**: E2E code MUST import the public package identifier (`local.curtailstr.CurtailStr`, `'curtail-str'`, `curtail_str`, etc.) resolved through the package manager, never via relative file paths into `../../packages/`.

## 2. Standard Scenarios & Output Contract

Every E2E console entry point MUST execute the same three scenarios in order and print the exact lines below to `stdout`:

| Scenario | Input | Options | Expected Line Printed |
| --- | --- | --- | --- |
| **Universal** | `"active-customer-code-in-the-stock"` | Default (`universal`) | `Universal: active-customer-code-in-the-stock -> actv-cstm-cd-the-stck` |
| **Custom** | `"customer-code"` | `mode: custom`, `replacements: {"code": "cdg"}` | `Custom: customer-code -> cstm-cdg` |
| **Configurable** | `"customer"` | `mode: configurable`, `maxWordLength: 2` | `Configurable: customer -> cs` |

### Exact Expected `stdout`

```text
Universal: active-customer-code-in-the-stock -> actv-cstm-cd-the-stck
Custom: customer-code -> cstm-cdg
Configurable: customer -> cs
```

## 3. Runtime Blueprints

### Java (`e2e-tests/java`)

- **Manifest**: `pom.xml` depending only on `io.github.alansferreira:curtail-str` and setting `<exec.mainClass>Main</exec.mainClass>`.
- **Entry point**: `src/main/java/Main.java`.
- **Run command**: `mvn -q -f e2e-tests/java/pom.xml compile exec:java`.

### Node.js (`e2e-tests/node`)

- **Manifest**: `package.json` (`"private": true`, `"type": "module"`, `"scripts": { "start": "node main.mjs" }`) depending only on `curtail-str`.
- **Entry point**: `main.mjs`.
- **Run command**: `npm --prefix e2e-tests/node install && npm --prefix e2e-tests/node start`.

### Python (`e2e-tests/python` — blueprint for future implementation)

- **Manifest**: `requirements.txt` or `pyproject.toml` depending only on `curtail-str`.
- **Entry point**: `main.py`.
- **Run command**: `python e2e-tests/python/main.py` (inside an isolated venv with `curtail-str` installed).

### Go (`e2e-tests/go` — blueprint for future implementation)

- **Manifest**: `go.mod` requiring `github.com/alansferreira/curtail-str/packages/go`.
- **Entry point**: `main.go`.
- **Run command**: `go -C e2e-tests/go run .`.

## 4. Required Per-Runtime Documentation (`e2e-tests/<runtime>/README.md`)

Every `e2e-tests/<runtime>` folder MUST include a `README.md` (in Portuguese, matching existing E2E READMEs) containing:

1. **Objetivo**: Explaining that the folder is a standalone console project to validate real consumption of the published package without unit tests.
2. **Estrutura**: Listing the manifest and entry-point file.
3. **Comandos de teste**: Commands to run both from inside `e2e-tests/<runtime>` and from the repository root.
4. **Saída esperada**: The 3-line expected console output block.
