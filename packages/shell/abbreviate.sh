#!/bin/sh

case $# in
    1) ;;
    *) printf '%s\n' 'Usage: sh abbreviate.sh "text" | --help' >&2; exit 2 ;;
esac
if [ "$1" = '--help' ]; then
    printf '%s\n' 'Usage: sh abbreviate.sh "text"' \
        'Universal mode. Requires POSIX awk; Unicode behavior depends on awk and locale.'
    exit 0
fi

# Pass data through stdin, never through awk source or -v escape processing.
printf '%s\n' "$1" | awk '
function abbreviate(word,    size, first, rest, result, previous, char, i) {
    size = length(word)
    if (size < 3) return ""
    if (size == 3) return word
    first = substr(word, 1, 1)
    rest = substr(word, 2)
    gsub(/[aeiou]/, "", rest)
    word = first rest
    result = ""
    previous = ""
    for (i = 1; i <= length(word); i++) {
        char = substr(word, i, 1)
        if (char != previous || char !~ /^[[:alpha:]]$/) result = result char
        previous = char
    }
    return substr(result, 1, 4)
}
{
    line = tolower($0)
    gsub(/[-_[:space:]]+/, " ", line)
    count = split(line, words, " ")
    for (position = 1; position <= count; position++) {
        result = abbreviate(words[position])
        if (result != "") {
            printf "%s%s", separator, result
            separator = "-"
        }
    }
}
END { printf "\n" }
'
