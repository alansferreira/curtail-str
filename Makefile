PYTHON ?= python3
MVN ?= mvn
PART ?= patch
VERSION ?=
CONFIRM ?=
RELEASE_PYTHON ?= .venv-release/bin/python

.DEFAULT_GOAL := help
.NOTPARALLEL:
.PHONY: help setup-release version check-version bump test test-release test-node test-python test-go test-java test-shell build build-node build-python build-go build-java build-shell release-check tag publish publish-node publish-python publish-java publish-go

help:
	@printf '%s\n' \
	  'make setup-release                  Install local release tooling and npm dev dependencies' \
	  'make bump PART=patch|minor|major     Bump the shared version (no commit or tag)' \
	  'make bump VERSION=X.Y.Z             Set a newer stable version explicitly' \
	  'make test / make build              Verify / build all packages' \
	  'make test-node / make build-node    Select node, python, go, java, or shell' \
	  'make tag CONFIRM=X.Y.Z              Create local release tags on a clean commit' \
	  'make publish CONFIRM=X.Y.Z          Test, build, push tags, publish all runtimes' \
	  'make publish-node CONFIRM=X.Y.Z     Publish one runtime (python/java/go also available)'

setup-release:
	$(PYTHON) -m venv .venv-release
	$(RELEASE_PYTHON) -m pip install -r requirements-release.txt
	cd packages/node && npm ci

version:
	@$(PYTHON) scripts/release.py version

check-version:
	$(PYTHON) scripts/release.py check

bump:
	$(PYTHON) scripts/release.py bump --part "$(PART)" $(if $(VERSION),--version "$(VERSION)",)

test: check-version test-release test-node test-python test-go test-java test-shell

test-release:
	$(PYTHON) -m unittest discover -s scripts/tests -v

test-node:
	cd packages/node && npm test && npm run typecheck && node test/package-smoke.cjs

test-python:
	PYTHONPATH=packages/python/src $(PYTHON) -m unittest discover -s packages/python/tests -v

test-go:
	cd packages/go && go test -race ./... && go vet ./...

test-java:
	$(MVN) -B -ntp -f packages/java/pom.xml verify

test-shell:
	$(PYTHON) -m unittest discover -s packages/shell/tests -v

build: check-version build-node build-python build-go build-java build-shell

build-node:
	$(PYTHON) scripts/release.py build node

build-python:
	$(RELEASE_PYTHON) scripts/release.py build python

build-go:
	$(PYTHON) scripts/release.py build go

build-java:
	$(MVN) -B -ntp -f packages/java/pom.xml clean package

build-shell:
	$(PYTHON) scripts/package_shell.py

release-check:
	$(PYTHON) scripts/release.py preflight --confirm "$(CONFIRM)"

tag: release-check
	$(PYTHON) scripts/release.py tag --confirm "$(CONFIRM)"

publish: release-check test build
	$(RELEASE_PYTHON) scripts/release.py publish all --confirm "$(CONFIRM)" --mvn "$(MVN)"

publish-node: release-check test-node build-node
	$(PYTHON) scripts/release.py publish node --confirm "$(CONFIRM)"

publish-python: release-check test-python build-python
	$(RELEASE_PYTHON) scripts/release.py publish python --confirm "$(CONFIRM)"

publish-java: release-check test-java build-java
	$(PYTHON) scripts/release.py publish java --confirm "$(CONFIRM)" --mvn "$(MVN)"

publish-go: release-check test-go build-go
	$(PYTHON) scripts/release.py publish go --confirm "$(CONFIRM)"
