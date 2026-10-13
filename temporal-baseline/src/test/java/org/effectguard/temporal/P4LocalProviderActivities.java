package org.effectguard.temporal;

import io.temporal.failure.ApplicationFailure;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Test-only Temporal Activity adapter for the separate Python P4 provider HTTP service. */
final class P4LocalProviderActivities implements ExternalEffectActivities {
  private static final Pattern STATUS = Pattern.compile("\\\"observed_status\\\"\\s*:\\s*\\\"([A-Z_]+)\\\"");
  private final HttpClient client = HttpClient.newHttpClient();
  private final String baseUrl;
  private final Map<String, AtomicInteger> attemptsByOperation = new ConcurrentHashMap<>();
  private final Map<String, Boolean> compensationFailureByOperation = new ConcurrentHashMap<>();
  private final Map<String, Boolean> duplicateSubmissionByOperation = new ConcurrentHashMap<>();

  P4LocalProviderActivities(String baseUrl) {
    this.baseUrl = baseUrl.replaceAll("/$", "");
  }

  @Override
  public String submit(RecoveryInput input) {
    int attempt = attemptsByOperation
        .computeIfAbsent(input.logicalOperationId(), ignored -> new AtomicInteger())
        .incrementAndGet();
    if (input.transientFailureBeforeCommit() && attempt == 1) {
      throw ApplicationFailure.newFailure("transient pre-commit failure", "TRANSIENT_PRE_COMMIT");
    }
    String submission = "{\"logical_operation_id\":\"" + escape(input.logicalOperationId())
        + "\",\"idempotency_key\":\"" + escape(input.logicalOperationId())
        + "\",\"effect_class\":\"COMPENSABLE\",\"supports_compensation\":true,\"acknowledge\":false}";
    post("/submit", submission);
    if (input.duplicateSubmission()) {
      post("/submit", submission);
      duplicateSubmissionByOperation.put(input.logicalOperationId(), true);
    }
    compensationFailureByOperation.put(input.logicalOperationId(), input.compensationFails());
    post("/resolve", "{\"logical_operation_id\":\"" + escape(input.logicalOperationId())
        + "\",\"observed_status\":\"" + escape(input.plannedResolvedStatus()) + "\"}");
    return "UNKNOWN";
  }

  @Override
  public String verify(String logicalOperationId) {
    String observed = observedStatus(get("/verify/" + logicalOperationId));
    return observed;
  }

  @Override
  public String compensate(String logicalOperationId) {
    if (Boolean.TRUE.equals(compensationFailureByOperation.get(logicalOperationId))) {
      throw ApplicationFailure.newFailure("configured compensation failure", "COMPENSATION_FAILURE");
    }
    post("/compensate", "{\"logical_operation_id\":\"" + escape(logicalOperationId) + "\"}");
    return "COMPENSATED";
  }

  int attemptsFor(String logicalOperationId) {
    return attemptsByOperation.get(logicalOperationId).get();
  }

  boolean duplicateSubmissionFor(String logicalOperationId) {
    return Boolean.TRUE.equals(duplicateSubmissionByOperation.get(logicalOperationId));
  }

  @Override
  public GraphEvaluation evaluateGraph(String semanticGraph, String rootObservedStatus) {
    int valid = 0;
    int invalid = 0;
    int unknown = 0;
    boolean unsupported = false;
    int recoveryWork = 0;
    StringBuilder summary = new StringBuilder();
    if (semanticGraph.isBlank()) return new GraphEvaluation(0, 0, 0, false, 0, "");
    for (String encoded : semanticGraph.split(";")) {
      String[] fields = encoded.split("\\|", -1);
      String actionId = fields[0];
      String effectClass = fields[2];
      boolean requiresRoot = Boolean.parseBoolean(fields[3]);
      boolean conflictsRoot = Boolean.parseBoolean(fields[4]);
      boolean compensationSupported = Boolean.parseBoolean(fields[5]);
      String decision = "VALID";
      if ("UNKNOWN".equals(rootObservedStatus)) decision = "UNKNOWN";
      else if (requiresRoot && "FAILURE".equals(rootObservedStatus)) decision = "INVALID";
      else if (conflictsRoot && "SUCCESS".equals(rootObservedStatus)) decision = "INVALID";
      if (summary.length() > 0) summary.append(';');
      summary.append(actionId).append('=').append(decision);
      if ("VALID".equals(decision)) valid++;
      if ("UNKNOWN".equals(decision)) unknown++;
      if ("INVALID".equals(decision)) {
        invalid++;
        if ("IRREVERSIBLE".equals(effectClass) ||
            (("COMPENSABLE".equals(effectClass) || "REVERSIBLE".equals(effectClass)) && !compensationSupported)) {
          unsupported = true;
        } else if ("COMPENSABLE".equals(effectClass) || "REVERSIBLE".equals(effectClass)) {
          recoveryWork += 2;
        } else {
          recoveryWork++;
        }
      }
    }
    return new GraphEvaluation(valid, invalid, unknown, unsupported, recoveryWork, summary.toString());
  }

  @Override
  public String materializeDescendants(String semanticGraph, String validitySummary, String rootOperationId) {
    StringBuilder trace = new StringBuilder();
    Map<String, String> decisions = new ConcurrentHashMap<>();
    for (String item : validitySummary.split(";")) {
      String[] pair = item.split("=", 2);
      if (pair.length == 2) decisions.put(pair[0], pair[1]);
    }
    for (String encoded : semanticGraph.split(";")) {
      String[] fields = encoded.split("\\|", -1);
      String actionId = fields[0];
      if (!"VALID".equals(decisions.get(actionId))) continue;
      String operationId = rootOperationId + ":" + fields[1];
      String body = "{\"logical_operation_id\":\"" + escape(operationId)
          + "\",\"idempotency_key\":\"" + escape(operationId)
          + "\",\"effect_class\":\"" + escape(fields[2])
          + "\",\"supports_compensation\":" + fields[5] + ",\"acknowledge\":true}";
      post("/submit", body);
      post("/resolve", "{\"logical_operation_id\":\"" + escape(operationId)
          + "\",\"observed_status\":\"SUCCESS\"}");
      verify(operationId);
      if (trace.length() > 0) trace.append(';');
      trace.append(actionId).append("=executed");
    }
    return trace.toString();
  }

  private String get(String path) {
    return send(HttpRequest.newBuilder(URI.create(baseUrl + path)).GET().build());
  }

  private String post(String path, String body) {
    return send(HttpRequest.newBuilder(URI.create(baseUrl + path))
        .header("Content-Type", "application/json")
        .POST(HttpRequest.BodyPublishers.ofString(body))
        .build());
  }

  private String send(HttpRequest request) {
    try {
      HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
      if (response.statusCode() != 200) {
        throw new IllegalStateException("P4 local provider returned HTTP " + response.statusCode());
      }
      return response.body();
    } catch (IOException exception) {
      throw new IllegalStateException("P4 local provider I/O failure", exception);
    } catch (InterruptedException exception) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException("P4 local provider request interrupted", exception);
    }
  }

  private static String observedStatus(String payload) {
    Matcher matcher = STATUS.matcher(payload);
    if (!matcher.find()) {
      throw new IllegalStateException("P4 local provider response lacks observed_status");
    }
    return matcher.group(1);
  }

  private static String escape(String value) {
    return value.replace("\\", "\\\\").replace("\"", "\\\"");
  }
}
