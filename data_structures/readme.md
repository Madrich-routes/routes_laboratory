# Используемые структуры данных и индекс по ним

## Индексация точек и поиск ближайших соседей

1. KD-tree
    1. sklearn.neighbors.KDTree
    2. scipy.spatial.KDTree
    
2. R-tree и всякие индексы
    1. https://pypi.org/project/Rtree/
    
3. Можно использовать Range-trees для геометрических

4. Interval tree — проверять попадание в интервалы
    1. Быстрая украденная из ядра https://github.com/biocore-ntnu/kerneltree
    2. https://pypi.org/project/intervaltree/
    
5. The Nested Containment List 
    1. Почти то же, что интервал, но быстрее https://github.com/biocore-ntnu/ncls
    2. Для временных окон должно быть круто

6. Удобно определять в какой отрезок попадаешь
    1. https://github.com/nanobit/rangetree

7. Quad-trees - еще один норм индекс (Надо бы изучить)

8. Bucket hashing

Geopandas вроде бы многое умеет

### Пара лекций
1. https://www.cise.ufl.edu/class/cot5520sp18/CG_RangeTrees.pdf
2. https://www.cise.ufl.edu/class/cot5520sp15/CG_RangeKDtrees.pdf
3. https://www.cs.cmu.edu/~ckingsf/bioinfo-lectures/rangetrees.pdf
4. https://en.wikipedia.org/wiki/Fractional_cascading


