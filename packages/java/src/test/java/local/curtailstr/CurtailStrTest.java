package local.curtailstr;

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

public class CurtailStrTest {
    private static CurtailStr.Options options(JsonObject object) {
        CurtailStr.Options.Builder builder = CurtailStr.Options.builder();
        if (object.has("mode")) {
            builder.mode(CurtailStr.Mode.valueOf(object.get("mode").getAsString().toUpperCase(Locale.ROOT)));
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
                CurtailStr.Options supplied = options(
                    item.has("options") ? item.getAsJsonObject("options") : new JsonObject());
                String result = CurtailStr.curtailStr(input, supplied);
                if (error) fail(name + ": expected error");
                assertEquals(name, item.get("expected").getAsString(), result);
                assertEquals(name, result, CurtailStr.curtailStr(input, supplied));
            } catch (IllegalArgumentException ex) {
                if (!error) throw new AssertionError(name, ex);
            }
            assertEquals(name + ": fixture mutated", snapshot, item.toString());
        }
    }

    @Test public void nativeContract() {
        assertEquals("cdg", CurtailStr.curtailStr("codigo"));
        assertEquals("", CurtailStr.curtailStr(null));
        assertThrows(IllegalArgumentException.class,
            () -> CurtailStr.curtailStr("\ud800"));
        assertThrows(IllegalArgumentException.class,
            () -> CurtailStr.Options.builder().mode(null));
        assertThrows(IllegalArgumentException.class,
            () -> CurtailStr.Options.builder().replacements(null));
        Map<String, String> replacements = new HashMap<>();
        replacements.put("CODIGO", "OK");
        CurtailStr.Options supplied = CurtailStr.Options.builder()
            .mode(CurtailStr.Mode.CUSTOM).replacements(replacements).build();
        replacements.put("CODIGO", "CHANGED");
        assertEquals("OK", CurtailStr.curtailStr("codigo", supplied));
        assertEquals("CHANGED", replacements.get("CODIGO"));
        replacements.put("abc", "\ud800");
        CurtailStr.Options invalid = CurtailStr.Options.builder()
            .mode(CurtailStr.Mode.CUSTOM).replacements(replacements).build();
        assertThrows(IllegalArgumentException.class,
            () -> CurtailStr.curtailStr("", invalid));
    }
}
