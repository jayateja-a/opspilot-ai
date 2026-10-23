package ai.opspilot;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.util.*;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.client.ResourceAccessException;

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
    when(db.update(
            startsWith("UPDATE incidents SET status='ANALYSIS_FAILED'"), anyString(), eq(id)))
        .thenAnswer(
            x -> {
              row.put("status", "ANALYSIS_FAILED");
              row.put("last_error", x.getArgument(1));
              return 1;
            });
    when(agent.analyze(anyMap())).thenThrow(new RuntimeException("timeout"));
    var service = new IncidentService(db, new ObjectMapper(), agent);
    assertEquals("ANALYSIS_FAILED", service.analyze(id).get("status"));
    assertEquals(
        "Investigation failed. Check the backend logs for the underlying cause, then retry analysis.",
        row.get("last_error"));
    verify(db)
        .update(startsWith("UPDATE incidents SET status='ANALYSIS_FAILED'"), anyString(), eq(id));
    verify(db)
        .update(startsWith("INSERT INTO audit_events"), eq(id), eq("ANALYSIS_FAILED"), anyString());
  }

  @Test
  void classifiesLabAndDatabaseFailuresWithoutExposingExceptionText() {
    assertTrue(
        IncidentService.analysisFailureMessage(
                new ResourceAccessException("private-host:8081", new IOException("secret")))
            .contains("synthetic service lab"));
    assertTrue(
        IncidentService.analysisFailureMessage(
                new org.springframework.jdbc.UncategorizedSQLException(
                    "query", "private SQL", new java.sql.SQLException("details")))
            .contains("PostgreSQL health"));
    assertFalse(
        IncidentService.analysisFailureMessage(new ResourceAccessException("private-host"))
            .contains("private-host"));
  }
}
