package ai.opspilot;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import java.util.*;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(Api.class)
class ApiTest {
  @Autowired MockMvc mvc;
  @MockitoBean IncidentService incidents;
  @MockitoBean AgentClient agent;
  @MockitoBean ItsmService itsm;

  @Test
  void deniesRequestsWithoutToken() throws Exception {
    mvc.perform(get("/api/incidents")).andExpect(status().isUnauthorized());
    verifyNoInteractions(incidents);
  }

  @Test
  void listsWithToken() throws Exception {
    when(incidents.list()).thenReturn(List.of());
    mvc.perform(get("/api/incidents").header("Authorization", "Bearer local-demo-token"))
        .andExpect(status().isOk())
        .andExpect(content().json("[]"));
  }

  @Test
  void invalidIncidentNeverReachesService() throws Exception {
    mvc.perform(
            post("/api/incidents")
                .header("Authorization", "Bearer local-demo-token")
                .contentType(MediaType.APPLICATION_JSON)
                .content(
                    "{\"service\":\"x\",\"title\":\"\",\"description\":\"x\",\"severity\":\"P0\"}"))
        .andExpect(status().isBadRequest());
    verifyNoInteractions(incidents);
  }

  @Test
  void invalidDecisionNeverReachesService() throws Exception {
    mvc.perform(
            post("/api/incidents/" + UUID.randomUUID() + "/approval")
                .header("Authorization", "Bearer local-demo-token")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"decision\":\"BYPASS\",\"reviewer\":\"x\",\"note\":\"x\"}"))
        .andExpect(status().isBadRequest());
    verifyNoInteractions(incidents);
  }

  @Test
  void validIncidentCallsService() throws Exception {
    when(incidents.create(any())).thenReturn(Map.of("status", "OPEN"));
    mvc.perform(
            post("/api/incidents")
                .header("Authorization", "Bearer local-demo-token")
                .contentType(MediaType.APPLICATION_JSON)
                .content(
                    "{\"service\":\"payment-service\",\"title\":\"Timeout\",\"description\":\"Pool"
                        + " exhausted\",\"severity\":\"P1\"}"))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.status").value("OPEN"));
    verify(incidents).create(any());
  }
}
