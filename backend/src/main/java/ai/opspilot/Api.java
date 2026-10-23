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
  private final ItsmService itsm;

  public Api(IncidentService incidents, AgentClient agent, ItsmService itsm) {
    this.incidents = incidents;
    this.agent = agent;
    this.itsm = itsm;
  }

  public record Create(
      @NotBlank @Size(max = 80) String service,
      @NotBlank @Size(max = 160) String title,
      @NotBlank @Size(max = 8000) String description,
      @Pattern(regexp = "P[0-5]") @NotNull String severity,
      @Size(max = 80) String scenarioId,
      @Pattern(regexp="HIGH|MEDIUM|LOW") String impact,
      @Pattern(regexp="HIGH|MEDIUM|LOW") String urgency,
      @Size(max=80) String category,
      @Size(max=80) String affectedCi,
      @Size(max=80) String reportedBy,
      @Size(max=80) String sourceChannel) {}

  public record Decision(
      @NotNull @Pattern(regexp = "APPROVE|REJECT") String decision,
      @NotBlank @Size(max = 80) String reviewer,
      @NotBlank @Size(max = 2000) String note) {}

  public record Runbook(
      @NotBlank @Pattern(regexp = "[a-zA-Z0-9_-]{1,80}") String id,
      @NotBlank @Size(max = 80) String service,
      @NotBlank @Size(max = 160) String title,
      @NotBlank @Size(max = 16000) String content) {}

  public record Problem(@NotBlank @Size(max=160) String title, @NotBlank @Size(max=8000) String description,
      @Size(max=4000) String rootCause, @Size(max=4000) String workaround, UUID incidentId) {}
  public record Change(@NotBlank @Size(max=160) String title, @NotBlank @Size(max=8000) String description,
      @NotNull @Pattern(regexp="STANDARD|NORMAL|EMERGENCY") String changeType, @NotNull @Pattern(regexp="LOW|MEDIUM|HIGH") String risk,
      @NotNull @Pattern(regexp="LOW|MEDIUM|HIGH") String impact, @NotBlank @Size(max=4000) String implementationPlan,
      @NotBlank @Size(max=4000) String rollbackPlan, UUID incidentId) {}
  public record ChangeTransition(@Pattern(regexp="ASSESSMENT|AUTHORIZED|SCHEDULED|IMPLEMENTING|REVIEW|CLOSED|REJECTED") String status,
      @Size(max=80) String reviewer) {}
  public record RcaReview(@NotNull Boolean approve, @NotBlank @Size(max=80) String reviewer) {}

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

  @GetMapping("/configuration-items") public Object configurationItems(){return itsm.configurationItems();}
  @GetMapping("/problems") public Object problems(){return itsm.problems();}
  @PostMapping("/problems") @ResponseStatus(HttpStatus.CREATED) public Object createProblem(@Valid @RequestBody Problem r){return itsm.createProblem(r);}
  @GetMapping("/changes") public Object changes(){return itsm.changes();}
  @PostMapping("/changes") @ResponseStatus(HttpStatus.CREATED) public Object createChange(@Valid @RequestBody Change r){return itsm.createChange(r);}
  @PostMapping("/changes/{id}/transition") public Object transitionChange(@PathVariable UUID id,@Valid @RequestBody ChangeTransition r){return itsm.transitionChange(id,r);}
  @GetMapping("/incidents/{id}/rca") public Object rcas(@PathVariable UUID id){return itsm.rcas(id);}
  @PostMapping("/rca/{id}/review") public Object reviewRca(@PathVariable UUID id,@Valid @RequestBody RcaReview r){return itsm.reviewRca(id,r);}
}
