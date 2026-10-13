package org.effectguard.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.client.WorkflowStub;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/** Two Maven phases surround an actual server termination/restart. */
class ServiceRestartPersistenceIntegrationTest {
  private static final String TASK_QUEUE = "effectguard-service-restart-development";
  private static final String WORKFLOW_ID = "effectguard-restart-persistence-v1";
  private WorkflowServiceStubs service;
  private WorkerFactory workers;

  @BeforeEach
  void setUp() {
    Assumptions.assumeTrue(System.getProperty("temporal.service.address") != null,
        "requires a separately started Temporal development service");
    Assumptions.assumeTrue(System.getProperty("temporal.restart.phase") != null,
        "requires start or complete restart phase");
    service = WorkflowServiceStubs.newServiceStubs(
        WorkflowServiceStubsOptions.newBuilder().setTarget(System.getProperty("temporal.service.address")).build());
    WorkflowClient client = WorkflowClient.newInstance(service);
    workers = WorkerFactory.newInstance(client);
    Worker worker = workers.newWorker(TASK_QUEUE);
    worker.registerWorkflowImplementationTypes(TemporalRecoveryWorkflowImpl.class);
    worker.registerActivitiesImplementations(new RestartProvider());
    workers.start();
  }

  @AfterEach
  void tearDown() {
    if (workers != null) workers.shutdown();
    if (service != null) service.shutdown();
  }

  @Test
  void persistAndResumeWorkflowAcrossServerRestart() throws InterruptedException {
    String phase = System.getProperty("temporal.restart.phase");
    TemporalRecoveryWorkflow workflow = WorkflowClient.newInstance(service).newWorkflowStub(
        TemporalRecoveryWorkflow.class,
        WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).setWorkflowId(WORKFLOW_ID).build());
    if ("start".equals(phase)) {
      WorkflowClient.start(workflow::recover,
          new RecoveryInput("restart-logical-001", false, false, false, false, 20));
      Thread.sleep(750); // Allows the persisted timer command to reach the service before external termination.
      return;
    }
    if ("complete".equals(phase)) {
      WorkflowStub existing = WorkflowClient.newInstance(service).newUntypedWorkflowStub(WORKFLOW_ID);
      RecoveryResult result = existing.getResult(RecoveryResult.class);
      assertEquals("RECOVERED", result.terminalStatus());
      return;
    }
    throw new IllegalArgumentException("temporal.restart.phase must be start or complete");
  }

  static final class RestartProvider implements ExternalEffectActivities {
    private final Map<String, Integer> committed = new ConcurrentHashMap<>();

    @Override
    public String submit(RecoveryInput input) {
      committed.putIfAbsent(input.logicalOperationId(), 1);
      return "SUCCESS";
    }

    @Override
    public String verify(String logicalOperationId) {
      return committed.containsKey(logicalOperationId) ? "SUCCESS" : "UNKNOWN";
    }

    @Override
    public String compensate(String logicalOperationId) {
      committed.remove(logicalOperationId);
      return "COMPENSATED";
    }
  }
}
