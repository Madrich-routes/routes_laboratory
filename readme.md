# Routing lab

Всевозможные тулзы, используемые при построении оптимальных маршрутов

# Описание

Структура проекта:
1. Она тут появится, когда стабилизируется

# Процесс разработки

1. master — стабильная ветка для использования в демо и тд.
2. develop — ветка с основной разработкой. Скорее всего все самое новое тут
3. Также есть ветки с отдельными фичами

# Установка и начало использования

1. Зависимости проекта устанавливаются через poetry
2. Для форматирования

# Правила и договоренности

### Единицы измерения и хранение
1. Координаты везде задаются в np.array(lat, lon) (Широта, Долгота), (55.75, 37.61) — Москва
2. Время задается в timestamp в секундах (int)
3. Расстояние задается в метрах (int)
4. Скорость в метрах в секунду — float
5. Вес в килограмах
6. Объем в литрах

Если что-то можно написать переиспользуемым — так и нужно сделать
