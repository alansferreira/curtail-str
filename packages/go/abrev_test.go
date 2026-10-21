package abrev

import (
	"encoding/json"
	"os"
	"reflect"
	"testing"
)

func TestSharedContract(t *testing.T) {
	data, err := os.ReadFile("../../spec/cases.json")
	if err != nil {
		t.Fatal(err)
	}
	var cases []struct {
		Name    string
		Input   *string
		Options struct {
			Mode               Mode
			Replacements       map[string]string
			MinWordLength      *int64
			PreserveWordLength *int64
			MaxWordLength      *int64
		}
		Expected string
		Error    bool
	}
	if err := json.Unmarshal(data, &cases); err != nil {
		t.Fatal(err)
	}
	for _, item := range cases {
		t.Run(item.Name, func(t *testing.T) {
			input := ""
			if item.Input != nil {
				input = *item.Input
			}
			options := Options{
				Mode: item.Options.Mode, Replacements: item.Options.Replacements,
				MinWordLength:      item.Options.MinWordLength,
				PreserveWordLength: item.Options.PreserveWordLength,
				MaxWordLength:      item.Options.MaxWordLength,
			}
			before, err := json.Marshal(options)
			if err != nil {
				t.Fatal(err)
			}
			got, err := Abrev(input, options)
			if item.Error {
				if err == nil {
					t.Fatal("expected error")
				}
			} else if err != nil || got != item.Expected {
				t.Fatalf("got %q, %v; want %q", got, err, item.Expected)
			}
			if !item.Error {
				repeated, repeatErr := Abrev(input, options)
				if repeatErr != nil || repeated != got {
					t.Fatalf("non-repeatable result: %q, %v", repeated, repeatErr)
				}
			}
			after, err := json.Marshal(options)
			if err != nil {
				t.Fatal(err)
			}
			if !reflect.DeepEqual(before, after) {
				t.Fatal("options mutated")
			}
		})
	}
}

func TestNativeContract(t *testing.T) {
	if got, err := Abrev("codigo"); err != nil || got != "cdg" {
		t.Fatalf("default call: %q, %v", got, err)
	}
	if _, err := Abrev("", Options{}, Options{}); err == nil {
		t.Fatal("expected error for multiple options")
	}
	if _, err := Abrev("\xff"); err == nil {
		t.Fatal("expected error for invalid UTF-8")
	}
	for _, replacements := range []map[string]string{
		{"abc": "\xff"}, {"\xff": "x"},
	} {
		if _, err := Abrev("", Options{
			Mode: Custom, Replacements: replacements,
		}); err == nil {
			t.Fatal("expected error for invalid UTF-8 in map")
		}
	}
}
