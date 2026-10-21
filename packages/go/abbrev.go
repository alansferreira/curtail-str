// Package abbrev provides pure, dictionary-free identifier abbreviation.
package abbrev

import (
	"fmt"
	"strings"
	"unicode"
	"unicode/utf8"

	"golang.org/x/text/unicode/norm"
)

// Mode selects the algorithm's customization policy.
type Mode string

const (
	Universal    Mode = "universal"
	Custom       Mode = "custom"
	Configurable Mode = "configurable"
)

// Options has universal defaults. A nil map or limit means omitted.
// Limits are independent and only permitted in Configurable mode.
type Options struct {
	Mode               Mode
	Replacements       map[string]string
	MinWordLength      *int64
	PreserveWordLength *int64
	MaxWordLength      *int64
}

func separator(r rune) bool {
	return r == '-' || r == '_' || r >= 0x09 && r <= 0x0d ||
		r == 0x20 || r == 0x85 || r == 0xa0 || r == 0x1680 ||
		r >= 0x2000 && r <= 0x200a || r == 0x2028 || r == 0x2029 ||
		r == 0x202f || r == 0x205f || r == 0x3000
}

func normalize(value string) string {
	var result strings.Builder
	for _, r := range value {
		if r == '\u0130' {
			result.WriteString("i\u0307")
		} else {
			result.WriteRune(unicode.ToLower(r))
		}
	}
	return norm.NFC.String(result.String())
}

func compress(word string, maximum int) string {
	runes := []rune(word)
	var tail strings.Builder
	removing := false
	for _, r := range norm.NFD.String(string(runes[1:])) {
		if strings.ContainsRune("aeiou", r) {
			removing = true
		} else if !(removing && unicode.IsMark(r)) {
			tail.WriteRune(r)
			removing = false
		}
	}
	result := make([]rune, 0, len(runes))
	var previous rune
	for _, r := range string(runes[0]) + norm.NFC.String(tail.String()) {
		if r != previous || !unicode.IsLetter(r) {
			result = append(result, r)
		}
		previous = r
	}
	if len(result) > maximum {
		result = result[:maximum]
	}
	return string(result)
}

// Abbrev abbrevs input without mutating options or maps.
// Supply zero or one Options value. Invalid options and invalid UTF-8 return
// an error, even for empty input. The zero Mode means Universal.
func Abbrev(input string, supplied ...Options) (string, error) {
	if len(supplied) > 1 {
		return "", fmt.Errorf("expected at most one Options value")
	}
	options := Options{}
	if len(supplied) == 1 {
		options = supplied[0]
	}
	mode := options.Mode
	if mode == "" {
		mode = Universal
	}
	if mode != Universal && mode != Custom && mode != Configurable {
		return "", fmt.Errorf("unknown mode: %q", mode)
	}
	if mode == Universal && options.Replacements != nil {
		return "", fmt.Errorf("replacements require custom or configurable mode")
	}
	limits := [3]int{3, 3, 4}
	for i, value := range []*int64{
		options.MinWordLength, options.PreserveWordLength, options.MaxWordLength,
	} {
		if value == nil {
			continue
		}
		if mode != Configurable {
			return "", fmt.Errorf("limits require configurable mode")
		}
		if *value < 1 || *value > 2147483647 {
			return "", fmt.Errorf("limit %d must be between 1 and 2147483647", i)
		}
		limits[i] = int(*value)
	}
	replacements := make(map[string]string, len(options.Replacements))
	for key, value := range options.Replacements {
		if !utf8.ValidString(key) || !utf8.ValidString(value) {
			return "", fmt.Errorf("replacement keys and values must be valid UTF-8")
		}
		normalized := normalize(key)
		if normalized == "" || strings.ContainsFunc(normalized, separator) {
			return "", fmt.Errorf("invalid replacement key: %q", key)
		}
		if _, exists := replacements[normalized]; exists {
			return "", fmt.Errorf("colliding replacement key: %q", key)
		}
		replacements[normalized] = value
	}
	if !utf8.ValidString(input) {
		return "", fmt.Errorf("input must be valid UTF-8")
	}
	output := make([]string, 0)
	for _, word := range strings.FieldsFunc(normalize(input), separator) {
		result, mapped := replacements[word]
		if !mapped {
			length := utf8.RuneCountInString(word)
			if length < limits[0] {
				continue
			}
			result = word
			if length > limits[1] {
				result = compress(word, limits[2])
			}
		}
		if result != "" {
			output = append(output, result)
		}
	}
	return strings.Join(output, "-"), nil
}
