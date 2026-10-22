# Playground

The playground is a static, browser-only interface for all three curtail-str
modes. Input is processed locally, never sent to a server or stored. Use a
current browser supporting Unicode property escapes and `String.isWellFormed`.

## Local development

From the repository root, using Node.js 22+:

```sh
make build-playground test-playground
python3 -m http.server 8000 --directory playground/dist
```

Open <http://localhost:8000>. Stop the server with Ctrl+C.

The build copies the UI and MIT license to the ignored `dist` directory and
converts only the CommonJS export of the real Node.js implementation to an
ES module. No algorithm is duplicated, no bundler or external CDN is needed,
and published runtime packages are unchanged. Tests run the complete shared
contract against the generated browser module.

## GitHub Pages

In the repository's **Settings > Pages**, set **Source** to **GitHub Actions**.
Commit and push the playground and workflow to `main`.
The [Pages workflow](../.github/workflows/cd-pages.yaml) builds and tests the
site on relevant pull requests, and deploys it after relevant pushes to `main`.
It can also be started manually from `main`.

The expected URL is <https://alansferreira.github.io/curtail-str/>.
The `github-pages` environment exposes the actual deployment URL in Actions.
All asset URLs are relative, so the site works under the repository path.
No registry tokens or GPG keys are needed. The deployment job uses only
`pages: write` and `id-token: write`; pull requests cannot deploy.

The site is separate from runtime publication and does not create release
tags or publish packages. Repository Pages policies and environment approval
rules must allow deployments from `main`.
