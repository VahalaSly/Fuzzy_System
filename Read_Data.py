import re
import logging


# this function's main role is reading the file and
# dividing the content in the right sections
def read_input_txt(filename):
    rulebase = []
    fuzzysets = []
    measurements = []
    found_rulebase = False
    found_fuzzysets = False
    found_measurements = False
    rulebase_count = 0
    fuzzysets_count = 0
    measurements_count = 0
    try:
        file = open(filename, "r")
    except FileNotFoundError as e:
        logging.error(e)
        logging.error("Check the name of the file and try again.")
        return False
    for line in file:
        line = line.rstrip('\n')
        # these if-statements look for the headers and change the section
        # it's currently been read to True, and the others to False
        # the _count variables make sure all sections are present in the txt file
        if line.lower() == "#rulebase":
            found_rulebase = True
            found_fuzzysets = False
            found_measurements = False
            rulebase_count = 1
            continue
        if line.lower() == "#fuzzysets":
            found_rulebase = False
            found_fuzzysets = True
            found_measurements = False
            fuzzysets_count = 1
            continue
        if line.lower() == "#measurements":
            found_rulebase = False
            found_fuzzysets = False
            found_measurements = True
            measurements_count = 1
            continue
        # while the current section is true, add the next lines to array
        if found_rulebase & (line != ""):
            rulebase.append(line.lower())
        if found_fuzzysets & (line != ""):
            fuzzysets.append(line.lower())
        if found_measurements & (line != ""):
            measurements.append(line.lower())
    if rulebase_count == 0 or fuzzysets_count == 0 or measurements_count == 0:
        logging.warning("The headers '#Rulebase', '#FuzzySets' and '#Measurements' are required before each section. "
                        "Please make sure they are included in the input file and try again.")
        return False
    return {"rulebase": rulebase, "fuzzysets": fuzzysets, "measurements": measurements}


def format_rules(rulebase_input):
    warning = False
    rules = {}
    rulebase_name = ""
    for item in rulebase_input:
        # we use this check to try and figure out which one is the rulebase name
        if ":" not in item:
            rulebase_name = item.rstrip()
        else:
            is_valid = check_rule_validity(item)
            if not is_valid:
                warning = True
            else:
                item = item.replace(": ", ":")
                # find the consequent -> we will use (rulebase, consequent) as key
                # to the dictionary containing the rules
                consequent = re.findall('then (\w+) is', item)[0]
                if (rulebase_name, consequent) in rules:
                    rules[(rulebase_name, consequent)].append(item.split(':')[1])
                else:
                    rules[(rulebase_name, consequent)] = [item.split(':')[1]]
    if warning:
        logging.warning("Please make sure the rules follow this structure:"
                        "\n if <variable-1> is [not] <status_x> [and|or] [<variable-n> is [not] <status-n>] "
                        "then <consequent_variable-i> is <status-j>")
    return rules


def format_fuzzy_sets(fuzzysets_input):
    fuzzysets = {}
    variable_name = ""
    for item in fuzzysets_input:
        try:
            # use variable_names as key and dict of status as values
            if len(item.split(" ")) == 1:
                variable_name = item
            else:
                status = item.replace("(", "").replace(")", "").replace(",", "").split(" ")
                status_name = status[0].rstrip()
                # remove parenthesis from status values and turn into float
                status_values = status[1:]
                status_values = list(map(float, status_values))
                if len(status_values) < 4:
                    logging.warning("The system requires the fuzzy sets to be represented by 4-tuples"
                                    " of the format 'a b α β'. Current tuple: %s".format(status_values))
                    exit(1)
                status_values = [status_values[0] - status_values[2], status_values[0], status_values[1],
                                 status_values[1] + status_values[3]]
                if variable_name in fuzzysets:
                    fuzzysets[variable_name].append((status_name, status_values))
                else:
                    fuzzysets[variable_name] = [(status_name, status_values)]
        except Exception as e:
            logging.error(e)
    return fuzzysets


def format_measurements(measurements_input):
    # expected measurements format: <variable_name> = <variable_value>
    measurements = {}
    for item in measurements_input:
        # add each measurement as item of dictionary
        try:
            variable_name = item.split('=')[0].rstrip()
            variable_value = float(item.split('=')[1])
            measurements[variable_name] = variable_value
        except Exception as e:
            logging.error(e)
    return measurements


def check_rule_validity(rule):
    validity = True
    consequent = re.findall('then (\w+) is', rule)
    negative_consequent = re.findall('then (\w+) is not', rule)
    if len(consequent) == 0:
        validity = False
        logging.warning("Couldn't find a consequent for %s. "
                        "Skipping rule..." % rule)
    elif len(negative_consequent) == 1:
        validity = False
        logging.warning("Invalid: %s"
                        "\n Negative consequents are currently not supported."
                        "\n Skipping rule..." % rule)
    return validity
