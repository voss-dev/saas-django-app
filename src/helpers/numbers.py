import math

def short_number(number):
    """
    Formats integers into human-readable compact strings  (e.g., 1000 -> 1K)
    """

    try:
        number = float(number)
    except (ValueError, TypeError):
        return "0"

    if number < 1000:
        return f"{int(number)}"

    # millnames = ['', 'K', 'M', 'B', 'T']

    # if number == 0:
        # raw_idx = 0
    # else:
        # raw_idx = math.floor(math.log10(abs(number)) / 3)

    # raw_idx = int(raw_idx)

    # idx = min(raw_idx, len(millnames) - 1)
    # idx = max(0, idx)

    millnames = ['', 'K', 'M', 'B', 'T']
    idx = max(
        0, 
        min(
            len(millnames) - 1, 
            int(math.floor(0 if number == 0 else math.log10(abs(number)) / 3))
        )
    )

    scaled = number / 10**(3 * idx)
    return f"{scaled:.1f}{millnames[idx]}"