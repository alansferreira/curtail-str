# Releases

All runtime packages share the stable semantic version in [VERSION](../VERSION).
The [Makefile](../Makefile) provides version bumps, tests, builds, tags, and
explicit publication. Commands run from the repository root.

## Requirements

- GNU Make, Python 3.11+, Git, and the supported Node.js, Go, and Java runtimes.
- npm and Maven 3.9.2+ on PATH.
- GnuPG with a signing key for Maven Central.
- Access to npm, PyPI, the Sonatype Central Portal, and the GitHub repository.
- A POSIX-compatible shell, such as Linux, macOS, or WSL, for Make recipes.
  The distributed Windows scripts do not require Make.

Set up local release dependencies:

```sh
make setup-release
```

This creates `.venv-release`, installs the packages declared in
[requirements-release.txt](../requirements-release.txt), and restores npm
development dependencies. It does not install language runtimes or Maven.
Override `PYTHON`, `MVN`, or `RELEASE_PYTHON` when needed:

```sh
make test PYTHON=python3.11 MVN=/opt/maven/bin/mvn
```

## Version bumps

```sh
make version
make bump                    # patch
make bump PART=minor
make bump PART=major
make bump VERSION=1.0.0       # explicit newer stable version
```

Bumps update Node.js metadata and its lockfile, Python metadata, Maven metadata,
versioned documentation links, and shell archives/checksums. Go takes its
version from Git tags rather than a version field in source code.
Only stable `X.Y.Z` versions without leading zeros are accepted.

A bump does not commit, tag, push, or publish. Review and commit all changes,
including added and removed shell archives, before tagging. Package license
files must match the root [MIT license](../LICENSE).

## Tests and builds

```sh
make check-version
make test
make build
```

Select individual runtimes with `test-node`, `test-python`, `test-go`,
`test-java`, `build-node`, `build-python`, `build-go`, or `build-java`.
`test-shell` and `build-shell` cover the standalone shell distribution.

Build outputs:

| Package | Output |
| --- | --- |
| npm | `packages/node/dist/curtail-str-X.Y.Z.tgz` |
| Python | `packages/python/dist/curtail_str-X.Y.Z-py3-none-any.whl` and `.tar.gz` |
| Java | `packages/java/target/curtail-str-X.Y.Z.jar` |
| Go | Package compilation; distribution uses Git tags |
| Shell | Versioned archives and checksums in `packages/shell/dist/` |

Python builds run Twine metadata checks and test both installed distributions.
Only artifacts matching `VERSION` are uploaded; old files in ignored build
directories are not selected. Shell archives are reproducible, so rebuilding
unchanged tracked content does not make the release tree dirty.

## Registry credentials

Never store tokens, signing keys, or passwords in the repository.

### npm

Authenticate with `npm login --registry=https://registry.npmjs.org/` or configure
a suitable token in your user npm configuration. Publication uses the public
npm registry, performs `npm whoami` before upload, and stages the package with
`npm stage publish` (requires npm 11.15.0+) for subsequent 2FA approval.

### PyPI

Create an API token with permission to publish `curtail-str`, then supply:

```sh
export TWINE_USERNAME=__token__
# Provide TWINE_PASSWORD through a secret manager or protected environment.
```

`TWINE_PASSWORD` must contain the token. The upload URL is fixed to production
PyPI, and uploads are non-interactive.

### Maven Central

