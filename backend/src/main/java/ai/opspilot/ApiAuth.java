package ai.opspilot;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
public class ApiAuth extends OncePerRequestFilter {
  private final byte[] expected;

  public ApiAuth(@Value("${opspilot.api-token}") String token) {
    if (token.isBlank()) throw new IllegalArgumentException("API_TOKEN must be set");
    expected = ("Bearer " + token).getBytes(StandardCharsets.UTF_8);
  }

  @Override
  protected void doFilterInternal(
      HttpServletRequest req, HttpServletResponse res, FilterChain chain)
      throws ServletException, IOException {
    if (req.getRequestURI().startsWith("/api/")
        && !MessageDigest.isEqual(
            expected,
            java.util.Objects.toString(req.getHeader("Authorization"), "")
                .getBytes(StandardCharsets.UTF_8))) {
      res.setStatus(401);
      res.setContentType("application/json");
      res.getWriter().write("{\"error\":\"Unauthorized\"}");
      return;
    }
    chain.doFilter(req, res);
  }
}
