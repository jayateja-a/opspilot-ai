package ai.opspilot;

import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class AgentClient {
  private final RestClient client;

  public AgentClient(
      @Value("${opspilot.agent-url}") String url, @Value("${opspilot.agent-token}") String token) {
    var factory = new SimpleClientHttpRequestFactory();
    factory.setConnectTimeout(5000);
    factory.setReadTimeout(60000);
    client =
        RestClient.builder()
            .baseUrl(url)
            .requestFactory(factory)
            .defaultHeader("X-Agent-Token", token)
            .build();
  }

  @SuppressWarnings("unchecked")
  public Map<String, Object> analyze(Map<String, Object> incident) {
    return client.post().uri("/v1/analyze").body(incident).retrieve().body(Map.class);
  }

  @SuppressWarnings("unchecked")
  public Map<String, Object> execute(Map<String, Object> request) {
    return client.post().uri("/v1/execute").body(request).retrieve().body(Map.class);
  }

  public Object scenarios() {
    return client.get().uri("/v1/scenarios").retrieve().body(Object.class);
  }

  public Object runbooks() {
    return client.get().uri("/v1/runbooks").retrieve().body(Object.class);
  }

  public Object ingest(Map<String, Object> request) {
    return client.post().uri("/v1/runbooks").body(request).retrieve().body(Object.class);
  }
}
