package ai.opspilot;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.jdbc.core.JdbcTemplate;

class AgentClientTest {
  @SuppressWarnings("unchecked")
  @Test
  void startupSeedsReservedBuiltInRunbooksThroughPersistencePath() {
    JdbcTemplate db = mock(JdbcTemplate.class);
    when(db.queryForList(
            startsWith("SELECT id FROM runbook_chunks"), (Object[]) any()))
        .thenReturn(List.of());
    AgentClient agent =
        new AgentClient(
            db,
            mock(LabClient.class),
            new ObjectMapper(),
            mock(ObjectProvider.class),
            mock(ObjectProvider.class),
            "demo",
            "text-embedding-3-small");

    agent.seedRunbooks();

    verify(db, times(12))
        .update(
            startsWith("INSERT INTO runbooks"),
            any(),
            any(),
            any(),
            any(),
            any(),
            any());
    verify(db, never()).update(startsWith("INSERT INTO runbooks"), startsWith("rb-"));
  }
}
