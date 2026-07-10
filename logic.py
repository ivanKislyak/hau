separator = '|'
pos_inf = float('inf')

def to_number(value: str):
    if type(value) is str and separator in value:
        return value.split(separator)
    if value in ('', None):
        return 0
    return float(value)

def calc_tiered_payment(units: float | int, tariff_parts: float | int) -> float:
    total = 0
    units_left = units

    for limit, rate in zip(tariff_parts[0::2], tariff_parts[1::2]):
        limit = to_number(limit)
        rate = to_number(rate)

        if units_left <= 0:
            break

        used_units = units_left if limit == pos_inf else min(units_left, limit)

        total += used_units * rate
        units_left -= used_units

    return total

def commas_to_dots(my_list: list[str], commas_qty: int = 1) -> list:
    """
    Replaces commas with dots in each string from the given list.

    Args:
        my_list: List of strings where commas should be replaced.
        commas_qty: Maximum number of commas to replace in each string.

    Returns:
        A new list with commas replaced by dots.
    """

    return [item.replace(',', '.', commas_qty) for item in my_list]