import os
import numpy as np

def main(v: str, eroot: str) -> tuple[list[list[int]], list[list[int]], list[list[int]], list[list[int]], list[list[int]]]:
    lines = v.strip().split('\n')
    edges = []
    verts = set()

    for line in lines:
        if line.strip():
            v1, v2 = line.split(',')
            v1 = v1.strip()
            v2 = v2.strip()
            verts.add(v1)
            verts.add(v2)
            edges.append((v1, v2))

    other_verts = sorted(v for v in verts if v != eroot)
    verts = [eroot] + other_verts
    n = len(verts)
    vert_index = {v: i for i, v in enumerate(verts)}

    adj = np.zeros((n, n), dtype=bool)
    for v1, v2 in edges:
        i = vert_index[v1]
        j = vert_index[v2]
        adj[i, j] = True

    r1_np = adj.astype(int)

    r2_np = r1_np.T

    tranzitive_r = adj.copy()
    for _ in range(1, n):
        tranzitive_r = tranzitive_r | (tranzitive_r @ adj)

    r3_np = (tranzitive_r & ~adj).astype(int)

    r4_np = r3_np.T

    r2_bool = r2_np.astype(bool)
    r5_np = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if np.any(r2_bool[i] & r2_bool[j]):
                r5_np[i, j] = 1
                r5_np[j, i] = 1

    return (
        r1_np.tolist(),
        r2_np.tolist(),
        r3_np.tolist(),
        r4_np.tolist(),
        r5_np.tolist()
    )

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "task1.csv")

    with open(csv_path, "r") as file:
        input_data = file.read()

    eroot = input("Введите значение корневой вершины: ").strip()
    matrices = main(input_data, eroot)

    relations = ["r1 (управление)", "r2 (подчинение)", "r3 (опосредованное управление)",
                 "r4 (опосредованное подчинение)", "r5 (соподчинение)"]

    for rel_name, matrix in zip(relations, matrices):
        print(f"\nМатрица для отношения {rel_name}:")
        for row in matrix:
            print(row)
