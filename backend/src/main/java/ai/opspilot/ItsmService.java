package ai.opspilot;

import java.util.*;
import org.springframework.jdbc.core.JdbcTemplate;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.boot.sql.init.dependency.DependsOnDatabaseInitialization;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;

/** Local ITSM records: configuration, problem, change and human-reviewed RCA. */
@Service
@DependsOnDatabaseInitialization
public class ItsmService {
  private final JdbcTemplate db;
  private final ObjectMapper json;
  public ItsmService(JdbcTemplate db,ObjectMapper json) { this.db = db; this.json=json; }

  @jakarta.annotation.PostConstruct
  public void seedConfigurationItems() {
    db.update("INSERT INTO configuration_items(id,name,ci_type,domain,health,attributes) VALUES ('payment-service','Payment API','APPLICATION','FINTECH','HEALTHY','{}'),('payment-db','Payment PostgreSQL','DATABASE','FINTECH','HEALTHY','{}'),('patient-record-service','Patient Record API','APPLICATION','HEALTHCARE','HEALTHY','{}'),('patient-record-db','Patient Records PostgreSQL','DATABASE','HEALTHCARE','HEALTHY','{}') ON CONFLICT(id) DO NOTHING");
  }
  public List<Map<String,Object>> configurationItems() { return db.queryForList("SELECT * FROM configuration_items ORDER BY domain,id"); }
  public List<Map<String,Object>> problems() { return db.queryForList("SELECT * FROM problem_records ORDER BY created_at DESC LIMIT 100"); }
  public List<Map<String,Object>> changes() { return db.queryForList("SELECT * FROM change_records ORDER BY created_at DESC LIMIT 100"); }
  public List<Map<String,Object>> rcas(UUID incidentId) { return db.queryForList("SELECT * FROM rca_documents WHERE incident_id=? ORDER BY created_at DESC", incidentId); }

  @Transactional
  public Map<String,Object> createProblem(Api.Problem request) {
    UUID id=UUID.randomUUID();
    db.update("INSERT INTO problem_records(id,ticket_number,title,description,root_cause,workaround) VALUES (?, 'PRB-' || nextval('ticket_number_seq'), ?, ?, ?, ?)", id, request.title(), request.description(), request.rootCause(), request.workaround());
    if (request.incidentId()!=null) { requireIncident(request.incidentId()); link("INCIDENT",request.incidentId().toString(),"PROBLEM",id.toString(),"RELATED_TO"); audit(request.incidentId(),"PROBLEM_CREATED",Map.of("problem_id",id.toString())); }
    return db.queryForMap("SELECT * FROM problem_records WHERE id=?",id);
  }
  @Transactional
  public Map<String,Object> createChange(Api.Change request) {
    UUID id=UUID.randomUUID();
    db.update("INSERT INTO change_records(id,ticket_number,title,description,change_type,risk,impact,implementation_plan,rollback_plan) VALUES (?, 'CHG-' || nextval('ticket_number_seq'), ?, ?, ?, ?, ?, ?, ?)", id, request.title(), request.description(), request.changeType(), request.risk(), request.impact(), request.implementationPlan(), request.rollbackPlan());
    if (request.incidentId()!=null) { requireIncident(request.incidentId()); link("INCIDENT",request.incidentId().toString(),"CHANGE",id.toString(),"PROPOSED_REMEDIATION"); audit(request.incidentId(),"CHANGE_CREATED",Map.of("change_id",id.toString())); }
    return db.queryForMap("SELECT * FROM change_records WHERE id=?",id);
  }
  @Transactional
  public Map<String,Object> transitionChange(UUID id, Api.ChangeTransition req) {
    var row=db.queryForList("SELECT * FROM change_records WHERE id=? FOR UPDATE",id).stream().findFirst().orElseThrow(()->new ResponseStatusException(HttpStatus.NOT_FOUND,"Change not found"));
    String from=Objects.toString(row.get("status")); String to=req.status();
    boolean valid=switch(from){case "DRAFT"->Set.of("ASSESSMENT","REJECTED").contains(to);case "ASSESSMENT"->Set.of("AUTHORIZED","REJECTED").contains(to);case "AUTHORIZED"->Set.of("SCHEDULED","REJECTED").contains(to);case "SCHEDULED"->Set.of("IMPLEMENTING","REJECTED").contains(to);case "IMPLEMENTING"->Set.of("REVIEW","REJECTED").contains(to);case "REVIEW"->Set.of("CLOSED","IMPLEMENTING").contains(to);default->false;};
    if(!valid) throw new ResponseStatusException(HttpStatus.CONFLICT,"Invalid change transition: "+from+" → "+to);
    db.update("UPDATE change_records SET status=?,reviewer=COALESCE(?,reviewer),updated_at=now() WHERE id=?",to,req.reviewer(),id);
    db.queryForList("SELECT source_id FROM record_links WHERE source_type='INCIDENT' AND target_type='CHANGE' AND target_id=?",id.toString()).forEach(link->audit(UUID.fromString(Objects.toString(link.get("source_id"))),"CHANGE_"+to,Map.of("change_id",id.toString(),"reviewer",Objects.toString(req.reviewer(),""))));
    return db.queryForMap("SELECT * FROM change_records WHERE id=?",id);
  }
  @Transactional
  public Map<String,Object> reviewRca(UUID rcaId, Api.RcaReview req) {
    var row=db.queryForList("SELECT * FROM rca_documents WHERE id=? FOR UPDATE",rcaId).stream().findFirst().orElseThrow(()->new ResponseStatusException(HttpStatus.NOT_FOUND,"RCA not found"));
    if(!"DRAFT".equals(row.get("status"))) throw new ResponseStatusException(HttpStatus.CONFLICT,"Only draft RCAs can be reviewed");
    db.update("UPDATE rca_documents SET status=?,approved_by=?,updated_at=now() WHERE id=?",req.approve()?"APPROVED":"REVIEWED",req.reviewer(),rcaId);
    audit((UUID)row.get("incident_id"),req.approve()?"RCA_APPROVED":"RCA_REVIEWED",Map.of("rca_id",rcaId.toString(),"reviewer",req.reviewer()));
    if(req.approve()) db.update("INSERT INTO runbooks(id,service,title,content,action,risk) SELECT ?,i.service, r.title, COALESCE(r.body->>'summary','') || E'\\n' || COALESCE(r.body->>'reasoning',''), 'manual_review','LOW' FROM rca_documents r JOIN incidents i ON i.id=r.incident_id WHERE r.id=? ON CONFLICT(id) DO NOTHING","rca-"+rcaId,rcaId);
    return db.queryForMap("SELECT * FROM rca_documents WHERE id=?",rcaId);
  }
  private void link(String st,String si,String tt,String ti,String rel){db.update("INSERT INTO record_links(source_type,source_id,target_type,target_id,relationship) VALUES (?,?,?,?,?) ON CONFLICT DO NOTHING",st,si,tt,ti,rel);}
  private void requireIncident(UUID id){if(!Boolean.TRUE.equals(db.queryForObject("SELECT EXISTS(SELECT 1 FROM incidents WHERE id=?)",Boolean.class,id)))throw new ResponseStatusException(HttpStatus.NOT_FOUND,"Incident not found");}
  private void audit(UUID id,String event,Map<String,Object> detail){try{db.update("INSERT INTO audit_events(incident_id,event,detail) VALUES (?,?,?::jsonb)",id,event,json.writeValueAsString(detail));}catch(Exception e){throw new IllegalStateException("Could not serialize audit event",e);}}
}
