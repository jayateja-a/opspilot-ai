package ai.opspilot;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

class LabClientTest {
  @Test
  void sendsFaultActivationAsJsonWithAnExplicitContentLength() throws Exception {
    HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
    AtomicReference<String> body = new AtomicReference<>();
    AtomicReference<String> contentLength = new AtomicReference<>();
    server.createContext(
        "/ops/faults",
        exchange -> {
          body.set(new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
          contentLength.set(exchange.getRequestHeaders().getFirst("Content-length"));
          exchange.sendResponseHeaders(200, -1);
          exchange.close();
        });
    server.createContext(
        "/ops/telemetry",
        exchange -> {
          byte[] response = "{\"domain\":\"fintech\",\"logs\":[],\"metrics\":{}}".getBytes(StandardCharsets.UTF_8);
          exchange.getResponseHeaders().set("Content-Type", "application/json");
          exchange.sendResponseHeaders(200, response.length);
          exchange.getResponseBody().write(response);
          exchange.close();
        });
    server.start();
    try {
      String url = "http://127.0.0.1:" + server.getAddress().getPort();
      LabClient client = new LabClient(url, url, url, "test-token", new ObjectMapper());

      client.activateAndRead("db-pool");

      assertEquals("{\"scenario_id\":\"db-pool\"}", body.get());
      assertEquals(Integer.toString(body.get().getBytes(StandardCharsets.UTF_8).length), contentLength.get());
    } finally {
      server.stop(0);
    }
  }

  @Test
  void routesCheckoutServiceToCommerceLabAndReadsItsTelemetry() throws Exception {
    AtomicInteger fintechRequests=new AtomicInteger(),commerceRequests=new AtomicInteger();
    HttpServer fintech=telemetryServer("fintech",fintechRequests);
    HttpServer healthcare=telemetryServer("healthcare",new AtomicInteger());
    HttpServer commerce=telemetryServer("ecommerce",commerceRequests);
    fintech.start();healthcare.start();commerce.start();
    try {
      LabClient client=new LabClient(url(fintech),url(healthcare),url(commerce),"test-token",new ObjectMapper());
      var telemetry=client.activateAndRead("commerce-imported-ticket");
      assertEquals("ecommerce",telemetry.get("domain"));
      assertTrue(commerceRequests.get()>=2,"expected fault activation and telemetry to use commerce controller");
      assertEquals(0,fintechRequests.get());
    } finally {fintech.stop(0);healthcare.stop(0);commerce.stop(0);}
  }

  private static String url(HttpServer server){return "http://127.0.0.1:"+server.getAddress().getPort();}
  private static HttpServer telemetryServer(String domain,AtomicInteger requests)throws Exception{
    HttpServer server=HttpServer.create(new InetSocketAddress("127.0.0.1",0),0);
    server.createContext("/ops/faults",exchange->{requests.incrementAndGet();exchange.getRequestBody().readAllBytes();exchange.sendResponseHeaders(200,-1);exchange.close();});
    server.createContext("/ops/telemetry",exchange->{requests.incrementAndGet();byte[] body=("{\"domain\":\""+domain+"\",\"logs\":[],\"metrics\":{}}").getBytes(StandardCharsets.UTF_8);exchange.getResponseHeaders().set("Content-Type","application/json");exchange.sendResponseHeaders(200,body.length);exchange.getResponseBody().write(body);exchange.close();});
    return server;
  }
}
