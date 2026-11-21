FAST_BURN = 14.4
SLOW_BURN = 6.0


def _check(slo, total, failed):
    if not 0 < slo < 1:
        raise ValueError(f"slo must be strictly between 0 and 1, got {slo}")
    if total < 0 or failed < 0 or failed > total:
        raise ValueError(f"need 0 <= failed <= total, got failed={failed}, total={total}")


def budget(slo, total, failed):
    _check(slo, total, failed)
    allowed = total * (1 - slo)
    remaining = allowed - failed
    return {"allowed_failures": allowed, "remaining_failures": remaining,
            "remaining_share": 1.0 if total == 0 else remaining / allowed, "exhausted": failed > allowed}


def burn_rate(slo, total, failed):
    _check(slo, total, failed)
    if total == 0:
        return 0.0
    return round((failed / total) / (1 - slo), 9)


def burn_alerts(slo, windows):
    if "1h" not in windows or "6h" not in windows:
        raise ValueError("windows needs the keys '1h' and '6h'")
    alerts = []
    if burn_rate(slo, *windows["1h"]) >= FAST_BURN:
        alerts.append("fast-burn")
    if burn_rate(slo, *windows["6h"]) >= SLOW_BURN:
        alerts.append("slow-burn")
    return alerts
