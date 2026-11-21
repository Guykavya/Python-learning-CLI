SECONDS_PER_DAY = 86_400


def estimate(dau, writes_per_user, reads_per_write, bytes_per_item, years, peak_factor):
    if min(dau, writes_per_user, reads_per_write, bytes_per_item) < 0:
        raise ValueError("numbers must not be negative")
    if years <= 0:
        raise ValueError("years must be positive")
    if peak_factor < 1:
        raise ValueError("the peak cannot be lower than the average: peak_factor >= 1")
    avg_write = dau * writes_per_user / SECONDS_PER_DAY
    avg_read = avg_write * reads_per_write
    storage_gb = dau * writes_per_user * 365 * years * bytes_per_item / 1e9
    return {
        "avg_write_qps": round(avg_write, 2),
        "peak_write_qps": round(avg_write * peak_factor, 2),
        "avg_read_qps": round(avg_read, 2),
        "peak_read_qps": round(avg_read * peak_factor, 2),
        "storage_gb": round(storage_gb, 1),
    }
