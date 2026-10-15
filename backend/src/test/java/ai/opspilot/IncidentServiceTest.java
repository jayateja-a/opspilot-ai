package ai.opspilot;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.*;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;

class IncidentServiceTest {
  @Test
  void agentFailurePersistsRetryableState() {
    JdbcTemplate db = mock(JdbcTemplate.class);
    AgentClient agent = mock(AgentClient.class);
    UUID id = UUID.randomUUID();
    var row = new HashMap<String, Object>();
    row.put("id", id);
    row.put("service", "payment-service");
    row.put("description", "Timeout");
    row.put("scenario_id", "db-pool");
    row.put("status", "OPEN");
    when(db.queryForList(startsWith("SELECT * FROM incidents"), eq(id)))
        .thenAnswer(x -> List.of(new HashMap<>(row)));
    when(db.update(startsWith("UPDATE incidents SET status='ANALYSIS_FAILED'"), eq(id)))
        .thenAnswer(
            x -> {
              row.put("status", "ANALYSIS_FAILED");
              return 1;
            });
    when(agent.analyze(anyMap())).thenThrow(new RuntimeException("timeout"));
    var service = new IncidentService(db, new ObjectMapper(), agent);
    assertEquals("ANALYSIS_FAILED", service.analyze(id).get("status"));
    verify(db).update(startsWith("UPDATE incidents SET status='ANALYSIS_FAILED'"), eq(id));
    verify(db)
        .update(startsWith("INSERT INTO audit_events"), eq(id), eq("ANALYSIS_FAILED"), anyString());
  }
}
