PYTHON ?= python3
MVN ?= mvn
PART ?= patch
VERSION ?=
CONFIRM ?=
RELEASE_PYTHON ?= .venv-release/bin/python
REPOSITORY := https://github.com/alansferreira/curtail-str

.DEFAULT_GOAL := help
.NOTPARALLEL:
.PHONY: build-playground test-playground
.PHONY: help setup-release version check-version bump test test-node test-python test-go test-java test-shell build build-node build-python build-go build-java build-shell release-check tag push-tags publish publish-node publish-python publish-java publish-go

help:
	@printf '%s\n' \
	  'make setup-release                  Install local release tooling and npm dev dependencies' \
	  'make bump PART=patch|minor|major     Bump the shared version (no commit or tag)' \
	  'make bump VERSION=X.Y.Z             Set a newer stable version explicitly' \
	  'make test / make build              Verify / build all packages' \
	  'make test-node / make build-node    Select node, python, go, java, or shell' \
	  'make test-playground                Build and test the browser playground' \
	  'make tag CONFIRM=X.Y.Z              Create local release tags on a clean commit' \
	  'make publish CONFIRM=X.Y.Z          Test, build, push tags, publish all runtimes' \
	  'make publish-node CONFIRM=X.Y.Z     Publish one runtime (python/java/go also available)'

setup-release:
	$(PYTHON) -m venv .venv-release
	$(RELEASE_PYTHON) -m pip install -r requirements-release.txt
	cd packages/node && npm ci

version:
	@tr -d '\r\n' < VERSION && printf '\n'

check-version:
	@version=$$(tr -d '\r\n' < VERSION); \
	printf '%s\n' "$$version" | grep -Eq '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$$' || { echo "Version must be stable SemVer X.Y.Z without leading zeros: $$version" >&2; exit 1; }; \
	sed -n '1,5p' packages/node/package.json | grep -Fq "\"version\": \"$$version\"" || { echo "node version does not match VERSION $$version" >&2; exit 1; }; \
	test "$$(sed -n '1,15p' packages/node/package-lock.json | grep -F -c "\"version\": \"$$version\"")" -eq 2 || { echo "npm lock version does not match VERSION $$version" >&2; exit 1; }; \
	grep -Fq "version = \"$$version\"" packages/python/pyproject.toml || { echo "python version does not match VERSION $$version" >&2; exit 1; }; \
	sed -n '1,15p' packages/java/pom.xml | grep -Fq "<version>$$version</version>" || { echo "java version does not match VERSION $$version" >&2; exit 1; }; \
	for pkg in node python go java; do \
		cmp -s LICENSE "packages/$$pkg/LICENSE" || { echo "$$pkg/LICENSE does not match the root license" >&2; exit 1; }; \
	done; \
	echo "Shared version: $$version"

bump: check-version
	@old=$$(tr -d '\r\n' < VERSION); \
	if [ -n "$(VERSION)" ]; then \
		printf '%s\n' "$(VERSION)" | grep -Eq '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$$' || { echo "Version must be stable SemVer X.Y.Z without leading zeros" >&2; exit 1; }; \
		awk -v old="$$old" -v new="$(VERSION)" 'BEGIN { \
			split(old, o, "."); split(new, n, "."); \
			if (n[1]+0 > o[1]+0 || (n[1]+0 == o[1]+0 && n[2]+0 > o[2]+0) || (n[1]+0 == o[1]+0 && n[2]+0 == o[2]+0 && n[3]+0 > o[3]+0)) exit 0; \
			exit 1; \
		}' || { echo "New version must be greater than the current version" >&2; exit 1; }; \
		new="$(VERSION)"; \
	else \
		case "$(PART)" in \
			major|minor|patch) ;; \
			*) echo "PART must be major, minor, or patch" >&2; exit 1 ;; \
		esac; \
		new=$$(awk -v old="$$old" -v part="$(PART)" 'BEGIN { \
			split(old, v, "."); \
			if (part == "major") printf "%d.0.0", v[1]+1; \
			else if (part == "minor") printf "%d.%d.0", v[1], v[2]+1; \
			else printf "%d.%d.%d", v[1], v[2], v[3]+1; \
		}'); \
	fi; \
	old_re=$$(printf '%s' "$$old" | sed 's/\./\\./g'); \
	replace_in_file() { tmp="$$1.tmp"; sed "$$2" "$$1" > "$$tmp" && mv "$$tmp" "$$1"; }; \
	printf '%s\n' "$$new" > VERSION; \
	replace_in_file packages/node/package.json "1,5s/\"version\": \"$$old_re\"/\"version\": \"$$new\"/"; \
	replace_in_file packages/node/package-lock.json "1,15s/\"version\": \"$$old_re\"/\"version\": \"$$new\"/g"; \
	replace_in_file packages/python/pyproject.toml "s/^version = \"$$old_re\"$$/version = \"$$new\"/"; \
	replace_in_file packages/java/pom.xml "1,15s|<version>$$old_re</version>|<version>$$new</version>|"; \
	for doc in README.md packages/java/README.md packages/shell/README.md docs/releases.md; do \
		replace_in_file "$$doc" "s/$$old_re/$$new/g"; \
	done; \
	$(PYTHON) scripts/package_shell.py; \
	rm -f "packages/shell/dist/curtail-str-shell-$$old.tar.gz" "packages/shell/dist/curtail-str-shell-$$old.zip"; \
	$(MAKE) --no-print-directory check-version; \
	echo "Version updated: $$old -> $$new. Review and commit before tagging."

