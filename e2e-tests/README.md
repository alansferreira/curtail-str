# E2E Console Tests (`e2e-tests`)

## Objetivo

Esta pasta reúne projetos console mínimos e independentes para testar o consumo real (end-to-end) dos pacotes publicados da biblioteca `curtail-str` em cada linguagem suportada.

> **Importante (para desenvolvedores e agentes de IA)**: Os projetos dentro de `e2e-tests/` são **exclusivamente aplicações console** (`main`) para verificação rápida de uso da biblioteca instalada via gerenciador de pacotes. **Não adicione frameworks ou suítes de testes unitários aqui** — os testes unitários e de contrato ficam em [`packages/`](../packages/). Consulte a especificação completa em [`spec/e2e-tests.md`](../spec/e2e-tests.md).

## Projetos disponíveis

| Runtime | Pasta | Manifesto | Ponto de entrada | Guia |
| --- | --- | --- | --- | --- |
| Java | [`e2e-tests/java`](./java) | [`pom.xml`](./java/pom.xml) | [`src/main/java/Main.java`](./java/src/main/java/Main.java) | [README](./java/README.md) |
| Node.js | [`e2e-tests/node`](./node) | [`package.json`](./node/package.json) | [`main.mjs`](./node/main.mjs) | [README](./node/README.md) |

## Execução rápida (a partir da raiz do repositório)

### Java

```bash
mvn -q -f e2e-tests/java/pom.xml compile exec:java
```

### Node.js

```bash
npm --prefix e2e-tests/node install
npm --prefix e2e-tests/node start
```

## Saída padrão esperada em todos os runtimes

```text
Universal: active-customer-code-in-the-stock -> actv-cstm-cd-the-stck
Custom: customer-code -> cstm-cdg
Configurable: customer -> cs
```
