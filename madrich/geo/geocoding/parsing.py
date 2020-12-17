"""В этом модуле реализован функционал извлечения осмысленной информации из адреса."""


def get_address(address: str):
    """Нормализцем адрес."""
    if not address:
        return None
    tokens = address.split(',')

    black_list = [
        'подъезд',
        'код домофона',
        "эт",
        'этаж',
        "кв",
        "квартира",
        "корп.",
        "корп ",
        "позвонить",
        "код",
        "домофон",
        "пом",
        "дмф",
        "помещение",
        "п-д",
    ]
    white_list = [
        "Московская ",
        "улица ",
        "дом ",
        "д. ",
        "ул. ",
        "г. ",
        "пр-кт ",
        "проспект ",
    ]

    address = []
    for token in tokens:
        if any(x in token for x in white_list):
            address.append(token)
            continue
        if any(x in token for x in black_list):
            continue
        address.append(token)
    address = ' '.join(address)
    return address