test: check-version test-node test-python test-go test-java test-shell

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
	mkdir -p packages/node/dist
	cd packages/node && npm pack --pack-destination dist

build-python:
	$(RELEASE_PYTHON) -m build packages/python
	@version=$$(tr -d '\r\n' < VERSION); \
	$(RELEASE_PYTHON) -m twine check --strict \
		"packages/python/dist/curtail_str-$$version-py3-none-any.whl" \
		"packages/python/dist/curtail_str-$$version.tar.gz" && \
	$(RELEASE_PYTHON) scripts/check_python_distribution.py \
		"packages/python/dist/curtail_str-$$version-py3-none-any.whl" \
		"packages/python/dist/curtail_str-$$version.tar.gz"

build-go:
	cd packages/go && go build ./...

build-java:
	$(MVN) -B -ntp -f packages/java/pom.xml clean package

build-shell:
	$(PYTHON) scripts/package_shell.py

build-playground:
	node scripts/build_playground.mjs

test-playground: build-playground
	node --test scripts/tests/playground.test.mjs

release-check: check-version
	@version=$$(tr -d '\r\n' < VERSION); \
	test "$(CONFIRM)" = "$$version" || { echo "Explicit confirmation required: CONFIRM=$$version" >&2; exit 1; }; \
	test -z "$$(git status --porcelain --untracked-files=all)" || { echo "Release requires a clean Git tree, including untracked files" >&2; exit 1; }; \
	test "$$(git branch --show-current)" = "main" || { echo "Release requires the main branch" >&2; exit 1; }; \
	remote=$$(git remote get-url origin); \
	case "$$remote" in \
		"$(REPOSITORY)"|"$(REPOSITORY).git"|git@github.com:alansferreira/curtail-str.git) ;; \
		*) echo "origin must point to alansferreira/curtail-str" >&2; exit 1 ;; \
	esac; \
	head=$$(git rev-parse HEAD); \
	for tag in "v$$version" "packages/go/v$$version"; do \
		if [ -n "$$(git tag --list "$$tag")" ] && [ "$$(git rev-list -n 1 "$$tag")" != "$$head" ]; then \
			echo "Tag $$tag already points to another commit" >&2; exit 1; \
		fi; \
	done; \
	echo "Release preflight passed: $$version"

tag: release-check
	@version=$$(tr -d '\r\n' < VERSION); \
	for tag in "v$$version" "packages/go/v$$version"; do \
		if [ -z "$$(git tag --list "$$tag")" ]; then \
			git tag -a "$$tag" -m "curtail-str $$version"; \
		fi; \
	done

push-tags: release-check
	@version=$$(tr -d '\r\n' < VERSION); \
	head=$$(git rev-parse HEAD); \
	remote_main=$$(git ls-remote --exit-code origin refs/heads/main | awk '{print $$1}'); \
	test "$$remote_main" = "$$head" || { echo "Push the release commit to origin/main before publishing" >&2; exit 1; }; \
	for tag in "v$$version" "packages/go/v$$version"; do \
		refs=$$(git ls-remote origin "refs/tags/$$tag" "refs/tags/$$tag^{}"); \
		if [ -n "$$refs" ]; then \
			remote_head=$$(printf '%s\n' "$$refs" | awk '$$2 ~ /\^\{\}$$/ { deref=$$1 } END { print (deref ? deref : $$1) }'); \
			test "$$remote_head" = "$$head" || { echo "Remote tag $$tag points to another commit" >&2; exit 1; }; \
		fi; \
		if [ -z "$$(git tag --list "$$tag")" ] && [ -n "$$(git ls-remote origin "refs/tags/$$tag")" ]; then \
			git fetch --no-tags origin "refs/tags/$$tag:refs/tags/$$tag"; \
		fi; \
		if [ -z "$$(git tag --list "$$tag")" ]; then \
			git tag -a "$$tag" -m "curtail-str $$version"; \
		fi; \
	done; \
	git push --atomic origin "refs/tags/v$$version" "refs/tags/packages/go/v$$version"

