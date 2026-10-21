import java.util.Collections;
import local.curtailstr.CurtailStr;

public class Consumer {
    public static void main(String[] args) {
        if (!"cdg-clnt".equals(CurtailStr.curtailStr("codigo-do-cliente"))) {
            throw new AssertionError("Universal JAR consumer failed");
        }
        CurtailStr.Options options = CurtailStr.Options.builder()
            .mode(CurtailStr.Mode.CUSTOM)
            .replacements(Collections.singletonMap("code", "cdg")).build();
        if (!"cdg".equals(CurtailStr.curtailStr("code", options))) {
            throw new AssertionError("Custom JAR consumer failed");
        }
        System.out.println("Installed JAR consumer OK");
    }
}
