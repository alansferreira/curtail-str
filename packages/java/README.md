# curtail-str for Java

Compatible with Eclipse Temurin Java 8 or later. No runtime dependencies.

## Install from source

Install `io.github.alansferreira:curtail-str:0.1.1` into the local Maven repository:

```sh
mvn -B -ntp -f /path/to/curtail-str/packages/java/pom.xml install
```

## Usage

```java
import local.curtailstr.CurtailStr;

String universal = CurtailStr.curtailStr("active-customer-code-in-the-stock");
// actv-cstm-cd-the-stck
String configurable = CurtailStr.curtailStr("customer",
    CurtailStr.Options.builder()
        .mode(CurtailStr.Mode.CONFIGURABLE)
        .maxWordLength(2)
        .build());
// cs
```

For replacements, use `Mode.CUSTOM` and
`.replacements(Map<String, String>)`. An empty value removes a word.
Other values are literal results without compression or truncation.
`Options` makes a defensive copy of the map when `build()` is called.

Null input returns `""`; null options use defaults. Invalid arguments throw
`IllegalArgumentException`, even for empty input. The builder rejects
explicitly supplied null modes and maps.

`minWordLength` (3), `preserveWordLength` (3), and `maxWordLength` (4) accept
`long` integers from 1 through 2147483647. Limits are independent and available
only in `CONFIGURABLE`. Replacement maps are accepted only in `CUSTOM` and
`CONFIGURABLE`.

The heuristic does not translate words or guarantee uniqueness. By default,
`code` becomes `cd` and `the` remains `the`. Lengths use Unicode code points,
not UTF-16 units.

## Development

Run `mvn -B -ntp verify` from this directory.
The output JAR is `target/curtail-str-0.1.1.jar`.
Tests use fixtures at the repository root; the JAR does not depend on them.

See the [algorithm contract](https://github.com/alansferreira/curtail-str/blob/main/spec/algorithm.md) for complete semantics.
