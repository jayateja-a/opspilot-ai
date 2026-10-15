package ai.opspilot;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class Api {
  private final IncidentService incidents;
  private final AgentClient agent;

  public Api(IncidentService incidents, AgentClient agent) {
    this.incidents = incidents;
    this.agent = agent;
  }

  public record Create(
      @NotBlank @Size(max = 80) String service,
      @NotBlank @Size(max = 160) String title,
      @NotBlank @Size(max = 8000) String description,
      @Pattern(regexp = "P[123]") @NotNull String severity,
      @Size(max = 80) String scenarioId) {}

  public record Decision(
      @NotNull @Pattern(regexp = "APPROVE|REJECT") String decision,
      @NotBlank @Size(max = 80) String reviewer,
      @NotBlank @Size(max = 2000) String note) {}

  public record Runbook(
      @NotBlank @Pattern(regexp = "[a-zA-Z0-9_-]{1,80}") String id,
      @NotBlank @Size(max = 80) String service,
      @NotBlank @Size(max = 160) String title,
      @NotBlank @Size(max = 16000) String content) {}

  @GetMapping("/incidents")
  public Object list() {
    return incidents.list();
  }

  @PostMapping("/incidents")
  @ResponseStatus(HttpStatus.CREATED)
  public Object create(@Valid @RequestBody Create r) {
    return incidents.create(r);
  }

  @GetMapping("/incidents/{id}")
  public Object get(@PathVariable UUID id) {
    return incidents.get(id);
  }

  @PostMapping("/incidents/{id}/analyze")
  public Object analyze(@PathVariable UUID id) {
    return incidents.analyze(id);
  }

  @PostMapping("/incidents/{id}/approval")
  public Object decide(@PathVariable UUID id, @Valid @RequestBody Decision r) {
    return incidents.decide(id, r);
  }

  @PostMapping("/incidents/{id}/execute")
  public Object execute(@PathVariable UUID id) {
    return incidents.execute(id);
  }

  @GetMapping("/scenarios")
  public Object scenarios() {
    return agent.scenarios();
  }

  @GetMapping("/runbooks")
  public Object runbooks() {
    return agent.runbooks();
  }

  @PostMapping("/runbooks")
  @ResponseStatus(HttpStatus.CREATED)
  public Object ingest(@Valid @RequestBody Runbook r) {
    return agent.ingest(
        Map.of("id", r.id(), "service", r.service(), "title", r.title(), "content", r.content()));
  }
}