Verify ownership of `io.github.alansferreira` in the
[Central Portal](https://central.sonatype.com/) and generate a publisher token.
Supply its username and password as `CENTRAL_USERNAME` and `CENTRAL_PASSWORD`.
The [Maven settings template](../scripts/maven-settings.xml) reads these
environment variables using server ID `central`.

Import your signing key into GnuPG and publish its public key to an appropriate
public key server. Unlock it with a GPG agent or provide `MAVEN_GPG_PASSPHRASE`
through a protected environment. Signing uses Maven GPG Plugin best-practice
mode; do not put the passphrase on the command line.

Java publication runs Maven interactively, allowing GPG agent to request the
passphrase through pinentry. Install a working pinentry program; in a Unix
terminal, set `export GPG_TTY="$(tty)"` before publishing. The profile does not
force loopback mode. Maven GPG Plugin enables loopback automatically when
`MAVEN_GPG_PASSPHRASE` is provided.

For a headless environment or an unavailable pinentry prompt, use a secret
manager to supply that variable. In a local Bash terminal, you can instead read
the passphrase without echoing or saving it in shell history, then test signing
without uploading:

```bash
read -r -s -p "GPG passphrase: " MAVEN_GPG_PASSPHRASE
printf '\n'
export MAVEN_GPG_PASSPHRASE
mvn -ntp -f packages/java/pom.xml -Prelease clean verify
unset MAVEN_GPG_PASSPHRASE
```

Do not enable shell tracing (`set -x`) while handling the passphrase. The
environment variable remains available to child processes until unset; use a
trusted terminal and clear it even if the command fails. For publication,
repeat the prompt and replace the Maven command with
`make publish-java CONFIRM=X.Y.Z`, using the current version.

The Maven `release` profile attaches source and Javadoc JARs, signs artifacts,
uploads through the Central Publishing plugin, and waits for publication.
Coordinates are `io.github.alansferreira:curtail-str:X.Y.Z`.
The ordinary build does not activate signing or upload.

To inspect release artifacts without uploading:

```sh
mvn -ntp -f packages/java/pom.xml -Prelease verify
```

This requires a usable signing key but does not invoke `deploy`.

The main JAR is a library artifact, not a Central Portal upload bundle.
Uploading it manually produces errors such as "Bundle has content that does
NOT have a .pom file" for its internal `META-INF` and class directories.
Use `make publish-java CONFIRM=X.Y.Z` to let the Central Publishing plugin
assemble and upload the bundle. The `verify` command above does not create
that bundle. A manual Portal upload requires a ZIP with Maven repository
layout containing the POM, main, source, and Javadoc JARs, their signatures,
and checksums; renaming the main JAR to ZIP is not sufficient.

## Tagging and publishing

Release commands require:

- Matching versions in all package metadata.
- A clean Git tree, including untracked files.
- The `main` branch and `origin` pointing to the project repository.
- An explicit `CONFIRM` equal to `VERSION`.
- No release tag pointing to a different commit.

Publishing additionally requires that the local commit already matches
`origin/main`. The commands do not push source commits.

```sh
make tag CONFIRM=0.1.6        # optional: creates local annotated tags only
make publish CONFIRM=0.1.6    # tests, builds, pushes tags, uploads all runtimes
```

Replace `0.1.6` with the current version. The tags are:

- `vX.Y.Z` for the overall release.
- `packages/go/vX.Y.Z` for the Go module in its repository subdirectory.

Java publication verifies signed release artifacts before creating or pushing
tags, so signing failures do not trigger those remote mutations.
After local checks, publication creates any missing tags and pushes both tags
atomically. It then uploads npm, PyPI, and Maven Central artifacts. Go is
published by the subdirectory tag and may take time to appear through proxies.
Shell downloads are served from the tracked GitHub files, not a separate
registry.

To publish or retry one runtime:

```sh
make publish-node CONFIRM=0.1.6
make publish-python CONFIRM=0.1.6
make publish-java CONFIRM=0.1.6
make publish-go CONFIRM=0.1.6
```

Each target runs the relevant tests and build before publication. Existing tags
at the release commit are reused, fetching missing local tags from `origin`
when necessary. Conflicting tags are never moved or deleted.

**Registry publication is not transactional.** A later failure does not undo
tags or successful uploads to other registries. Inspect registry state and retry
only the failed runtime. Existing versions are not overwritten or silently
skipped. If published contents need changing, bump to a new version.

## GitHub Actions CD

Publication workflows are separated by destination:

| Destination | Workflow |
| --- | --- |
| npm | [Publish npm](../.github/workflows/cd-npm.yaml) |
| PyPI | [Publish PyPI](../.github/workflows/cd-pypi.yaml) |
| Maven Central | [Publish Maven Central](../.github/workflows/cd-maven-central.yaml) |
| Go module tags | [Publish Go](../.github/workflows/cd-go.yaml) |

Open **Actions > Publish destination > Run workflow** and select `main`.
The workflow reads the release version automatically from the committed
`VERSION` file and validates matching package metadata; no version input is
required. Run each destination separately to publish all packages or retry
only a failed registry. Each workflow is independent and installs only the
tools for its destination.
There is no generic or reusable CD workflow.

Before the first run, create a GitHub environment named `release`. Restrict
deployment branches to `main` and configure required reviewers if supported
by your GitHub plan. Add the following environment secrets:

| Secret | Required for | Value |
| --- | --- | --- |
| `NPM_TOKEN` | Node.js | npm token with permission to stage packages for `curtail-str` |
| `PYPI_TOKEN` | Python | PyPI API token, including the `pypi-` prefix |
| `CENTRAL_USERNAME` | Java | Central Portal publisher-token username |
| `CENTRAL_PASSWORD` | Java | Central Portal publisher-token password |
| `GPG_PRIVATE_KEY` | Java | ASCII-armored private signing key |
| `MAVEN_GPG_PASSPHRASE` | Java | Passphrase protecting that private key |

Export the private key only to a protected local file when configuring the
secret; do not print it in logs, attach it to chat, or commit it:

```sh
gpg --armor --export-secret-keys YOUR_FINGERPRINT > /secure/path/signing-key.asc
```

Transfer the file content to the `GPG_PRIVATE_KEY` environment secret, then
remove the local export securely. The public key must already be published
to a public key server. The runner imports the private key into a temporary,
isolated GPG home, uses the passphrase through the environment without an
interactive prompt, and stops its GPG agent at step exit. GitHub-hosted runners
are ephemeral; do not change this workflow to a persistent self-hosted runner
without adding key cleanup.

Every run checks the dispatched commit and version, tests its own runtime
package, builds that package, then publishes only its destination. The
separate CI workflow covers the complete runtime matrix.
Registry secrets are
provided only to the publishing step. The job uses `GITHUB_TOKEN` with
`contents: write` for annotated release tags; no personal access token is
needed. Repository tag rules must permit those pushes.

Publication runs are serialized and an active run is never automatically
cancelled by a later dispatch. Avoid publishing locally at the same time.
The workflows neither bump versions nor commit or push source changes.
Commit and push the release version to `main` before dispatching. If `main`
changes while a run waits for approval, start a new run for the current commit.
There is no publication trigger on pushes, tags, or pull requests.

The separate CI verification workflow never publishes packages.
