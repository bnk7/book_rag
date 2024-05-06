def dict_to_commas(data: dict[str, str]) -> str:
    """
    Return a nicely formatted readable version of the values of a dictionary.

    Args:
        data (dict[str, str]): The dictionary to be formatted
    Returns:
        String representing the values of the dictionary
    """
    items = list(data.values())
    if len(items) > 2:
        output = ', '.join(items[:-1]) + ', and ' + items[-1]
    elif len(items) == 2:
        output = items[0] + ' and ' + items[1]
    else:
        output = items[0]
    return output


def convert_date(date: str) -> str:
    """Converts the given date from yyyy-mm-dd format to month day, year format.

    Args:
        date (str): The date to convert
    Returns:
        String representing the reformatted date
    """
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    year = date[:4]
    month = months[int(date[5:7])]
    day = date[-2:]

    return month + " " + day + ", " + year