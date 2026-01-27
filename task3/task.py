import json
import numpy as np

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()
        return content

def warshall_algorithm(matrix):
    n = len(matrix)
    closure = matrix.copy()
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                closure[i, j] = closure[i, j] or (closure[i, k] and closure[k, j])
    
    return closure

def find_connected_components(closure_matrix):
    n = len(closure_matrix)
    visited = [False] * n
    components = []
    
    for i in range(n):
        if not visited[i]:
            component = []
            for j in range(n):
                if closure_matrix[i, j] and closure_matrix[j, i]:
                    component.append(j + 1)
                    visited[j] = True
            components.append(sorted(component))
    
    return components

def compare_clusters(cluster1, cluster2, C_matrix):
    i = cluster1[0] - 1
    j = cluster2[0] - 1
    
    if C_matrix[i, j] == 1 and C_matrix[j, i] == 0:
        return -1
    elif C_matrix[i, j] == 0 and C_matrix[j, i] == 1:
        return 1
    else:
        return 0

def main(json_a, json_b):
    rank_a = json.loads(json_a)
    rank_b = json.loads(json_b)
   
    all_objs = set()
    for rank in [rank_a, rank_b]:
        for cluster in rank:
            if not isinstance(cluster, list):
                cluster = [cluster]
            all_objs.update(cluster)
   
    if not all_objs:
        return {"kernel": [], "consistent_ranking": []}
    
    n = max(all_objs)
   
    def build_matrix(rank):
        pos = [0] * n
        current_pos = 0
        for cluster in rank:
            if not isinstance(cluster, list):
                cluster = [cluster]
            for obj in cluster:
                pos[obj - 1] = current_pos
            current_pos += 1
       
        mat = np.zeros((n, n), dtype=int)
        for i in range(n):
            for j in range(n):
                if pos[i] >= pos[j]:
                    mat[i, j] = 1
        return mat
   
    YA = build_matrix(rank_a)
    YB = build_matrix(rank_b)
   
    YAB = YA * YB
    YA_T = YA.T
    YB_T = YB.T
    YAB_prime = YA_T * YB_T
   
    kernel = []
    for i in range(n):
        for j in range(i + 1, n):
            if YAB[i, j] == 0 and YAB_prime[i, j] == 0:
                kernel.append([i + 1, j + 1])
    
    P1 = YA * YB_T
    P2 = YA_T * YB
    P = np.logical_or(P1, P2).astype(int)
    
    C = YA * YB

    for pair in kernel:
        i, j = pair[0] - 1, pair[1] - 1
        C[i, j] = 1
        C[j, i] = 1
    
    E = C * C.T

    E_star = warshall_algorithm(E)
    
    clusters = find_connected_components(E_star)
    
    cluster_matrix = np.zeros((len(clusters), len(clusters)), dtype=int)
    
    for i in range(len(clusters)):
        for j in range(len(clusters)):
            if i != j:
                elem_i = clusters[i][0] - 1
                elem_j = clusters[j][0] - 1
                if C[elem_i, elem_j] == 1:
                    cluster_matrix[i, j] = 1
    
    visited = [False] * len(clusters)
    result_order = []
    
    def topological_sort(v):
        visited[v] = True
        for u in range(len(clusters)):
            if cluster_matrix[v, u] == 1 and not visited[u]:
                topological_sort(u)
        result_order.append(v)
    
    for i in range(len(clusters)):
        if not visited[i]:
            topological_sort(i)
    
    result_order.reverse()

    consistent_ranking = []
    for idx in result_order:
        cluster = clusters[idx]
        if len(cluster) == 1:
            consistent_ranking.append(cluster[0])
        else:
            consistent_ranking.append(cluster)
    
    return {
        "kernel": kernel,
        "consistent_ranking": consistent_ranking
    }

if __name__ == "__main__":
    json_a = read_json_file('range_a.json')
    json_b = read_json_file('range_b.json')
    json_c = read_json_file('range_c.json')
    
    print("СРАВНЕНИЕ РАНЖИРОВОК")
    
    print("\nrange_a.json vs range_b.json")
    result_ab = main(json_a, json_b)
    print(f"Ядро противоречий: {result_ab['kernel']}")
    print(f"Согласованная ранжировка: {result_ab['consistent_ranking']}")
    
    print("\nrange_a.json vs range_c.json")
    result_ac = main(json_a, json_c)
    print(f"Ядро противоречий: {result_ac['kernel']}")
    print(f"Согласованная ранжировка: {result_ac['consistent_ranking']}")
    
    print("\nrange_b.json vs range_c.json")
    result_bc = main(json_b, json_c)
    print(f"Ядро противоречий: {result_bc['kernel']}")
    print(f"Согласованная ранжировка: {result_bc['consistent_ranking']}")
