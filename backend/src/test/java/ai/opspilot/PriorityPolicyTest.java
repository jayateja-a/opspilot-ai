package ai.opspilot;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class PriorityPolicyTest {
  @Test void derivesEveryImpactUrgencyCombination() {
    String[][] cases={{"HIGH","HIGH","P1"},{"HIGH","MEDIUM","P2"},{"HIGH","LOW","P3"},{"MEDIUM","HIGH","P2"},{"MEDIUM","MEDIUM","P3"},{"MEDIUM","LOW","P4"},{"LOW","HIGH","P3"},{"LOW","MEDIUM","P4"},{"LOW","LOW","P5"}};
    for(String[] c:cases)assertEquals(c[2],PriorityPolicy.derive(c[0],c[1]),c[0]+" impact / "+c[1]+" urgency");
  }
  @Test void rejectsUnknownImpactOrUrgency() {
    assertThrows(IllegalArgumentException.class,()->PriorityPolicy.derive("P0","HIGH"));
    assertThrows(IllegalArgumentException.class,()->PriorityPolicy.derive("LOW",null));
  }
}
