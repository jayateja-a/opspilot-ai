package ai.opspilot;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class IncidentService {
  private final JdbcTemplate db;
  private final ObjectMapper json;
  private final AgentClient agent;

  public IncidentService(JdbcTemplate db, ObjectMapper json, AgentClient agent) {
    this.db = db;
    this.json = json;
    this.agent = agent;
  }

  String encode(Object o) {
    try {
      return json.writeValueAsString(o);
    } catch (Exception e) {
      throw new IllegalStateException(e);
    }
  }

  Map<String, Object> decode(Object o) {
    try {
      return json.readValue(o.toString(), new TypeReference<>() {});
    } catch (Exception e) {
      throw new IllegalStateException(e);
    }
  }

  Map<String, Object> convert(Map<String, Object> row) {
    var r = new LinkedHashMap<>(row);
    for (String k : List.of("analysis", "result", "detail"))
      if (r.get(k) != null) r.put(k, decode(r.get(k)));
    return r;
  }

  public List<Map<String, Object>> list() {
    return db.queryForList("SELECT * FROM incidents ORDER BY created_at DESC LIMIT 100").stream()
        .map(this::convert)
        .toList();
  }

  Map<String, Object> load(UUID id, boolean lock) {
    var rows =
        db.queryForList("SELECT * FROM incidents WHERE id=?" + (lock ? " FOR UPDATE" : ""), id);
    if (rows.isEmpty())
      throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Incident not found");
    return convert(rows.get(0));
  }

  public Map<String, Object> get(UUID id) {
    var r = load(id, false);
    r.put(
        "events",
        db.queryForList("SELECT * FROM audit_events WHERE incident_id=? ORDER BY id", id).stream()
            .map(this::convert)
            .toList());
    r.put(
        "approval",
        db.queryForList("SELECT * FROM approvals WHERE incident_id=?", id).stream()
            .findFirst()
            .orElse(null));
    r.put(
        "execution",
        db.queryForList("SELECT * FROM executions WHERE incident_id=?", id).stream()
            .map(this::convert)
            .findFirst()
            .orElse(null));
    return r;
  }

  void event(UUID id, String name, Object detail) {
    db.update(
        "INSERT INTO audit_events(incident_id,event,detail) VALUES (?,?,?::jsonb)",
        id,
        name,
        encode(detail));
  }

  void require(Map<String, Object> r, String... allowed) {
    if (!Arrays.asList(allowed).contains(r.get("status")))
      throw new ResponseStatusException(
          HttpStatus.CONFLICT, "Invalid transition from " + r.get("status"));
  }

  @Transactional
  public Map<String, Object> create(Api.Create request) {
    UUID id = UUID.randomUUID();
    String scenario = request.scenarioId();
    if (scenario != null) {
      Object raw = agent.scenarios();
      if (!(raw instanceof List<?> items))
        throw new IllegalStateException("Invalid scenario response");
      var match =
          items.stream()
              .filter(x -> x instanceof Map<?, ?> m && scenario.equals(m.get("id")))
              .findFirst()
              .orElseThrow(
                  () -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "Unknown scenario"));
      if (!request.service().equals(((Map<?, ?>) match).get("service")))
        throw new ResponseStatusException(
            HttpStatus.BAD_REQUEST, "Scenario does not match service");
    }
    db.update(
        "INSERT INTO services(id,name) VALUES (?,?) ON CONFLICT DO NOTHING",
        request.service(),
        request.service());
    db.update(
        "INSERT INTO incidents(id,service,title,description,severity,scenario_id) VALUES"
            + " (?,?,?,?,?,?)",
        id,
        request.service(),
        request.title(),
        request.description(),
        request.severity(),
        scenario);
    event(id, "INCIDENT_CREATED", Map.of("simulation", true));
    return get(id);
  }

  @Transactional
  public Map<String, Object> analyze(UUID id) {
    var r = load(id, true);
    require(r, "OPEN", "ANALYSIS_FAILED");
    Map<String, Object> analysis;
    try {
      analysis =
          agent.analyze(
              Map.of(
                  "incident_id",
                  id.toString(),
                  "service",
                  r.get("service"),
                  "description",
                  r.get("description"),
                  "scenario_id",
                  Objects.toString(r.get("scenario_id"), "")));
      if (analysis == null
          || !(analysis.get("recommendation") instanceof Map<?, ?>)
          || !(analysis.get("citations") instanceof List<?>))
        throw new IllegalStateException("Invalid agent contract");
    } catch (Exception e) {
      db.update(
          "UPDATE incidents SET status='ANALYSIS_FAILED',last_error='AI service unavailable or"
              + " invalid response',updated_at=now() WHERE id=?",
          id);
      event(id, "ANALYSIS_FAILED", Map.of("retryable", true));
      return get(id);
    }
    db.update(
        "UPDATE incidents SET"
            + " status='AWAITING_APPROVAL',analysis=?::jsonb,last_error=NULL,updated_at=now() WHERE"
            + " id=?",
        encode(analysis),
        id);
    event(id, "ANALYSIS_COMPLETED", Map.of("mode", analysis.get("mode")));
    return get(id);
  }

  @Transactional
  public Map<String, Object> decide(UUID id, Api.Decision request) {
    var r = load(id, true);
    require(r, "AWAITING_APPROVAL");
    var a = (Map<?, ?>) r.get("analysis");
    var rec = (Map<?, ?>) a.get("recommendation");
    if (request.decision().equals("APPROVE") && !Boolean.TRUE.equals(rec.get("executable")))
      throw new ResponseStatusException(HttpStatus.CONFLICT, "Insufficient evidence for execution");
    UUID approval = UUID.randomUUID();
    db.update(
        "INSERT INTO approvals(id,incident_id,decision,reviewer,note) VALUES (?,?,?,?,?)",
        approval,
        id,
        request.decision(),
        request.reviewer(),
        request.note());
    db.update(
        "UPDATE incidents SET status=?,updated_at=now() WHERE id=?",
        request.decision().equals("APPROVE") ? "APPROVED" : "REJECTED",
        id);
    event(
        id,
        "HUMAN_" + request.decision(),
        Map.of("reviewer", request.reviewer(), "approval_id", approval.toString()));
    return get(id);
  }

  @Transactional
  public Map<String, Object> execute(UUID id) {
    var r = load(id, true);
    if ("RESOLVED".equals(r.get("status"))) return get(id);
    require(r, "APPROVED");
    var approval =
        db.queryForMap("SELECT * FROM approvals WHERE incident_id=? AND decision='APPROVE'", id);
    var a = (Map<?, ?>) r.get("analysis");
    var rec = (Map<?, ?>) a.get("recommendation");
    var result =
        agent.execute(
            Map.of(
                "incident_id",
                id.toString(),
                "approval_id",
                approval.get("id").toString(),
                "service",
                r.get("service"),
                "scenario_id",
                r.get("scenario_id"),
                "action",
                rec.get("action")));
    if (result == null
        || !Boolean.TRUE.equals(result.get("success"))
        || !Boolean.TRUE.equals(result.get("simulated")))
      throw new ResponseStatusException(
          HttpStatus.BAD_GATEWAY, "Simulation did not verify successfully");
    db.update(
        "INSERT INTO executions(incident_id,approval_id,result) VALUES (?,?,?::jsonb)",
        id,
        approval.get("id"),
        encode(result));
    db.update("UPDATE incidents SET status='RESOLVED',updated_at=now() WHERE id=?", id);
    event(id, "SIMULATION_EXECUTED", result);
    return get(id);
  }
}
