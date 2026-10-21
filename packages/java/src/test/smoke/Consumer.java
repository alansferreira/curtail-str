import java.util.Collections;
import local.abbrev.Abbrev;

public class Consumer {
    public static void main(String[] args) {
        if (!"cdg-clnt".equals(Abbrev.abbrev("codigo-do-cliente"))) {
            throw new AssertionError("Universal JAR consumer failed");
        }
        Abbrev.Options options = Abbrev.Options.builder()
            .mode(Abbrev.Mode.CUSTOM)
            .replacements(Collections.singletonMap("code", "cdg")).build();
        if (!"cdg".equals(Abbrev.abbrev("code", options))) {
            throw new AssertionError("Custom JAR consumer failed");
        }
        System.out.println("Installed JAR consumer OK");
    }
}
