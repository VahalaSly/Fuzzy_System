### Fuzzy Rule-Based System 
Created for university project. Makes use of the skfuzzy library.

Takes a txt file as input with the following format:
```
  #Rulebase
  <RuleBaseName>
  Rule 1:	if <variable-1> is <status_x> [and|or] [<variable-n> is <status-n>] then <consequent_variable-i> is <status-j>
  Rule 2:	if <variable-2> is <status-y> [and|or] [<variable-n> is <status-n>] then <consequent_variable-i> is <status-j>
  ...
  
  #FuzzySets
  <variable-1>
  <status-x> <4-tuple>
  ...
  <status-xn> <4-tuple>
  
  <variable-2>
  <status-y> <4-tuple>
  ...
  <status-yn> <4-tuple>
  
  ...
  
  <consequent_variable-i>
  <status-j> <4-tuple>
  ...
  <status-jn> <4-tuple>
  
  #Measurements
  <variable-1> = <RealValue-1>
  ...
  <variable-n> = <RealValue-n>
``` 

An example txt file is present in the main directory.
  

