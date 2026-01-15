import json
import numpy as np

def main() -> None:
    def load_ranking(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def parse_ranking(raw_json):
        return json.loads(raw_json)

    def extract_all_items(rankings):
        items = set()
        for ranking in rankings:
            for group in ranking:
                group_items = group if isinstance(group, list) else [group]
                items.update(group_items)
        return sorted(items)

    def position_map(ranking, max_item):
        positions = [0] * max_item
        pos_index = 0
        for group in ranking:
            group = group if isinstance(group, list) else [group]
            for item in group:
                positions[item - 1] = pos_index
            pos_index += 1
        return positions

    def dominance_matrix(pos):
        n = len(pos)
        mat = np.zeros((n, n), dtype=int)
        for i in range(n):
            for j in range(n):
                if pos[i] >= pos[j]:
                    mat[i, j] = 1
        return mat

    def compute_conflict_kernel(mat1, mat2):
        n = mat1.shape[0]
        kernel = []
        common_zero = (mat1 == 0) & (mat2 == 0)
        transp_zero = (mat1.T == 0) & (mat2.T == 0)
        for i in range(n):
            for j in range(i + 1, n):
                if common_zero[i, j] and transp_zero[i, j]:
                    kernel.append([i + 1, j + 1])
        return kernel

    def compare_rankings(ranking_a, ranking_b):
        all_items = extract_all_items([ranking_a, ranking_b])
        if not all_items:
            return []
        n = max(all_items)
        pos_a = position_map(ranking_a, n)
        pos_b = position_map(ranking_b, n)
        dom_a = dominance_matrix(pos_a)
        dom_b = dominance_matrix(pos_b)
        return compute_conflict_kernel(dom_a, dom_b)

    def compare_files(file1, file2):
        r1 = parse_ranking(load_ranking(file1))
        r2 = parse_ranking(load_ranking(file2))
        return compare_rankings(r1, r2)

    print("СРАВНЕНИЕ РАНЖИРОВОК")

    ab_kernel = compare_files('range_a.json', 'range_b.json')
    print("range_a.json vs range_b.json")
    print(f"Ядро противоречий: {ab_kernel}")

    ac_kernel = compare_files('range_a.json', 'range_c.json')
    print("\nrange_a.json vs range_c.json")
    print(f"Ядро противоречий: {ac_kernel}")

    bc_kernel = compare_files('range_b.json', 'range_c.json')
    print("\nrange_b.json vs range_c.json")
    print(f"Ядро противоречий: {bc_kernel}")

if __name__ == "__main__":
    main()
