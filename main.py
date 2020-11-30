import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from Fuzzy_System import read_data
import re


def build_fuzzy_universe(fuzzy_sets, rulebase_name):
    universe_variables = {}
    # create custom membership functions for variable, for each of its statuses.
    for variable_name, variable_statuses in fuzzy_sets.items():
        # TODO: Figure out way to establish lowest and highest values for status? More for loops? (Pain??)
        if variable_name.lower() == rulebase_name.lower():
            universe_variables[variable_name] = ctrl.Consequent(np.arange(-10, 50), variable_name)
        else:
            universe_variables[variable_name] = ctrl.Antecedent(np.arange(-10, 50), variable_name)
        for status in variable_statuses:
            status_name = status[0]
            status_values = status[1]
            universe_variables[variable_name][status_name] = fuzz.trapmf(universe_variables[variable_name].universe, status_values)
    return universe_variables


def build_rules(rules, variables):
    ctrl_rules = []
    for rule in rules:
        args = []
        # TODO: Dynamic creation of rules args to allow for multiple and/or
        keywords = re.findall('(\w+) is (\w+)', rule)
        if "and" in rule.lower():
            ctrl_rules.append(
                ctrl.Rule(variables[keywords[0][0]][keywords[0][1]] & variables[keywords[1][0]][keywords[1][1]],
                          variables[keywords[2][0]][keywords[2][1]]))
        elif "or" in rule.lower():
            ctrl_rules.append(
                ctrl.Rule(variables[keywords[0][0]][keywords[0][1]] | variables[keywords[1][0]][keywords[1][1]],
                          variables[keywords[2][0]][keywords[2][1]]))
        else:
            ctrl_rules.append(
                ctrl.Rule(variables[keywords[0][0]][keywords[0][1]], variables[keywords[1][0]][keywords[1][1]]))
    return ctrl_rules


def defuzzify(rules, measurements):
    rule_ctrl = ctrl.ControlSystem(rules)
    rulebase = ctrl.ControlSystemSimulation(rule_ctrl)
    for variable,value in measurements.items():
        rulebase.input[variable] = value
    # Crunch the numbers
    rulebase.compute()
    return rulebase


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
    for rulebase_name, rules_values in rules.items():
        universe_variables = build_fuzzy_universe(fuzzy_sets, rulebase_name)
        ctrl_rules = build_rules(rules_values, universe_variables)
        calculated_rulebase = defuzzify(ctrl_rules, measurements)
        print("The defuzzified value for " + rulebase_name + " is:")
        print(calculated_rulebase.output[rulebase_name])


if __name__ == "__main__":
    main()
