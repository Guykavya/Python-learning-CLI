def _ratio(a, b):
    return float(a / b) if b else 0.0


def cls_metrics(TP, FP, FN, TN):
    if min(TP, FP, FN, TN) < 0:
        raise ValueError("counts cannot be negative")
    precision = _ratio(TP, TP + FP)
    recall = _ratio(TP, TP + FN)
    return {
        "accuracy": _ratio(TP + TN, TP + FP + FN + TN),
        "precision": precision,
        "recall": recall,
        "specificity": _ratio(TN, TN + FP),
        "f1": _ratio(2 * precision * recall, precision + recall),
    }
