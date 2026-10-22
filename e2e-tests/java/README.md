# E2E Test — Java Console

## Objetivo

Esta pasta (`e2e-tests/java`) contém um projeto Java console mínimo e independente para validar o consumo real (end-to-end) do pacote publicado `io.github.alansferreira:curtail-str` via Maven, exercitando a API pública nos modos `UNIVERSAL`, `CUSTOM` e `CONFIGURABLE` sem depender da estrutura interna do repositório ou de frameworks de testes unitários.

## Estrutura

- [pom.xml](./pom.xml): configuração Maven com a dependência `io.github.alansferreira:curtail-str` e definição da classe principal (`Main`).
- [src/main/java/Main.java](./src/main/java/Main.java): aplicação console que executa chamadas de exemplo da biblioteca e imprime os resultados no terminal.

## Comandos de teste

Executando a partir da pasta `e2e-tests/java`:

```bash
# Compilar e executar a aplicação console
mvn -q compile exec:java
```

Executando a partir da raiz do repositório:

```bash
# Compilar e executar sem mudar de diretório
mvn -q -f e2e-tests/java/pom.xml compile exec:java

# Resolver e verificar dependências baixadas
mvn -f e2e-tests/java/pom.xml dependency:resolve

# Limpar artefatos compilados
mvn -f e2e-tests/java/pom.xml clean
```

### Saída esperada

```text
Universal: active-customer-code-in-the-stock -> actv-cstm-cd-the-stck
Custom: customer-code -> cstm-cdg
Configurable: customer -> cs
```
