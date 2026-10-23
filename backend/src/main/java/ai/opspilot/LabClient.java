package ai.opspilot;

import java.util.Map;
import java.util.Set;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/** Read-only telemetry client plus named fault controls for the synthetic Compose lab. */
@Component
public class LabClient {
  private static final Set<String> HEALTHCARE=Set.of("oom","certificate","dns");
  private final RestClient fintech,healthcare;
  private final String token;
  public LabClient(@Value("${opspilot.lab.fintech-url:http://localhost:8081}") String f,
      @Value("${opspilot.lab.healthcare-url:http://localhost:8082}") String h,
      @Value("${opspilot.lab.token:local-lab-token}") String token) {
    this.fintech=client(f); this.healthcare=client(h); this.token=token;
  }
  private RestClient client(String url){var factory=new SimpleClientHttpRequestFactory();factory.setConnectTimeout(1500);factory.setReadTimeout(3000);return RestClient.builder().baseUrl(url).requestFactory(factory).build();}
  private RestClient forScenario(String id){return HEALTHCARE.contains(id)?healthcare:fintech;}
  @SuppressWarnings("unchecked")
  public Map<String,Object> activateAndRead(String scenarioId) {
    RestClient client=forScenario(scenarioId);
    client.post().uri("/ops/faults").header("X-Lab-Token",token).body(Map.of("scenario_id",scenarioId)).retrieve().toBodilessEntity();
    return client.get().uri("/ops/telemetry").retrieve().body(Map.class);
  }
  public void clear(String scenarioId){forScenario(scenarioId).post().uri("/ops/faults").header("X-Lab-Token",token).body(Map.of()).retrieve().toBodilessEntity();}
}
