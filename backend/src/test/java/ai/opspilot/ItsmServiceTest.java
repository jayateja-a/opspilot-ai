package ai.opspilot;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import java.util.*;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.server.ResponseStatusException;

class ItsmServiceTest {
  @Test void changeLifecycleRejectsSkippedAuthorizationAndAcceptsAssessment() {
    JdbcTemplate db=mock(JdbcTemplate.class); ItsmService service=new ItsmService(db,new com.fasterxml.jackson.databind.ObjectMapper()); UUID id=UUID.randomUUID();
    when(db.queryForList(contains("FOR UPDATE"),eq(id))).thenReturn(List.of(Map.of("status","DRAFT")));
    assertThrows(ResponseStatusException.class,()->service.transitionChange(id,new Api.ChangeTransition("AUTHORIZED","CAB")));
    verify(db,never()).update(startsWith("UPDATE change_records"),any(),any(),any());
    when(db.queryForMap(contains("SELECT * FROM change_records"),eq(id))).thenReturn(Map.of("id",id,"status","ASSESSMENT"));
    assertEquals("ASSESSMENT",service.transitionChange(id,new Api.ChangeTransition("ASSESSMENT","owner")).get("status"));
    verify(db).update(startsWith("UPDATE change_records"),eq("ASSESSMENT"),eq("owner"),eq(id));
  }

  @Test void rcaReviewOnlyPromotesApprovedDraftToRetrievalKnowledge() {
    JdbcTemplate db=mock(JdbcTemplate.class); ItsmService service=new ItsmService(db,new com.fasterxml.jackson.databind.ObjectMapper()); UUID id=UUID.randomUUID();
    when(db.queryForList(contains("rca_documents"),eq(id))).thenReturn(List.of(Map.of("status","DRAFT","incident_id",UUID.randomUUID())));
    when(db.queryForMap(contains("SELECT * FROM rca_documents"),eq(id))).thenReturn(Map.of("id",id,"status","APPROVED"));
    var result=service.reviewRca(id,new Api.RcaReview(true,"reviewer"));
    assertEquals("APPROVED",result.get("status"));
    verify(db).update(startsWith("UPDATE rca_documents"),eq("APPROVED"),eq("reviewer"),eq(id));
    verify(db).update(contains("INSERT INTO runbooks"),eq("rca-"+id),eq(id));
  }

  @Test void reviewedRcaCannotBePromotedAgain() {
    JdbcTemplate db=mock(JdbcTemplate.class); ItsmService service=new ItsmService(db,new com.fasterxml.jackson.databind.ObjectMapper()); UUID id=UUID.randomUUID();
    when(db.queryForList(contains("rca_documents"),eq(id))).thenReturn(List.of(Map.of("status","REVIEWED")));
    assertThrows(ResponseStatusException.class,()->service.reviewRca(id,new Api.RcaReview(true,"reviewer")));
    verify(db,never()).update(startsWith("UPDATE rca_documents"),any(),any(),any());
  }
}
