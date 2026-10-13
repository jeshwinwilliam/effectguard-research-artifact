package org.effectguard.temporal;

import java.io.Serializable;

/** Terminal result exposed by the development Temporal baseline. */
public record RecoveryResult(
    String terminalStatus,
    String detail,
    String validitySummary,
    int recoveryWork,
    String descendantTrace) implements Serializable {
  public RecoveryResult(String terminalStatus, String detail) {
    this(terminalStatus, detail, "", 0, "");
  }
}
