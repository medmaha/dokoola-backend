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


#
def get_month_name(month: int) -> str:

    if month < 1:
        month = 1
    if month > 12:
        month = 12

    # Month 1-12
    return months[month - 1]


def get_month_index(month: str) -> int:
    for index, m in enumerate(months):
        if m == month:
            return index
    return 1
