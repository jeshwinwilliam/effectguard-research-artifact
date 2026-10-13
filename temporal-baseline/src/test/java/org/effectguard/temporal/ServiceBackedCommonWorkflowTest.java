package org.effectguard.temporal;

import static org.junit.jupiter.api.Assertions.assertNotNull;

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Properties;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Executes one common development specification through a real Temporal
 * service and writes an execution witness for the Python common harness.
 */
class ServiceBackedCommonWorkflowTest {
  private static final String TASK_QUEUE = "effectguard-common-development";
  private WorkflowServiceStubs service;
  private WorkerFactory workers;
  private P4LocalProviderActivities provider;

  @BeforeEach
  void setUp() {
    Assumptions.assumeTrue(required("temporal.service.address") != null
            && required("effectguard.provider.url") != null
            && required("effectguard.common.workflow.id") != null
            && required("effectguard.common.operation.id") != null
            && required("effectguard.common.output") != null,
        "requires a Temporal service, P4 provider, and common-harness properties");
    service = WorkflowServiceStubs.newServiceStubs(WorkflowServiceStubsOptions.newBuilder()
        .setTarget(required("temporal.service.address")).build());
    WorkflowClient client = WorkflowClient.newInstance(service);
    workers = WorkerFactory.newInstance(client);
    Worker worker = workers.newWorker(TASK_QUEUE);
    provider = new P4LocalProviderActivities(required("effectguard.provider.url"));
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
  void executesCommonDevelopmentSpecification() throws IOException {
    String workflowId = required("effectguard.common.workflow.id");
    String operationId = required("effectguard.common.operation.id");
    RecoveryResult result = WorkflowClient.newInstance(service).newWorkflowStub(
        TemporalRecoveryWorkflow.class,
        WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).setWorkflowId(workflowId).build()).recover(
            new RecoveryInput(
                operationId,
                true,
                booleanProperty("effectguard.common.transient_failure"),
                booleanProperty("effectguard.common.root_compensation_required"),
                booleanProperty("effectguard.common.root_compensation_supported"),
                0,
                required("effectguard.common.resolved_status"),
                booleanProperty("effectguard.common.duplicate_submission"),
                booleanProperty("effectguard.common.compensation_fails"),
                required("effectguard.common.semantic_graph"),
                booleanProperty("effectguard.common.evidence_deadline_expired")));
    assertNotNull(result);
    writeWitness(workflowId, operationId, result);
  }

  private void writeWitness(String workflowId, String operationId, RecoveryResult result) throws IOException {
    Properties witness = new Properties();
    witness.setProperty("workflow_id", workflowId);
    witness.setProperty("logical_operation_id", operationId);
    witness.setProperty("terminal_status", result.terminalStatus());
    witness.setProperty("detail", result.detail());
    witness.setProperty("activity_attempts", Integer.toString(provider.attemptsFor(operationId)));
    witness.setProperty("duplicate_submission", Boolean.toString(provider.duplicateSubmissionFor(operationId)));
    witness.setProperty("graph_sha256", required("effectguard.common.graph_sha256"));
    witness.setProperty("runtime_validity", result.validitySummary());
    witness.setProperty("recovery_work", Integer.toString(result.recoveryWork()));
    witness.setProperty("descendant_trace", result.descendantTrace());
    Path output = Path.of(required("effectguard.common.output"));
    Files.createDirectories(output.getParent());
    try (OutputStream stream = Files.newOutputStream(output)) {
      witness.store(stream, "EffectGuard common development Temporal execution witness");
    }
  }

  private static String required(String name) {
    String value = System.getProperty(name);
    return value == null || value.isBlank() ? null : value;
  }

  private static boolean booleanProperty(String name) {
    return Boolean.parseBoolean(System.getProperty(name, "false"));
  }
}
