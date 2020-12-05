import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from Fuzzy_System import Read_Data
import re
import logging


def build_fuzzy_universe(fuzzy_sets, consequent):
    universe_variables = {}
    # create custom membership functions for variable, for each of its statuses.
    for variable_name, variable_statuses in fuzzy_sets.items():
        try:
            # find range of statuses values for each variable - aka their smallest and highest value
            smallest, largest = find_minmax_values(variable_statuses)
            # now create the ctrl universe variable using the aforementioned range
            if variable_name.lower() == consequent.lower():
                # the +2 is currently a mystery - doesn't work without it
                universe_variables[variable_name] = ctrl.Consequent(np.arange(smallest, largest), variable_name)
            else:
                universe_variables[variable_name] = ctrl.Antecedent(np.arange(smallest, largest), variable_name)
            # adding each of the statuses and their values to the universe variables
            for status in variable_statuses:
                status_name = status[0]
                status_values = status[1]
                universe_variables[variable_name][status_name] = fuzz.trapmf(universe_variables[variable_name].universe,
                                                                                 status_values)
        except Exception as e:
            logging.error(e)
    return universe_variables


def find_minmax_values(variable_statuses):
    small_values = []
    large_values = []
    for variable_status in variable_statuses:
        try:
            # take the smallest/largest value for each status
            small_values.append(min(variable_status[1]))
            large_values.append(max(variable_status[1]))
        except Exception as e:
            logging.error(e)
    # then take the smallest/largest value among all statuses
    smallest = min(small_values)
    largest = max(large_values)
    return smallest, largest


def build_fuzzy_rules(rules, variables):
    args = 1
    ctrl_rules = []
    for rule in rules:
        try:
            rule_split = rule.split("then")
            antecedents = dict(re.findall('(\w+)\s*is\s*[not\s]*(\w+)', rule_split[0]))
            consequents = re.findall('(\w+)\s*is\s*[not\s]*(\w+)', rule_split[1])
            words_in_rule = rule_split[0].split(" ")
            # loops through the antecedent part of the rule. If it finds and/or,
            # it grabs the next word as the antecedent and adds it to the rules
            # if it finds `not', it appends it to the rule
            for i in range(3, len(words_in_rule)):
                try:
                    if words_in_rule[i-3] == "if":
                        args = variables[words_in_rule[i-2]][antecedents[words_in_rule[i-2]]]
                    elif words_in_rule[i-3] == "and":
                        if words_in_rule[i] == "not":
                            args = args & ~ variables[words_in_rule[i-2]][antecedents[words_in_rule[i-2]]]
                        else:
                            args = args & variables[words_in_rule[i-2]][antecedents[words_in_rule[i-2]]]
                    elif words_in_rule[i-3] == "or":
                        if words_in_rule[i] == "not":
                            args = args | ~ variables[words_in_rule[i-2]][antecedents[words_in_rule[i-2]]]
                        else:
                            args = args | variables[words_in_rule[i-2]][antecedents[words_in_rule[i-2]]]
                except KeyError as e:
                    logging.error("Could not recognise antecedent variable: {}. "
                                  "Make sure each variable is only one word.".format(words_in_rule[i]))
            # couldn't get consequent to handle not :(
            consequent = variables[consequents[0][0]][consequents[0][1]]
            ctrl_rules.append(ctrl.Rule(args, consequent))
        except Exception as e:
            logging.error(e)
    return ctrl_rules


def defuzzify(rules, measurements):
    rule_ctrl = ctrl.ControlSystem(rules)
    rulebase = ctrl.ControlSystemSimulation(rule_ctrl)
    for variable, value in measurements.items():
        try:
            rulebase.input[variable] = value
        except Exception as e:
            logging.error(e)
    rulebase.compute()
    return rulebase


def is_data_valid(fuzzy_sets, rules, measurements):
    if len(fuzzy_sets) == 0:
        logging.error("Couldn't find any valid fuzzy sets!")
    if len(rules) == 0:
        logging.error("Couldn't find any valid rules!")
    if len(measurements) == 0:
        logging.error("Couldn't find any valid measurements!")
    if len(fuzzy_sets) <= len(measurements):
        logging.warning(
            "ERROR: Not enough fuzzy sets have been added in the input, or too many measurements have been included. "
            "Make sure a fuzzy set is present for each variable, including consequent variables.")
    else:
        return True


def main():
    # first, read the main file and separate the sections
    input_txt = Read_Data.read_input_txt("rules_and_data")
    # input_txt will return false if any of the 3 mandatory headers are missing
    if not input_txt:
        logging.warning("Exiting...")
        exit(1)

    # then, format the sections according to need
    fuzzy_sets = Read_Data.format_fuzzy_sets(input_txt["fuzzysets"])  # dict of dicts
    rules = Read_Data.format_rules(input_txt["rulebase"])  # dict
    measurements = Read_Data.format_measurements(input_txt["measurements"])  # dict

    if not is_data_valid(fuzzy_sets, rules, measurements):
        logging.warning("The input data is not valid. Please check the message above for more details. Exiting...")
        exit(1)

    # we build a different fuzzy universe for each rule base (in case there are multiple given)!
    for rulebase_pair, rules_values in rules.items():
        consequent = rulebase_pair[1]
        rulebase_name = rulebase_pair[0]
        universe_variables = build_fuzzy_universe(fuzzy_sets, consequent)
        fuzzy_rules = build_fuzzy_rules(rules_values, universe_variables)
        # once the rules and universe variables have been created, defuzzify rule base unknown value
        calculated_rulebase = defuzzify(fuzzy_rules, measurements)
        print("The defuzzified suggested value of " + consequent + " for the " + rulebase_name + " is:")
        print(calculated_rulebase.output[consequent])
        universe_variables[consequent].view(sim=calculated_rulebase)


if __name__ == "__main__":
    main()
