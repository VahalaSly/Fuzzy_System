import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from Fuzzy_System import read_data


def build_fuzzy_universe(fuzzy_sets, rulebase_name):
    universe_variables = {}
    for variable_name, variable_statuses in fuzzy_sets.items():
        # TODO: Figure out way to establish lowest and highest values for status? More for loops? (Pain??)
        if variable_name.lower() == rulebase_name.lower():
            universe_variables[variable_name] = ctrl.Consequent(np.arange(-10, 50), variable_name)
        else:
            universe_variables[variable_name] = ctrl.Antecedent(np.arange(-10, 50), variable_name)
        for status in variable_statuses:
            status_name = status[0]
            status_values = status[1]
            # create custom membership functions for variable, for each of its statuses.
            universe_variables[variable_name][status_name] = fuzz.trapmf(universe_variables[variable_name].universe, status_values)






def main():
    input_txt = read_data.read_input_txt("rules_and_data")
    rulebase_input = input_txt["rulebase"]
    fuzzysets_input = input_txt["fuzzysets"]
    measurements_input = input_txt["measurements"]

    fuzzy_sets = read_data.format_fuzzy_sets(fuzzysets_input)        #dict of dicts
    rules = read_data.format_rules(rulebase_input)                   #dict of tuples
    measurements = read_data.format_measurements(measurements_input) #dict

    print("Measurements: ")
    print(measurements)
    print("Fuzzy Sets: ")
    print(fuzzy_sets)
    print("Rule Base:")
    print(rules)

    # we build a different fuzzy universe for each rule base!
    for rulebase_name,rules_value in rules.items():
        build_fuzzy_universe(fuzzy_sets, rulebase_name)


if __name__ == "__main__":
    main()
