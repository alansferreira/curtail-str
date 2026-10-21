import java.util.Collections;
import local.abrev.Abrev;

public class Consumer {
    public static void main(String[] args) {
        if (!"cdg-clnt".equals(Abrev.abrev("codigo-do-cliente"))) {
            throw new AssertionError("Universal JAR consumer failed");
        }
        Abrev.Options options = Abrev.Options.builder()
            .mode(Abrev.Mode.CUSTOM)
            .replacements(Collections.singletonMap("code", "cdg")).build();
        if (!"cdg".equals(Abrev.abrev("code", options))) {
            throw new AssertionError("Custom JAR consumer failed");
        }
        System.out.println("Installed JAR consumer OK");
    }
}
