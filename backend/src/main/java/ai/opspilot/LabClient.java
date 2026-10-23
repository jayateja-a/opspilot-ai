package ai.opspilot;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;
import java.util.Set;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/** Read-only telemetry client plus named fault controls for the synthetic Compose lab. */
@Component
public class LabClient {
  private static final Set<String> HEALTHCARE=Set.of("oom","certificate","dns");
  private final RestClient fintech,healthcare,commerce;
  private final String token;
  private final ObjectMapper json;
  public LabClient(@Value("${opspilot.lab.fintech-url:http://localhost:8081}") String f,
      @Value("${opspilot.lab.healthcare-url:http://localhost:8082}") String h,
      @Value("${opspilot.lab.commerce-url:http://localhost:8083}") String c,
      @Value("${opspilot.lab.token:local-lab-token}") String token, ObjectMapper json) {
    this.fintech=client(f); this.healthcare=client(h); this.commerce=client(c); this.token=token; this.json=json;
  }
  private RestClient client(String url){var factory=new SimpleClientHttpRequestFactory();factory.setConnectTimeout(1500);factory.setReadTimeout(3000);return RestClient.builder().baseUrl(url).requestFactory(factory).build();}
  private RestClient forScenario(String id){
    // Some legacy fixture tickets also use checkout-service, so select a lab by
    // the explicit catalog namespace instead of the service name alone.
    if(id.startsWith("commerce-"))return commerce;
    return HEALTHCARE.contains(id)?healthcare:fintech;
  }
  @SuppressWarnings("unchecked")
  public Map<String,Object> activateAndRead(String scenarioId) {
    RestClient client=forScenario(scenarioId);
    byte[] payload;
    try { payload=json.writeValueAsBytes(Map.of("scenario_id",scenarioId)); }
    catch (Exception e) { throw new IllegalStateException("Could not serialize lab fault activation request",e); }
    // The Python lab reads bodies by Content-Length; explicitly send JSON bytes and length
    // so this request works with its minimal HTTP handler as well as standard clients.
    client.post().uri("/ops/faults").header("X-Lab-Token",token).contentType(MediaType.APPLICATION_JSON).contentLength(payload.length).body(payload).retrieve().toBodilessEntity();
    return client.get().uri("/ops/telemetry").retrieve().body(Map.class);
  }
  public void clear(String scenarioId){forScenario(scenarioId).post().uri("/ops/faults").header("X-Lab-Token",token).body(Map.of()).retrieve().toBodilessEntity();}
}
