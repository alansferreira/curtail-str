package local.abrev;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import org.junit.Test;
import static org.junit.Assert.*;

public class AbrevTest {
    private static Abrev.Options options(JsonObject object) {
        Abrev.Options.Builder builder = Abrev.Options.builder();
        if (object.has("mode")) {
            builder.mode(Abrev.Mode.valueOf(object.get("mode").getAsString().toUpperCase(Locale.ROOT)));
        }
        if (object.has("replacements")) {
            Map<String, String> replacements = new HashMap<>();
            for (Map.Entry<String, JsonElement> entry : object.getAsJsonObject("replacements").entrySet()) {
                replacements.put(entry.getKey(), entry.getValue().getAsString());
            }
            builder.replacements(replacements);
        }
        if (object.has("minWordLength")) builder.minWordLength(object.get("minWordLength").getAsLong());
        if (object.has("preserveWordLength")) builder.preserveWordLength(object.get("preserveWordLength").getAsLong());
        if (object.has("maxWordLength")) builder.maxWordLength(object.get("maxWordLength").getAsLong());
        return builder.build();
    }

    @Test public void sharedContract() throws Exception {
        JsonArray cases;
        try (Reader reader = Files.newBufferedReader(
                Paths.get(System.getProperty("contract.path")), StandardCharsets.UTF_8)) {
            cases = JsonParser.parseReader(reader).getAsJsonArray();
        }
        for (JsonElement element : cases) {
            JsonObject item = element.getAsJsonObject();
            String name = item.get("name").getAsString();
            boolean error = item.has("error") && item.get("error").getAsBoolean();
            String snapshot = item.toString();
            try {
                String input = item.get("input").isJsonNull() ? null : item.get("input").getAsString();
                Abrev.Options supplied = options(
                    item.has("options") ? item.getAsJsonObject("options") : new JsonObject());
                String result = Abrev.abrev(input, supplied);
                if (error) fail(name + ": expected error");
                assertEquals(name, item.get("expected").getAsString(), result);
                assertEquals(name, result, Abrev.abrev(input, supplied));
            } catch (IllegalArgumentException ex) {
                if (!error) throw new AssertionError(name, ex);
            }
            assertEquals(name + ": fixture mutated", snapshot, item.toString());
        }
    }

    @Test public void nativeContract() {
        assertEquals("cdg", Abrev.abrev("codigo"));
        assertEquals("", Abrev.abrev(null));
        assertThrows(IllegalArgumentException.class,
            () -> Abrev.abrev("\ud800"));
        assertThrows(IllegalArgumentException.class,
            () -> Abrev.Options.builder().mode(null));
        assertThrows(IllegalArgumentException.class,
            () -> Abrev.Options.builder().replacements(null));
        Map<String, String> replacements = new HashMap<>();
        replacements.put("CODIGO", "OK");
        Abrev.Options supplied = Abrev.Options.builder()
            .mode(Abrev.Mode.CUSTOM).replacements(replacements).build();
        replacements.put("CODIGO", "CHANGED");
        assertEquals("OK", Abrev.abrev("codigo", supplied));
        assertEquals("CHANGED", replacements.get("CODIGO"));
        replacements.put("abc", "\ud800");
        Abrev.Options invalid = Abrev.Options.builder()
            .mode(Abrev.Mode.CUSTOM).replacements(replacements).build();
        assertThrows(IllegalArgumentException.class,
            () -> Abrev.abrev("", invalid));
    }
}
