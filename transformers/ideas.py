
"""

1. Класс добавляющий очень дорогие машины с бесконечной вместимостью, чтобы все можно было вывезти

2. Трансформер, который меняет ограничения проблемы таким образом, чтобы ее было легче решить

3. Ограничения преобразуются в штрафы.

4. Убираем всякие inf, nan и тд, которые могут быть в проблеме

5. Приводим все что можно к интам

6. Удаляем ненужные ребра (не кандидаты). Или ставим их веса в inf, чтобы точно не хотелось брать

7. Изменяем id, который пришел в API, на призвольный

8. Добавляем какие-нибудь фиктивные вершины

9. Или удаляем лишние вершины или ребра, которые не нужны

10. Склеиваем часть пути в одну вершину и дальше используем ее как одну вершину

11. Преобразуем проблему в кластеризованную проблему

12. Нормализуем расстояния. Нормализуем capacity.

13. Разбиваем одну проблему на несколько. По кластерам. Или на разные дни.

14. Time dependent problem -> usual
В этой работе мельком обмолвились, что так можно
(A constructive heuristic for time-dependent multi-depot vehicle routing
 problem with time-windows and heterogeneous fleet)

15. Приоритеты заказчиков к целевой функции, например

16. Разные постпроцессоры. (Их можно в принципе вынести в отдельный модуль)

17. TODO: Любые классы проблем или классы трансформеров начнут протекать.
 Ровно так, как это было с векторными потоками. И как это было с опасным солвером.
 Там пришлось всю иерархию классов делать по новой. Как с этим быть?

18. Объединять заявки, которые нужно обязательно обслужить или вывезти вместе

19. Трансформер от наивного вывода к результату?

20. Трансформеры сделать как пайплайны в sklearn

"""
