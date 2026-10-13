package org.effectguard.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Real-service development matrix using the shared P4 provider HTTP contract.
 * It validates Temporal's provider observations; it is not a confirmatory
 * paired experiment or an implementation of EffectGuard's evaluator.
 */
class ServiceBackedProviderOutcomeMatrixTest {
  private static final String TASK_QUEUE = "effectguard-service-paired-development";
  private WorkflowServiceStubs service;
  private WorkerFactory workers;

  @BeforeEach
  void setUp() {
    String address = System.getProperty("temporal.service.address");
    String providerUrl = System.getProperty("effectguard.provider.url");
    Assumptions.assumeTrue(address != null && providerUrl != null,
        "requires a separately started Temporal service and P4 local provider");
    service = WorkflowServiceStubs.newServiceStubs(
        WorkflowServiceStubsOptions.newBuilder().setTarget(address).build());
    WorkflowClient client = WorkflowClient.newInstance(service);
    workers = WorkerFactory.newInstance(client);
    Worker worker = workers.newWorker(TASK_QUEUE);
    worker.registerWorkflowImplementationTypes(TemporalRecoveryWorkflowImpl.class);
    worker.registerActivitiesImplementations(new P4LocalProviderActivities(providerUrl));
    workers.start();
  }

  @AfterEach
  void tearDown() {
    if (workers != null) workers.shutdown();
    if (service != null) service.shutdown();
  }

  @Test
  void validates_delayed_success_failure_unknown_and_duplicate_safe_retry() {
    assertEquals("RECOVERED", workflow("delayed-success").recover(
        input("delayed-success", true, false, false, false, "SUCCESS")).terminalStatus());
    assertEquals("RECOVERED", workflow("delayed-failure").recover(
        input("delayed-failure", true, false, false, false, "FAILURE")).terminalStatus());
    assertEquals("UNRESOLVED", workflow("persistent-unknown").recover(
        input("persistent-unknown", true, false, false, false, "UNKNOWN")).terminalStatus());
    assertEquals("RECOVERY_UNSUPPORTED", workflow("unsupported-compensation").recover(
        input("unsupported-compensation", true, false, true, false, "SUCCESS")).terminalStatus());
    assertEquals("RECOVERED", workflow("retry-idempotency").recover(
        input("retry-idempotency", true, true, false, false, "SUCCESS")).terminalStatus());
  }

  private TemporalRecoveryWorkflow workflow(String prefix) {
    return WorkflowClient.newInstance(service).newWorkflowStub(
        TemporalRecoveryWorkflow.class,
        WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).setWorkflowId(prefix + "-" + UUID.randomUUID()).build());
  }

  private static RecoveryInput input(
      String prefix,
      boolean ambiguous,
      boolean transientFailure,
      boolean compensationRequired,
      boolean compensationSupported,
      String resolvedStatus) {
    return new RecoveryInput(
        prefix + "-" + UUID.randomUUID(),
        ambiguous,
        transientFailure,
        compensationRequired,
        compensationSupported,
        0,
        resolvedStatus);
  }
}
