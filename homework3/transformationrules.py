def combinations(size):
    combs = []
    activity = [0] * size
    def __combine(index):
        if index == size:
            combs.append(activity[:])
        else:
            for j in [0, 1]:
                activity[index] = j
                __combine(index + 1)
    __combine(0)
    return combs

def take_active(arr, active_indexes):
    return [arr[index] for index, activity in enumerate(active_indexes) if activity]

def take_inactive(arr, active_indexes):
    return [arr[index] for index, activity in enumerate(active_indexes) if not activity]

def wrap(accum, f):
    return lambda x: f(accum(x))

def build_function_composition(func_arr):
    result_func = lambda x: x
    for func in func_arr:
        result_func = wrap(result_func, func)
    return result_func

commutative_rules = [
    lambda x: x.replace('o', '0'),
    lambda x: x.replace('i', '1'),
    lambda x: x.replace('e', '3')
]
capitalization_rule = lambda x: x.title()

# Build transformation rules
transform_rules = []
for active_config in combinations(len(commutative_rules)):
    active_functions = take_active(commutative_rules, active_config)
    transform_rules.append(build_function_composition(active_functions))

    for before_capitalization in combinations(len(active_functions)):
        functions_before = take_active(active_functions, before_capitalization)
        functions_after = take_inactive(active_functions, before_capitalization)
        
        before_function = build_function_composition(functions_before)
        after_function = build_function_composition(functions_after)

        acc = lambda x: x
        for func in [before_function, capitalization_rule, after_function]:
            acc = wrap(acc, func)
        transform_rules.append(acc)

def apply_transformation_rules(text):
    return list(set(map(lambda f: f(text), transform_rules)))