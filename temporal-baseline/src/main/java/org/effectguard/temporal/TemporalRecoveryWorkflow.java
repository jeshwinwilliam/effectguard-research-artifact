package org.effectguard.temporal;

import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface TemporalRecoveryWorkflow {
  @WorkflowMethod
  RecoveryResult recover(RecoveryInput input);
}
