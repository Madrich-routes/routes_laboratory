# Средние скорости взяты отсюда
# https://rg.ru/2019/01/22/reg-cfo/sredniaia-skorost-dvizheniia-v-moskve-s-2010-goda-uvelichilas-na-18.html#:~:text=%D0%9D%D0%B0%20%D1%81%D0%B5%D0%B3%D0%BE%D0%B4%D0%BD%D1%8F%D1%88%D0%BD%D0%B8%D0%B9%20%D0%B4%D0%B5%D0%BD%D1%8C%20%D1%81%D1%80%D0%B5%D0%B4%D0%BD%D1%8F%D1%8F%20%D1%81%D1%83%D1%82%D0%BE%D1%87%D0%BD%D0%B0%D1%8F,%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%8B%20%D1%81%D1%80%D0%B0%D0%B7%D1%83%20%D0%BF%D0%BE%20%D0%BD%D0%B5%D1%81%D0%BA%D0%BE%D0%BB%D1%8C%D0%BA%D0%B8%D0%BC%20%D0%BD%D0%B0%D0%BF%D1%80%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F%D0%BC.
# https://ru.wikipedia.org/wiki/%D0%9A%D0%B8%D0%BB%D0%BE%D0%BC%D0%B5%D1%82%D1%80_%D0%B2_%D1%87%D0%B0%D1%81

# https://www.researchgate.net/figure/List-of-pedestrian-mean-speed-in-different-countries_tbl1_280980330
FOOT_SPEEDS = {
    "min": 1.08,
    "avg": 5 / 3.6,  # это курьер, он должен торопиться!
    "max": 7 / 3.6,  # Очень быстро это 9, а у нас еще светофоры и прочее
}

# https://rollmaster.ru/info/Skorost-velosipeda_538_article.html
BICYCLE_SPEEDS = {
    "min": 7 / 3.6,
    "avg": 13 / 3.6,
    "max": 25 / 3.6,
}

CAR_NO_TRAFFIC_SPEEDS = {
    "min": 25 / 3.6,
    "avg": 45 / 3.6,
    "max": 60 / 3.6,
}

CAR_TRAFFIC_SPEEDS = {
    "min": 1,
    "avg": 24 / 3.6,
    "max": 56 / 3.6,
}
