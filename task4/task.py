import json
import numpy as np

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()
        return content

def membership(x, points):
    points = sorted(points, key=lambda p: p[0])
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    
    if len(points) < 2:
        return 0.0
    
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            dx = xs[i + 1] - xs[i]
            if dx == 0:
                return (ys[i] + ys[i + 1]) / 2
            dy = ys[i + 1] - ys[i]
            return ys[i] + dy * (x - xs[i]) / dx
    return 0.0

def fuzzify(value, ling_var):
    result = {}
    for term in ling_var:
        result[term['id']] = membership(value, term['points'])
    return result

def get_output_range(control_ling_var):
    all_x = []
    for term in control_ling_var:
        all_x.extend(p[0] for p in term['points'])
    if not all_x:
        return 0, 10
    return min(all_x), max(all_x)

def aggregate_membership(activations, rules, control_ling_var, s_values):
    mu_agg = np.zeros(len(s_values), dtype=float)
    for act, rule in zip(activations, rules):
        input_id, output_id = rule
        output_term = next((t for t in control_ling_var if t['id'] == output_id), None)
        if output_term is None or act == 0:
            continue

        mu_out = np.array([membership(s, output_term['points']) for s in s_values])

        mu_clipped = np.minimum(act, mu_out)

        mu_agg = np.maximum(mu_agg, mu_clipped)
    return mu_agg

def defuzzify_first_of_max(s_values, mu_agg):
    if len(mu_agg) == 0:
        return 0.0
    max_mu = np.max(mu_agg)
    if max_mu == 0:
        return 0.0
    for i, mu in enumerate(mu_agg):
        if np.isclose(mu, max_mu, atol=1e-6):
            return s_values[i]
    return 0.0


def compute_optimal_control(T, temp_ling_var, control_ling_var, rules, steps=1001):
    s_min, s_max = get_output_range(control_ling_var)
    s_values = np.linspace(s_min, s_max, steps)

    mu_input = fuzzify(T, temp_ling_var)

    activations = [mu_input.get(rule[0], 0.0) for rule in rules]

    mu_agg = aggregate_membership(activations, rules, control_ling_var, s_values)

    s_opt = defuzzify_first_of_max(s_values, mu_agg)
    
    return s_opt


def main(lvinput_path='lvinput.json', lvoutput_path='lvoutput.json', rules_path='rules.json', T=19.0):
    lvinput_json = read_json_file(lvinput_path)
    lvoutput_json = read_json_file(lvoutput_path)
    rules_json = read_json_file(rules_path)

    temp_data = json.loads(lvinput_json)
    control_data = json.loads(lvoutput_json)
    rules = json.loads(rules_json)

    temp_ling_var = temp_data["температура"]
    control_ling_var = control_data["нагрев"]

    s_opt = compute_optimal_control(T, temp_ling_var, control_ling_var, rules)
    return s_opt

if __name__ == "__main__":
    optimal_s = main(T=19.0)
    print(f"Для температуры 19.0°C оптимальное управление: {optimal_s:.2f}")
