import csv
# #v: list[str] = ["v1", "v2", "v3", "v4"] #sorted
# v: set[str] = {"v1", "v2", "v3", "v4"} #unsorted
# E: set[tuple[str, str, float]] = {("v1", "v2", 25), ("v1", "v3", 12), ("v3", "v4", 3.0), ("v4", "v1", 4.0)} #множество рёбер (v1, v2, weight)
# #вообще хотим сохранять в файл
# G = (v, E) #граф - кортеж из вершин и рёбер
# #читаем csv файл и возвращаем половину матрицы смежности, пишем функцию, которая на вход получаем строчку, а на выходе вовращает каждую строчку list[list]

with open("task0/task2.csv", "r", encoding="utf-8") as f:
    csv_string = f.read().split("\n")
#print(csv_string)

def main(csv_graph: str) -> list[list[int]]:
    edges = [] #список рёбер кортеж (v1, v2)
    vertices = set() #множество вершин
    for line in csv_graph:
        a = line.split(",")
        v1 = a[0]
        v2 = a[1]
        edges.append((v1, v2))
        vertices.add(v1)
        vertices.add(v2)
    vertices = sorted(vertices)
    n = len(vertices)
    index = {vertices[i]: i for i in range(n)} #ключ  вершина значение  индекс вершины
    #print(index)
    matrix = [[0] * n for _ in range(n)] #матрица смежности
    for v1, v2 in edges:
        i = index[v1]
        j = index[v2]
        matrix[i][j] = 1
        matrix[j][i] = 1 
    return matrix       

print(main(csv_string))







