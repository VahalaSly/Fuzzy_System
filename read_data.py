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
    file = open(filename, "r")
    for line in file:
        line = line.rstrip('\n')
        # these if-statements look for the headers and change the section
        # it's currently been read to True, and the others to False
        # the _count variables make sure all sections are present in the txt file
        if line == "[Rulebase]":
            found_rulebase = True
            found_fuzzysets = False
            found_measurements = False
            rulebase_count = 1
            continue
        if line == "[FuzzySets]":
            found_rulebase = False
            found_fuzzysets = True
            found_measurements = False
            fuzzysets_count = 1
            continue
        if line == "[Measurements]":
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
        return False
    return {"rulebase": rulebase, "fuzzysets": fuzzysets, "measurements": measurements}


def format_rules(rulebase_input):
    # expected rules format:
    # <RulebaseName>
    # Rule<n>: if <variable_name> is <variable_status> [and|or] [<variable_name_i> is <variable_status_i>]
    # then <variable_name_j> is <variable_status_j>

    rulebase_name = ""
    rules = {}
    for item in rulebase_input:
        # we use this check to try and figure out which one is the rulebase name
        if "then" not in item or "if" not in item:
            rulebase_name = item.rstrip()
            rules[rulebase_name] = []
        if ":" in item:
            item = item.replace(": ", ":")
            rules[rulebase_name].append(item.split(':')[1])
    return rules


# returns the sets with format: {variable_name:{status_name:[status_values]}, {...}}}
def format_fuzzy_sets(fuzzysets_input):
    fuzzysets = {}
    variable_name = ""
    for item in fuzzysets_input:
        try:
            # use variable_names as key and dict of status as values
            if "(" not in item:
                variable_name = item
                statuses = {} # clean up statuses for new variable
            else:
                status_name = item.split("(")[0].rstrip()
                # remove parenthesis from status values and turn into float
                status_values = item.split("(")[1]
                status_values = status_values.replace('(','').replace(')','')
                status_values = list(map(float, status_values.split(',')))
                if variable_name in fuzzysets:
                    fuzzysets[variable_name].append((status_name, status_values))
                else:
                    fuzzysets[variable_name] = [(status_name, status_values)]
        except Exception as e:
            print(e)
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
            print(e)
    return measurements