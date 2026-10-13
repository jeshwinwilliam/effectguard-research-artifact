package org.effectguard.temporal;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface ExternalEffectActivities {
  @ActivityMethod
  String submit(RecoveryInput input);

  @ActivityMethod
  String verify(String logicalOperationId);

  @ActivityMethod
  String compensate(String logicalOperationId);

  default GraphEvaluation evaluateGraph(String semanticGraph, String rootObservedStatus) {
    return new GraphEvaluation(0, 0, 0, false, 0, "");
  }

  default String materializeDescendants(String semanticGraph, String validitySummary, String rootOperationId) {
    return "";
  }
}