publish: release-check test build
	@version=$$(tr -d '\r\n' < VERSION); \
	test -f "packages/node/dist/curtail-str-$$version.tgz" || { echo "Build the npm tarball first" >&2; exit 1; }; \
	npm whoami --registry=https://registry.npmjs.org/; \
	test -n "$$TWINE_USERNAME" || { echo "Missing environment variable: TWINE_USERNAME" >&2; exit 1; }; \
	test -n "$$TWINE_PASSWORD" || { echo "Missing environment variable: TWINE_PASSWORD" >&2; exit 1; }; \
	$(RELEASE_PYTHON) -m twine check --strict \
		"packages/python/dist/curtail_str-$$version-py3-none-any.whl" \
		"packages/python/dist/curtail_str-$$version.tar.gz"; \
	test -n "$$CENTRAL_USERNAME" || { echo "Missing environment variable: CENTRAL_USERNAME" >&2; exit 1; }; \
	test -n "$$CENTRAL_PASSWORD" || { echo "Missing environment variable: CENTRAL_PASSWORD" >&2; exit 1; }; \
	command -v "$(MVN)" >/dev/null 2>&1 || { echo "Maven executable not found: $(MVN)" >&2; exit 1; }; \
	gpg --list-secret-keys --with-colons | grep -q '^sec:' || { echo "A GPG secret key is required for Maven Central signing" >&2; exit 1; }; \
	$(MVN) -ntp -f packages/java/pom.xml -Prelease clean verify; \
	$(MAKE) --no-print-directory push-tags CONFIRM="$(CONFIRM)"; \
	echo "Go version published by tag: packages/go/v$$version"; \
	npm publish "packages/node/dist/curtail-str-$$version.tgz" --access=public --registry=https://registry.npmjs.org/; \
	$(RELEASE_PYTHON) -m twine upload --non-interactive \
		--repository-url https://upload.pypi.org/legacy/ \
		"packages/python/dist/curtail_str-$$version-py3-none-any.whl" \
		"packages/python/dist/curtail_str-$$version.tar.gz"; \
	$(MVN) -ntp -s scripts/maven-settings.xml -f packages/java/pom.xml -Prelease deploy

publish-node: release-check test-node build-node
	@version=$$(tr -d '\r\n' < VERSION); \
	test -f "packages/node/dist/curtail-str-$$version.tgz" || { echo "Build the npm tarball first" >&2; exit 1; }; \
	npm whoami --registry=https://registry.npmjs.org/; \
	$(MAKE) --no-print-directory push-tags CONFIRM="$(CONFIRM)"; \
	npm publish "packages/node/dist/curtail-str-$$version.tgz" --access=public --registry=https://registry.npmjs.org/

publish-python: release-check test-python build-python
	@version=$$(tr -d '\r\n' < VERSION); \
	test -n "$$TWINE_USERNAME" || { echo "Missing environment variable: TWINE_USERNAME" >&2; exit 1; }; \
	test -n "$$TWINE_PASSWORD" || { echo "Missing environment variable: TWINE_PASSWORD" >&2; exit 1; }; \
	$(RELEASE_PYTHON) -m twine check --strict \
		"packages/python/dist/curtail_str-$$version-py3-none-any.whl" \
		"packages/python/dist/curtail_str-$$version.tar.gz"; \
	$(MAKE) --no-print-directory push-tags CONFIRM="$(CONFIRM)"; \
	$(RELEASE_PYTHON) -m twine upload --non-interactive \
		--repository-url https://upload.pypi.org/legacy/ \
		"packages/python/dist/curtail_str-$$version-py3-none-any.whl" \
		"packages/python/dist/curtail_str-$$version.tar.gz"

publish-java: release-check test-java build-java
	@test -n "$$CENTRAL_USERNAME" || { echo "Missing environment variable: CENTRAL_USERNAME" >&2; exit 1; }; \
	test -n "$$CENTRAL_PASSWORD" || { echo "Missing environment variable: CENTRAL_PASSWORD" >&2; exit 1; }; \
	command -v "$(MVN)" >/dev/null 2>&1 || { echo "Maven executable not found: $(MVN)" >&2; exit 1; }; \
	gpg --list-secret-keys --with-colons | grep -q '^sec:' || { echo "A GPG secret key is required for Maven Central signing" >&2; exit 1; }; \
	$(MVN) -ntp -f packages/java/pom.xml -Prelease clean verify; \
	$(MAKE) --no-print-directory push-tags CONFIRM="$(CONFIRM)"; \
	$(MVN) -ntp -s scripts/maven-settings.xml -f packages/java/pom.xml -Prelease deploy

publish-go: release-check test-go build-go
	@version=$$(tr -d '\r\n' < VERSION); \
	$(MAKE) --no-print-directory push-tags CONFIRM="$(CONFIRM)"; \
	echo "Go version published by tag: packages/go/v$$version"
