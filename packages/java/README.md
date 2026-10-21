# Curtail-str para Java

Compativel com Eclipse Temurin Java 8 ou superior. Sem dependencias de runtime.

```java
import local.curtailstr.CurtailStr;

String universal = CurtailStr.curtailStr("codigo-do-cliente");
// cdg-clnt
String configurable = CurtailStr.curtailStr("cliente",
    CurtailStr.Options.builder()
        .mode(CurtailStr.Mode.CONFIGURABLE)
        .maxWordLength(2)
        .build());
// cl
```

Para personalizar, usar `Mode.CUSTOM` e
`.replacements(Map<String, String>)`. `""` como valor remove a palavra;
outros valores sao resultados finais literais, sem compressao ou corte.
`Options` faz copia defensiva do mapa ao executar `build()`.

Entrada `null` retorna `""`; opcoes `null` usam os padroes. Argumentos
invalidos geram `IllegalArgumentException`, inclusive para entrada vazia.
O builder rejeita modo e mapa nulos explicitamente fornecidos.

`minWordLength` (3), `preserveWordLength` (3) e `maxWordLength` (4) aceitam
inteiros `long` em 1..2147483647; sao independentes e exclusivos do modo
`CONFIGURABLE`. Mapa so e permitido em `CUSTOM` e `CONFIGURABLE`.

Nao ha traducao nem garantia de unicidade. `code` vira `cd` e `the` permanece
`the` por padrao. Comprimentos usam pontos de codigo, nao unidades UTF-16.

Build e testes: `mvn -B -ntp verify`. JAR: `target/curtail-str-0.1.0.jar`.
Coordenadas locais: `org.alf:curtail-str:0.1.0`. Os testes usam o
corpus da raiz do monorepositorio; o JAR nao depende dele.
