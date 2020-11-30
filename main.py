import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from Fuzzy_System import read_data
import re


def build_fuzzy_universe(fuzzy_sets, rulebase_name):
    universe_variables = {}
    # create custom membership functions for variable, for each of its statuses.
    for variable_name, variable_statuses in fuzzy_sets.items():
        # find range of statuses values for each variable - aka their smallest and highest value
        small_values = []
        large_values = []
        for variable_status in variable_statuses:
            # take the smallest/largest value for each status
            small_values.append(min(variable_status[1]))
            large_values.append(max(variable_status[1]))
        # then take the smallest/largest value among all statuses
        smallest = min(small_values)
        largest = max(large_values)
        # now create the ctrl universe variable using the aforementioned range
        if variable_name.lower() == rulebase_name.lower():
            # the +2 is currently a mystery - doesn't work without it
            universe_variables[variable_name] = ctrl.Consequent(np.arange(smallest, largest+2), variable_name)
        else:
            universe_variables[variable_name] = ctrl.Antecedent(np.arange(smallest, largest+2), variable_name)
        # adding each of the statuses and their values to the universe variables
        for status in variable_statuses:
            status_name = status[0]
            status_values = status[1]
            if len(status_values) == 3:
                universe_variables[variable_name][status_name] = fuzz.trimf(universe_variables[variable_name].universe,
                                                                         status_values)
            if len(status_values) == 4:
                universe_variables[variable_name][status_name] = fuzz.trapmf(universe_variables[variable_name].universe,
                                                                         status_values)
    return universe_variables


def build_rules(rules, variables):
    args = 1
    ctrl_rules = []
    for rule in rules:
        keywords = re.findall('(\w+) is (\w+)', rule)
        for i in range(0, len(keywords)-1):
            if i == 0:
                args = variables[keywords[i][0]][keywords[i][1]]
            else:
                if "and" in rule.lower():
                    args = args & variables[keywords[i][0]][keywords[i][1]]
                elif "or" in rule.lower():
                    args = args | variables[keywords[i][0]][keywords[i][1]]
                else:
                    args = args
        then_statement = variables[keywords[-1][0]][keywords[-1][1]]
        ctrl_rules.append(ctrl.Rule(args, then_statement))
    return ctrl_rules


def defuzzify(rules, measurements):
    rule_ctrl = ctrl.ControlSystem(rules)
    rulebase = ctrl.ControlSystemSimulation(rule_ctrl)
    for variable, value in measurements.items():
        rulebase.input[variable] = value
    rulebase.compute()
    return rulebase


def is_data_valid(fuzzy_sets, rules, measurements):
    if len(fuzzy_sets) == 0 or len(rules) == 0 or len(measurements) == 0:
        print("ERROR: One of the sections is empty!")
    if len(fuzzy_sets) <= len(measurements):
        print("ERROR: Not enough fuzzy sets present in the input, or too many measurements have been included. "
              "Make sure a fuzzy set is present for the consequent variable as well!")
    if not all(key in fuzzy_sets.keys() for key in rules.keys()):
        print("ERROR: Couldn't recognise some of the RuleBase names! The RuleBase names "
              "need to correspond names of the consequent variables.")
    else:
        return True



def main():
    # first, read the main file and separate the sections
    input_txt = read_data.read_input_txt("rules_and_data")
    if not input_txt:
        print("The headers '[Rulebase]', '[FuzzySets]' and '[Measurements]' are required before each section. "
              "Please make sure they are included in the input file and try again. Exiting...")
        exit(1)

    # then, format the sections according to need
    fuzzy_sets = read_data.format_fuzzy_sets(input_txt["fuzzysets"])  # dict of dicts
    rules = read_data.format_rules(input_txt["rulebase"])  # dict of tuples
    measurements = read_data.format_measurements(input_txt["measurements"])  # dict

    if not is_data_valid(fuzzy_sets, rules, measurements):
        print("The input data is not valid. Please check the message above for more details. Exiting...")
        exit(1)

    # print("Measurements: ")
    # print(measurements)
    # print("Fuzzy Sets: ")
    # print(fuzzy_sets)
    # print("Rule Base:")
    # print(rules)

    # we build a different fuzzy universe for each rule base (in case there are multiple given)!
    for rulebase_name, rules_values in rules.items():
        universe_variables = build_fuzzy_universe(fuzzy_sets, rulebase_name)
        ctrl_rules = build_rules(rules_values, universe_variables)
        # once the rules and universe variables have been created, defuzzify rule base unknown value
        calculated_rulebase = defuzzify(ctrl_rules, measurements)
        print("The defuzzified value for " + rulebase_name + " is:")
        print(calculated_rulebase.output[rulebase_name])
        #print(universe_variables["Tip"].view())


if __name__ == "__main__":
    main()
