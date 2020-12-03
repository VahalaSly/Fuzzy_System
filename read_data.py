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
        if line == "#Rulebase":
            found_rulebase = True
            found_fuzzysets = False
            found_measurements = False
            rulebase_count = 1
            continue
        if line == "#FuzzySets":
            found_rulebase = False
            found_fuzzysets = True
            found_measurements = False
            fuzzysets_count = 1
            continue
        if line == "#Measurements":
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
    # expected rules format:
    # <RulebaseName>
    # Rule<n>: if <variable_name> is <variable_status> [and|or] [<variable_name_i> is <variable_status_i>]
    # then <variable_name_j> is <variable_status_j>
    warning = False
    rules = {}
    for item in rulebase_input:
        # we use this check to try and figure out which one is the rulebase name, and skip it
        if ":" not in item:
            continue
        else:
            # find the consequent -> we will use it as key to the dictionary containing the rules
            consequent = re.findall('then (\w+) is', item)
            if len(consequent) == 0:
                warning = True
                logging.warning("Couldn't find a consequent for %s. "
                                "Skipping rule..." % item)
            else:
                item = item.replace(": ", ":")
                consequent = consequent[0]
                if consequent in rules:
                    rules[consequent].append(item.split(':')[1])
                else:
                    rules[consequent] = [item.split(':')[1]]
    if warning:
        logging.warning("Please make sure the rules follow this structure:"
                        "\n if <variable-1> is <status_x> [and|or] [<variable-n> is <status-n>] "
                        "then <consequent_variable-i> is <status-j>")
    return rules


# returns the sets with format: {variable_name:{status_name:[status_values]}, {...}}}
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
                    logging.error("The system requires the fuzzy sets to be represented by 4-tuples"
                                  " of the format 'a b α β'. Current tuple: {}".format(status_values))
                    logging.warning("Exiting...")
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
