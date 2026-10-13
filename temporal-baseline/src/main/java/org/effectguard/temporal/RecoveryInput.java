package org.effectguard.temporal;

import java.io.Serializable;

/** Public, paired development input; it contains no evaluator-only truth. */
public record RecoveryInput(
    String logicalOperationId,
    boolean ambiguousAcknowledgement,
    boolean transientFailureBeforeCommit,
    boolean compensationRequiredAfterVerifiedSuccess,
    boolean compensationSupported,
    int pauseBeforeSubmitSeconds,
    String plannedResolvedStatus,
    boolean duplicateSubmission,
    boolean compensationFails,
    String semanticGraph,
    boolean evidenceDeadlineExpired) implements Serializable {

  /** Preserves the original development fixture's delayed-success behavior. */
  public RecoveryInput(
      String logicalOperationId,
      boolean ambiguousAcknowledgement,
      boolean transientFailureBeforeCommit,
      boolean compensationRequiredAfterVerifiedSuccess,
      boolean compensationSupported,
      int pauseBeforeSubmitSeconds) {
    this(
        logicalOperationId,
        ambiguousAcknowledgement,
        transientFailureBeforeCommit,
        compensationRequiredAfterVerifiedSuccess,
        compensationSupported,
        pauseBeforeSubmitSeconds,
        "SUCCESS",
        false,
        false,
        "",
        false);
  }

  /** Paired development constructor with a public provider outcome schedule. */
  public RecoveryInput(
      String logicalOperationId,
      boolean ambiguousAcknowledgement,
      boolean transientFailureBeforeCommit,
      boolean compensationRequiredAfterVerifiedSuccess,
      boolean compensationSupported,
      int pauseBeforeSubmitSeconds,
      String plannedResolvedStatus) {
    this(
        logicalOperationId,
        ambiguousAcknowledgement,
        transientFailureBeforeCommit,
        compensationRequiredAfterVerifiedSuccess,
        compensationSupported,
        pauseBeforeSubmitSeconds,
        plannedResolvedStatus,
        false,
        false,
        "",
        false);
  }

  /** Preserves the existing provider-matrix constructor. */
  public RecoveryInput(
      String logicalOperationId,
      boolean ambiguousAcknowledgement,
      boolean transientFailureBeforeCommit,
      boolean compensationRequiredAfterVerifiedSuccess,
      boolean compensationSupported,
      int pauseBeforeSubmitSeconds,
      String plannedResolvedStatus,
      boolean duplicateSubmission,
      boolean compensationFails) {
    this(
        logicalOperationId,
        ambiguousAcknowledgement,
        transientFailureBeforeCommit,
        compensationRequiredAfterVerifiedSuccess,
        compensationSupported,
        pauseBeforeSubmitSeconds,
        plannedResolvedStatus,
        duplicateSubmission,
        compensationFails,
        "",
        false);
  }
}
