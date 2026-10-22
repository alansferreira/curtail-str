# E2E Test — Node.js Console

## Objetivo

Esta pasta (`e2e-tests/node`) contém um projeto Node.js console mínimo e independente para validar o consumo real (end-to-end) do pacote publicado `curtail-str` via npm, exercitando a API pública nos modos `universal`, `custom` e `configurable` sem depender da estrutura interna do repositório ou de frameworks de testes unitários.

## Estrutura

- [package.json](./package.json): configuração do pacote com a dependência `curtail-str` e script `start`.
- [main.mjs](./main.mjs): aplicação console que executa chamadas de exemplo da biblioteca e imprime os resultados no terminal.

## Comandos de teste

Executando a partir da pasta `e2e-tests/node`:

```bash
# Instalar a dependência e executar a aplicação console
npm install
npm start
```

Executando a partir da raiz do repositório:

```bash
# Instalar dependências e executar sem mudar de diretório
npm --prefix e2e-tests/node install
npm --prefix e2e-tests/node start
```

### Saída esperada

```text
Universal: active-customer-code-in-the-stock -> actv-cstm-cd-the-stck
Custom: customer-code -> cstm-cdg
Configurable: customer -> cs
```
