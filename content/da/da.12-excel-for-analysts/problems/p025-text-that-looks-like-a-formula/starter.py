def write_safe(ws, row, col, value):
    """Write value into the cell; text starting with =, +, - or @ is stored as text, never as a formula. Return the cell."""
    raise NotImplementedError
