package local.abbreviate;

import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Pattern;

/** Pure, dictionary-free identifier abbreviation. */
public final class Abbreviate {
    private static final Pattern SEPARATORS = Pattern.compile(
        "[-_\\x{0009}-\\x{000d}\\x{0020}\\x{0085}\\x{00a0}\\x{1680}"
        + "\\x{2000}-\\x{200a}\\x{2028}\\x{2029}\\x{202f}\\x{205f}\\x{3000}]+");

    private Abbreviate() {}

    public enum Mode { UNIVERSAL, CUSTOM, CONFIGURABLE }

    /** Immutable options; use builder() to distinguish omitted and explicit limits. */
    public static final class Options {
        private final Mode mode;
        private final Map<String, String> replacements;
        private final Long minimum;
        private final Long preservation;
        private final Long maximum;

        private Options(Builder builder) {
            mode = builder.mode;
            replacements = builder.replacements == null ? null
                : Collections.unmodifiableMap(new HashMap<>(builder.replacements));
            minimum = builder.minimum;
            preservation = builder.preservation;
            maximum = builder.maximum;
        }

        public static Builder builder() { return new Builder(); }

        public static final class Builder {
            private Mode mode = Mode.UNIVERSAL;
            private Map<String, String> replacements;
            private Long minimum;
            private Long preservation;
            private Long maximum;

            private Builder() {}

            public Builder mode(Mode value) {
                if (value == null) throw new IllegalArgumentException("Mode cannot be null");
                mode = value;
                return this;
            }

            public Builder replacements(Map<String, String> value) {
                if (value == null) throw new IllegalArgumentException("Map cannot be null");
                replacements = value;
                return this;
            }

            public Builder minWordLength(long value) { minimum = value; return this; }
            public Builder preserveWordLength(long value) { preservation = value; return this; }
            public Builder maxWordLength(long value) { maximum = value; return this; }
            public Options build() { return new Options(this); }
        }
    }

    private static void validString(String value) {
        if (value == null) throw new IllegalArgumentException("Expected a Unicode string");
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (Character.isHighSurrogate(c)) {
                if (++i >= value.length() || !Character.isLowSurrogate(value.charAt(i))) {
                    throw new IllegalArgumentException("Unpaired surrogate");
                }
            } else if (Character.isLowSurrogate(c)) {
                throw new IllegalArgumentException("Unpaired surrogate");
            }
        }
    }

    private static String normalize(String value) {
        StringBuilder result = new StringBuilder();
        value.codePoints().forEach(cp ->
            result.append(new String(Character.toChars(cp)).toLowerCase(Locale.ROOT)));
        return Normalizer.normalize(result, Normalizer.Form.NFC);
    }

    private static boolean mark(int cp) {
        int type = Character.getType(cp);
        return type == Character.NON_SPACING_MARK || type == Character.COMBINING_SPACING_MARK
            || type == Character.ENCLOSING_MARK;
    }

    private static String compress(String word, int maximum) {
        int first = word.codePointAt(0);
        int[] rest = Normalizer.normalize(
            word.substring(Character.charCount(first)), Normalizer.Form.NFD).codePoints().toArray();
        StringBuilder tail = new StringBuilder();
        boolean removing = false;
        for (int cp : rest) {
            if (cp == 'a' || cp == 'e' || cp == 'i' || cp == 'o' || cp == 'u') {
                removing = true;
            } else if (!(removing && mark(cp))) {
                tail.appendCodePoint(cp);
                removing = false;
            }
        }
        int[] combined = (new String(Character.toChars(first))
            + Normalizer.normalize(tail, Normalizer.Form.NFC)).codePoints().toArray();
        StringBuilder result = new StringBuilder();
        int previous = -1;
        int count = 0;
        for (int cp : combined) {
            if (cp != previous || !Character.isLetter(cp)) {
                if (count++ == maximum) break;
                result.appendCodePoint(cp);
            }
            previous = cp;
        }
        return result.toString();
    }

    private static int limit(Long value, int fallback, Mode mode) {
        if (value == null) return fallback;
        if (mode != Mode.CONFIGURABLE) {
            throw new IllegalArgumentException("Limits require configurable mode");
        }
        if (value < 1 || value > Integer.MAX_VALUE) {
            throw new IllegalArgumentException("Limits must be between 1 and 2147483647");
        }
        return value.intValue();
    }

    public static String abbreviate(String input) {
        return abbreviate(input, null);
    }

    /** Null input returns empty; invalid options throw IllegalArgumentException. */
    public static String abbreviate(String input, Options supplied) {
        Options options = supplied == null ? Options.builder().build() : supplied;
        if (options.mode == Mode.UNIVERSAL && options.replacements != null) {
            throw new IllegalArgumentException("Replacements require custom or configurable mode");
        }
        int minimum = limit(options.minimum, 3, options.mode);
        int preservation = limit(options.preservation, 3, options.mode);
        int maximum = limit(options.maximum, 4, options.mode);
        Map<String, String> replacements = new HashMap<>();
        if (options.replacements != null) {
            for (Map.Entry<String, String> entry : options.replacements.entrySet()) {
                validString(entry.getKey());
                validString(entry.getValue());
                String key = normalize(entry.getKey());
                if (key.isEmpty() || SEPARATORS.matcher(key).find() || replacements.containsKey(key)) {
                    throw new IllegalArgumentException("Invalid or colliding replacement key");
                }
                replacements.put(key, entry.getValue());
            }
        }
        if (input == null) return "";
        validString(input);
        List<String> output = new ArrayList<>();
        for (String word : SEPARATORS.split(normalize(input))) {
            if (word.isEmpty()) continue;
            String result;
            if (replacements.containsKey(word)) {
                result = replacements.get(word);
            } else {
                int length = word.codePointCount(0, word.length());
                if (length < minimum) continue;
                result = length <= preservation ? word : compress(word, maximum);
            }
            if (!result.isEmpty()) output.add(result);
        }
        return String.join("-", output);
    }
}
