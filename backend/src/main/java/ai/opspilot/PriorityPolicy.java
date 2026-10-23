package ai.opspilot;

/** ITIL-style priority derivation from recorded impact and urgency. */
public final class PriorityPolicy {
  private PriorityPolicy() {}
  public static String derive(String impact,String urgency) {
    if(impact==null||urgency==null) throw new IllegalArgumentException("Impact and urgency are required");
    return switch(impact+":"+urgency) {
      case "HIGH:HIGH" -> "P1";
      case "HIGH:MEDIUM","MEDIUM:HIGH" -> "P2";
      case "HIGH:LOW","MEDIUM:MEDIUM","LOW:HIGH" -> "P3";
      case "MEDIUM:LOW","LOW:MEDIUM" -> "P4";
      case "LOW:LOW" -> "P5";
      default -> throw new IllegalArgumentException("Impact and urgency must be HIGH, MEDIUM, or LOW");
    };
  }
}
