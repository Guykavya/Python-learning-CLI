def safe_divide_all(pairs, logger) -> list:
    """Divide each (a, b); log problems instead of stopping."""
    results = []
    for i, (a, b) in enumerate(pairs):
        try:
            q = a / b
        except ZeroDivisionError:
            logger.warning("pair %d: division by zero (%r / %r)", i, a, b)
            results.append(None)
        except TypeError:
            logger.exception("pair %d: cannot divide %r by %r", i, a, b)
            results.append(None)
        else:
            logger.debug("pair %d: %r / %r = %r", i, a, b, q)
            results.append(q)
    return results
