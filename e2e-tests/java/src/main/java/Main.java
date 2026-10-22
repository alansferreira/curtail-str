import java.util.Collections;
import local.curtailstr.CurtailStr;

public class Main {
    public static void main(String[] args) {
        String sampleInput = "active-customer-code-in-the-stock";
        String universal = CurtailStr.curtailStr(sampleInput);
        System.out.println("Universal: " + sampleInput + " -> " + universal + "");

        CurtailStr.Options customOptions = CurtailStr.Options.builder()
            .mode(CurtailStr.Mode.CUSTOM)
            .replacements(Collections.singletonMap("code", "cdg"))
            .build();
        sampleInput = "customer-code";
        String custom = CurtailStr.curtailStr(sampleInput, customOptions);
        System.out.println("Custom: " + sampleInput + " -> " + custom + "");
        
        CurtailStr.Options configurableOptions = CurtailStr.Options.builder()
            .mode(CurtailStr.Mode.CONFIGURABLE)
            .maxWordLength(2)
            .build();
        sampleInput = "customer";
        String configurable = CurtailStr.curtailStr(sampleInput, configurableOptions);
        
        System.out.println("Configurable: " + sampleInput + " -> " + configurable + "");
    }
}
