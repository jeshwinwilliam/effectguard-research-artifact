package org.effectguard.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Opt-in test for an actual separately started Temporal development service.
 * It is skipped unless -Dtemporal.service.address=host:port is provided.
 */
class ServiceBackedTemporalIntegrationTest {
  private static final String TASK_QUEUE = "effectguard-service-backed-development";
  private WorkflowServiceStubs service;
  private WorkerFactory workers;
  private ServiceProvider provider;

  @BeforeEach
  void setUp() {
    Assumptions.assumeTrue(System.getProperty("temporal.service.address") != null,
        "requires a separately started Temporal development service");
    service = WorkflowServiceStubs.newServiceStubs(
        WorkflowServiceStubsOptions.newBuilder()
            .setTarget(System.getProperty("temporal.service.address"))
            .build());
    WorkflowClient client = WorkflowClient.newInstance(service);
    workers = WorkerFactory.newInstance(client);
    Worker worker = workers.newWorker(TASK_QUEUE);
    provider = new ServiceProvider();
    worker.registerWorkflowImplementationTypes(TemporalRecoveryWorkflowImpl.class);
    worker.registerActivitiesImplementations(provider);
    workers.start();
  }

  @AfterEach
  void tearDown() {
    if (workers != null) {
      workers.shutdown();
    }
    if (service != null) {
      service.shutdown();
    }
  }

  @Test
  void serviceBackedWorkflowRetriesVerifiesAndCompensates() {
    RecoveryResult verified = workflow("service-verified").recover(
        new RecoveryInput("service-logical-001", true, true, false, false, 0));
    RecoveryResult compensated = workflow("service-compensated").recover(
        new RecoveryInput("service-logical-002", true, false, true, true, 0));
    RecoveryResult unsupported = workflow("service-unsupported").recover(
        new RecoveryInput("service-logical-003", true, false, true, false, 0));

    assertEquals("RECOVERED", verified.terminalStatus());
    assertEquals(2, provider.submitAttemptsFor("service-logical-001"));
    assertEquals(1, provider.committedEffectCount("service-logical-001"));
    assertEquals("RECOVERED", compensated.terminalStatus());
    assertEquals("RECOVERY_UNSUPPORTED", unsupported.terminalStatus());
    assertEquals(1, provider.compensationAttempts.get());
  }

  private TemporalRecoveryWorkflow workflow(String workflowId) {
    return WorkflowClient.newInstance(service).newWorkflowStub(
        TemporalRecoveryWorkflow.class,
        WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).setWorkflowId(workflowId + "-" + UUID.randomUUID()).build());
  }

  static final class ServiceProvider implements ExternalEffectActivities {
    final AtomicInteger submitAttempts = new AtomicInteger();
    final AtomicInteger compensationAttempts = new AtomicInteger();
    final Map<String, Integer> committed = new ConcurrentHashMap<>();
    final Map<String, AtomicInteger> attemptsByOperation = new ConcurrentHashMap<>();

    @Override
    public String submit(RecoveryInput input) {
      submitAttempts.incrementAndGet();
      int operationAttempt = attemptsByOperation
          .computeIfAbsent(input.logicalOperationId(), ignored -> new AtomicInteger())
          .incrementAndGet();
      if (input.transientFailureBeforeCommit() && operationAttempt == 1) {
        throw io.temporal.failure.ApplicationFailure.newFailure("transient pre-commit failure", "TRANSIENT_PRE_COMMIT");
      }
      committed.putIfAbsent(input.logicalOperationId(), 1);
      return input.ambiguousAcknowledgement() ? "UNKNOWN" : "SUCCESS";
    }

    @Override
    public String verify(String logicalOperationId) {
      return committed.containsKey(logicalOperationId) ? "SUCCESS" : "UNKNOWN";
    }

    @Override
    public String compensate(String logicalOperationId) {
      compensationAttempts.incrementAndGet();
      committed.remove(logicalOperationId);
      return "COMPENSATED";
    }

    int committedEffectCount(String logicalOperationId) {
      return committed.containsKey(logicalOperationId) ? 1 : 0;
    }

    int submitAttemptsFor(String logicalOperationId) {
      return attemptsByOperation.get(logicalOperationId).get();
    }
  }
}
