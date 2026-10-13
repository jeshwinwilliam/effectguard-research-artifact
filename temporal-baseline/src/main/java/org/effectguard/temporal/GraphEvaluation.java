package org.effectguard.temporal;

import java.io.Serializable;

/** Public semantic-graph decision produced from provider-visible evidence. */
public record GraphEvaluation(
    int validCount,
    int invalidCount,
    int unknownCount,
    boolean unsupported,
    int recoveryWork,
    String validitySummary) implements Serializable {}
