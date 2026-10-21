# Curtail-str para Python

Python 3.11 ou superior, sem dependencias de runtime.

```python
from curtail_str import curtail_str

assert curtail_str("codigo-do-cliente") == "cdg-clnt"
assert curtail_str("code-in-the-stock", {
    "mode": "custom",
    "replacements": {"the": "", "code": "cdg"},
}) == "cdg-stck"
assert curtail_str("cliente", {
    "mode": "configurable", "max_word_length": 2,
}) == "cl"
```

`None` retorna `""`. Opcoes omitidas ou `None` usam os padroes. Argumentos
invalidos geram `TypeError` ou `ValueError`, inclusive para entrada vazia.
Mapas associam strings a resultados finais literais; `""` remove uma palavra.

O modo padrao `universal` nao aceita mapa. Os limites inteiros positivos
`min_word_length` (3), `preserve_word_length` (3) e `max_word_length` (4) sao
independentes e exclusivos de `configurable`. Palavras preservadas e valores
do mapa nao sao truncados. Nenhum argumento e modificado.

Esta heuristica nao traduz palavras nem garante unicidade. Conta pontos de
codigo Unicode e preserva a inicial das palavras comprimidas.
`code` vira `cd` e `the` permanece `the` por padrao.

Para desenvolver, instale com `python -m pip install -e .` e execute
`python -m unittest discover -s tests -v`. Os testes de contrato requerem o
corpus da raiz do monorepositorio; o pacote instalado nao depende dele.
