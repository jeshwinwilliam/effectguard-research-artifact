package org.effectguard.temporal;

import io.temporal.activity.ActivityOptions;
import io.temporal.common.RetryOptions;
import io.temporal.workflow.Workflow;
import java.time.Duration;

public final class TemporalRecoveryWorkflowImpl implements TemporalRecoveryWorkflow {
  private final ExternalEffectActivities activities = Workflow.newActivityStub(
      ExternalEffectActivities.class,
      ActivityOptions.newBuilder()
          .setStartToCloseTimeout(Duration.ofSeconds(10))
          .setRetryOptions(RetryOptions.newBuilder().setMaximumAttempts(2).build())
          .build());

  @Override
  public RecoveryResult recover(RecoveryInput input) {
    if (input.pauseBeforeSubmitSeconds() > 0) {
      Workflow.sleep(Duration.ofSeconds(input.pauseBeforeSubmitSeconds()));
    }
    String observed = activities.submit(input);
    if ("UNKNOWN".equals(observed)) {
      observed = activities.verify(input.logicalOperationId());
    }
    GraphEvaluation graph = activities.evaluateGraph(input.semanticGraph(), observed);
    if (graph.unknownCount() > 0) {
      return new RecoveryResult("UNRESOLVED", "semantic graph remains UNKNOWN", graph.validitySummary(), graph.recoveryWork(), "");
    }
    if (graph.unsupported()) {
      return new RecoveryResult("RECOVERY_UNSUPPORTED", "semantic graph requires unavailable or irreversible recovery", graph.validitySummary(), graph.recoveryWork(), "");
    }
    if (input.compensationFails() && graph.recoveryWork() > 0) {
      return new RecoveryResult("FAILED", "configured semantic-graph compensation failure", graph.validitySummary(), graph.recoveryWork(), "");
    }
    String descendants = activities.materializeDescendants(
        input.semanticGraph(), graph.validitySummary(), input.logicalOperationId());
    if ("SUCCESS".equals(observed)) {
      if (input.compensationRequiredAfterVerifiedSuccess()) {
        if (!input.compensationSupported()) {
          return new RecoveryResult("RECOVERY_UNSUPPORTED", "a verified effect requires unavailable compensation capability", graph.validitySummary(), graph.recoveryWork(), descendants);
        }
        try {
          activities.compensate(input.logicalOperationId());
        } catch (RuntimeException exception) {
          return new RecoveryResult("FAILED", "explicit compensation activity failed", graph.validitySummary(), graph.recoveryWork(), descendants);
        }
        return new RecoveryResult("RECOVERED", "verified committed effect was explicitly compensated", graph.validitySummary(), graph.recoveryWork(), descendants);
      }
      return new RecoveryResult("RECOVERED", "provider verification established one committed logical effect; " + descendants, graph.validitySummary(), graph.recoveryWork(), descendants);
    }
    if ("FAILURE".equals(observed)) {
      return new RecoveryResult("RECOVERED", "provider verification established that no active effect committed; " + descendants, graph.validitySummary(), graph.recoveryWork(), descendants);
    }
    return new RecoveryResult("UNRESOLVED", "provider verification did not produce decisive evidence", graph.validitySummary(), graph.recoveryWork(), descendants);
  }
}
