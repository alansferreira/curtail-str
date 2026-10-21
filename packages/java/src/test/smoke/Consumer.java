import java.util.Collections;
import local.abbreviate.Abbreviate;

public class Consumer {
    public static void main(String[] args) {
        if (!"cdg-clnt".equals(Abbreviate.encurtarChaveUniversal("codigo-do-cliente"))) {
            throw new AssertionError("Universal JAR consumer failed");
        }
        Abbreviate.Options options = Abbreviate.Options.builder()
            .mode(Abbreviate.Mode.CUSTOM)
            .replacements(Collections.singletonMap("code", "cdg")).build();
        if (!"cdg".equals(Abbreviate.encurtarChaveUniversal("code", options))) {
            throw new AssertionError("Custom JAR consumer failed");
        }
        System.out.println("Installed JAR consumer OK");
    }
}
