def iget(d, *args, default=None):
    """
    Получаем значение, по пути во вложенном словаре
    """
    res = d
    for a in args[:-1]:
        res = d.get(a, {})

    return res.get(args[-1], default)
