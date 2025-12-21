import json
import numpy as np

def load_data_from_file(filepath):
    """Загружает сырой JSON контент из файла"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()

def calculate_membership_degree(input_val, fuzzy_set):
    """Вычисляет степень принадлежности для заданного множества"""
    sorted_points = sorted(fuzzy_set, key=lambda pt: pt[0])
    x_coords = [pt[0] for pt in sorted_points]
    y_coords = [pt[1] for pt in sorted_points]
    
    n_points = len(sorted_points)
    if n_points < 2:
        return 0.0
    
    if input_val <= x_coords[0]:
        return y_coords[0]
    if input_val >= x_coords[-1]:
        return y_coords[-1]
    
    for idx in range(n_points - 1):
        if x_coords[idx] <= input_val <= x_coords[idx + 1]:
            delta_x = x_coords[idx + 1] - x_coords[idx]
            if delta_x == 0:
                return (y_coords[idx] + y_coords[idx + 1]) / 2
            delta_y = y_coords[idx + 1] - y_coords[idx]
            return y_coords[idx] + (delta_y * (input_val - x_coords[idx]) / delta_x)
    return 0.0

def apply_fuzzification(input_value, input_fuzzy_sets):
    """Применяет фазификацию ко всем терминам входной переменной"""
    fuzzy_result = {}
    for fuzzy_term in input_fuzzy_sets:
        fuzzy_result[fuzzy_term['id']] = calculate_membership_degree(input_value, fuzzy_term['points'])
    return fuzzy_result

def determine_output_bounds(output_fuzzy_sets):
    """Определяет границы выходного диапазона"""
    all_coords = []
    for term_set in output_fuzzy_sets:
        all_coords.extend([pt[0] for pt in term_set['points']])
    return (min(all_coords), max(all_coords)) if all_coords else (0, 10)

def combine_fuzzy_outputs(fuzzy_acts, rule_base, output_sets, output_grid):
    """Агрегирует выходные нечёткие множества по правилам"""
    aggregated_mu = np.zeros(len(output_grid))
    
    for activation_level, fuzzy_rule in zip(fuzzy_acts, rule_base):
        premise_term, conclusion_term = fuzzy_rule
        target_output_set = next((s for s in output_sets if s['id'] == conclusion_term), None)
        
        if not target_output_set or activation_level == 0:
            continue
            
        output_memberships = np.array([calculate_membership_degree(val, target_output_set['points']) 
                                     for val in output_grid])
        
        clipped_output = np.minimum(activation_level, output_memberships)
        aggregated_mu = np.maximum(aggregated_mu, clipped_output)
    
    return aggregated_mu

def resolve_fuzzy_output(grid_values, membership_vector):
    """Разфацификация методом середины максимума"""
    if len(membership_vector) == 0:
        return 0.0
        
    peak_value = np.max(membership_vector)
    if peak_value == 0:
        return 0.0
    
    peak_indices = np.where(np.isclose(membership_vector, peak_value, atol=1e-6))[0]
    if len(peak_indices) == 0:
        return 0.0
    
    first_peak = grid_values[peak_indices[0]]
    last_peak = grid_values[peak_indices[-1]]
    return (first_peak + last_peak) / 2

def calculate_fuzzy_control(current_temp, input_sets, output_sets, fuzzy_rules, grid_resolution=1001):
    """Вычисляет оптимальное управление по нечёткой логике"""
    output_min, output_max = determine_output_bounds(output_sets)
    control_grid = np.linspace(output_min, output_max, grid_resolution)
    
    input_fuzzification = apply_fuzzification(current_temp, input_sets)
    rule_activations = [input_fuzzification.get(rule[0], 0.0) for rule in fuzzy_rules]
    
    combined_output = combine_fuzzy_outputs(rule_activations, fuzzy_rules, output_sets, control_grid)
    optimal_control = resolve_fuzzy_output(control_grid, combined_output)
    
    return optimal_control

def process_fuzzy_system(input_config='lvinput.json', output_config='lvoutput.json', 
                        rules_config='rules.json', target_temp=19.0):
    """Главная функция обработки нечёткой системы управления"""
    input_raw = load_data_from_file(input_config)
    output_raw = load_data_from_file(output_config)
    rules_raw = load_data_from_file(rules_config)
    
    input_linguistic = json.loads(input_raw)
    output_linguistic = json.loads(output_raw)
    inference_rules = json.loads(rules_raw)
    
    temperature_terms = input_linguistic["температура"]
    heating_terms = output_linguistic["нагрев"]
    
    control_value = calculate_fuzzy_control(target_temp, temperature_terms, heating_terms, inference_rules)
    return control_value

if __name__ == "__main__":
    result = process_fuzzy_system(T=19.0)
    print(f"Оптимальное значение нагрева при 19.0°C: {result:.2f}")
