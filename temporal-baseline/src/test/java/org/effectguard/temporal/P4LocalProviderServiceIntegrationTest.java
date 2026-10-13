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

/** Opt-in test proving Temporal uses the existing P4 provider over its HTTP boundary. */
class P4LocalProviderServiceIntegrationTest {
  private static final String TASK_QUEUE = "effectguard-p4-provider-development";
  private WorkflowServiceStubs service;
  private WorkerFactory workers;
  private P4LocalProviderActivities provider;

  @BeforeEach
  void setUp() {
    String address = System.getProperty("temporal.service.address");
    String providerUrl = System.getProperty("effectguard.provider.url");
    Assumptions.assumeTrue(address != null && providerUrl != null,
        "requires a separately started Temporal service and P4 local provider");
    service = WorkflowServiceStubs.newServiceStubs(WorkflowServiceStubsOptions.newBuilder().setTarget(address).build());
    WorkflowClient client = WorkflowClient.newInstance(service);
    workers = WorkerFactory.newInstance(client);
    Worker worker = workers.newWorker(TASK_QUEUE);
    provider = new P4LocalProviderActivities(providerUrl);
    worker.registerWorkflowImplementationTypes(TemporalRecoveryWorkflowImpl.class);
    worker.registerActivitiesImplementations(provider);
    workers.start();
  }

  @AfterEach
  void tearDown() {
    if (workers != null) workers.shutdown();
    if (service != null) service.shutdown();
  }

  @Test
  void temporalAndEffectGuardCanObserveTheSameProviderProtocol() {
    String verifiedOperation = "shared-provider-verified-" + UUID.randomUUID();
    String compensatedOperation = "shared-provider-compensated-" + UUID.randomUUID();
    String unsupportedOperation = "shared-provider-unsupported-" + UUID.randomUUID();
    RecoveryResult verified = workflow("shared-provider-verified").recover(
        new RecoveryInput(verifiedOperation, true, true, false, false, 0));
    RecoveryResult compensated = workflow("shared-provider-compensated").recover(
        new RecoveryInput(compensatedOperation, true, false, true, true, 0));
    RecoveryResult unsupported = workflow("shared-provider-unsupported").recover(
        new RecoveryInput(unsupportedOperation, true, false, true, false, 0));

    assertEquals("RECOVERED", verified.terminalStatus());
    assertEquals(2, provider.attemptsFor(verifiedOperation));
    assertEquals("RECOVERED", compensated.terminalStatus());
    assertEquals("RECOVERY_UNSUPPORTED", unsupported.terminalStatus());
  }

  private TemporalRecoveryWorkflow workflow(String prefix) {
    return WorkflowClient.newInstance(service).newWorkflowStub(
        TemporalRecoveryWorkflow.class,
        WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).setWorkflowId(prefix + "-" + UUID.randomUUID()).build());
  }
}
