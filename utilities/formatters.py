months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

def get_month_name_by_index(index: int) -> str:
    if index < 0:
        index = 1
    if index > 12:
        index = 12
    return months[index - 1]


def get_month_index_by_name(month: str) -> int:
    month = month.lower()
    for index, m in enumerate(months):
        if m.lower() == month:
            return index
    return 1
