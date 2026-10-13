package org.effectguard.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.failure.ApplicationFailure;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class TemporalRecoveryWorkflowTest {
  private static final String TASK_QUEUE = "effectguard-development";
  private TestWorkflowEnvironment environment;
  private DevelopmentProvider provider;

  @BeforeEach
  void setUp() {
    environment = TestWorkflowEnvironment.newInstance();
    Worker worker = environment.newWorker(TASK_QUEUE);
    provider = new DevelopmentProvider();
    worker.registerWorkflowImplementationTypes(TemporalRecoveryWorkflowImpl.class);
    worker.registerActivitiesImplementations(provider);
    environment.start();
  }

  @AfterEach
  void tearDown() {
    environment.close();
  }

  @Test
  void retries_before_commit_then_verifies_an_ambiguous_receipt_without_duplicate_effect() {
    RecoveryResult result = workflow("ambiguous-retry").recover(
        new RecoveryInput("logical-001", true, true, false, false, 0));

    assertEquals("RECOVERED", result.terminalStatus());
    assertEquals(2, provider.submitAttempts.get());
    assertEquals(1, provider.committedEffectCount("logical-001"));
    assertEquals(1, provider.verifyAttempts.get());
  }

  @Test
  void compensates_only_when_the_development_contract_declares_it_safe() {
    RecoveryResult compensated = workflow("compensated").recover(
        new RecoveryInput("logical-002", true, false, true, true, 0));
    RecoveryResult unsupported = workflow("unsupported").recover(
        new RecoveryInput("logical-003", true, false, true, false, 0));

    assertEquals("RECOVERED", compensated.terminalStatus());
    assertEquals(1, provider.compensationAttempts.get());
    assertEquals("RECOVERY_UNSUPPORTED", unsupported.terminalStatus());
  }

  @Test
  void preserves_materialized_descendant_trace_for_all_post_materialization_terminal_paths() {
    RecoveryResult recovered = workflow("trace-recovered").recover(
        input("trace-recovered", false, true, false));
    RecoveryResult unsupported = workflow("trace-unsupported").recover(
        input("trace-unsupported", true, false, false));

    provider.failCompensation = true;
    RecoveryResult failed = workflow("trace-failed").recover(
        input("trace-failed", true, true, false));
    provider.failCompensation = false;
    provider.forceUnknownVerification = true;
    RecoveryResult unresolved = workflow("trace-unresolved").recover(
        input("trace-unresolved", false, true, false));

    assertEquals("RECOVERED", recovered.terminalStatus());
    assertEquals("RECOVERY_UNSUPPORTED", unsupported.terminalStatus());
    assertEquals("FAILED", failed.terminalStatus());
    assertEquals("UNRESOLVED", unresolved.terminalStatus());
    assertEquals("descendant=executed", recovered.descendantTrace());
    assertEquals("descendant=executed", unsupported.descendantTrace());
    assertEquals("descendant=executed", failed.descendantTrace());
    assertEquals("descendant=executed", unresolved.descendantTrace());
  }

  @Test
  void leaves_trace_empty_when_terminal_graph_decisions_precede_materialization() {
    RecoveryResult unresolved = workflow("graph-unknown").recover(
        input("graph-unknown", false, false, false, "graph-unknown"));
    RecoveryResult unsupported = workflow("graph-unsupported").recover(
        input("graph-unsupported", false, false, false, "graph-unsupported"));
    RecoveryResult failed = workflow("graph-failed").recover(
        input("graph-failed", false, false, true, "graph-failed"));

    assertEquals("UNRESOLVED", unresolved.terminalStatus());
    assertEquals("RECOVERY_UNSUPPORTED", unsupported.terminalStatus());
    assertEquals("FAILED", failed.terminalStatus());
    assertEquals("", unresolved.descendantTrace());
    assertEquals("", unsupported.descendantTrace());
    assertEquals("", failed.descendantTrace());
  }

  private static RecoveryInput input(String operationId, boolean requiresCompensation,
      boolean compensationSupported, boolean compensationFails) {
    return input(operationId, requiresCompensation, compensationSupported, compensationFails, "graph-normal");
  }

  private static RecoveryInput input(String operationId, boolean requiresCompensation,
      boolean compensationSupported, boolean compensationFails, String graph) {
    return new RecoveryInput(
        operationId, true, false, requiresCompensation, compensationSupported, 0,
        "SUCCESS", false, compensationFails, graph, false);
  }

  private TemporalRecoveryWorkflow workflow(String workflowId) {
    return environment.getWorkflowClient().newWorkflowStub(
        TemporalRecoveryWorkflow.class,
        WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).setWorkflowId(workflowId).build());
  }

  static final class DevelopmentProvider implements ExternalEffectActivities {
    final AtomicInteger submitAttempts = new AtomicInteger();
    final AtomicInteger verifyAttempts = new AtomicInteger();
    final AtomicInteger compensationAttempts = new AtomicInteger();
    final Map<String, Integer> committed = new ConcurrentHashMap<>();
    boolean failCompensation;
    boolean forceUnknownVerification;

    @Override
    public String submit(RecoveryInput input) {
      int attempt = submitAttempts.incrementAndGet();
      if (input.transientFailureBeforeCommit() && attempt == 1) {
        throw ApplicationFailure.newFailure("transient pre-commit failure", "TRANSIENT_PRE_COMMIT");
      }
      committed.putIfAbsent(input.logicalOperationId(), 1);
      return input.ambiguousAcknowledgement() ? "UNKNOWN" : "SUCCESS";
    }

    @Override
    public String verify(String logicalOperationId) {
      verifyAttempts.incrementAndGet();
      if (forceUnknownVerification) {
        return "UNKNOWN";
      }
      return committed.containsKey(logicalOperationId) ? "SUCCESS" : "UNKNOWN";
    }

    @Override
    public String compensate(String logicalOperationId) {
      compensationAttempts.incrementAndGet();
      if (failCompensation) {
        throw ApplicationFailure.newFailure("configured compensation failure", "COMPENSATION_FAILURE");
      }
      committed.remove(logicalOperationId);
      return "COMPENSATED";
    }

    @Override
    public GraphEvaluation evaluateGraph(String semanticGraph, String rootObservedStatus) {
      return switch (semanticGraph) {
        case "graph-unknown" -> new GraphEvaluation(0, 0, 1, false, 1, "descendant=UNKNOWN");
        case "graph-unsupported" -> new GraphEvaluation(0, 1, 0, true, 1, "descendant=INVALID");
        case "graph-failed" -> new GraphEvaluation(0, 1, 0, false, 1, "descendant=INVALID");
        default -> new GraphEvaluation(1, 0, 0, false, 1, "descendant=VALID");
      };
    }

    @Override
    public String materializeDescendants(String semanticGraph, String validitySummary, String rootOperationId) {
      return "descendant=executed";
    }

    int committedEffectCount(String logicalOperationId) {
      return committed.containsKey(logicalOperationId) ? 1 : 0;
    }
  }
}
