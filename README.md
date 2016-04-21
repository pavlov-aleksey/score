This coding project is a hypothetical scoring engine for sales leads. The goal
of this exercise is understand what you consider production-quality code with a
small set of requirements. Please provide some level of unit testing.

The application will be run from the command-line and take as a command-line
argument the path to a csv file. The csv file is expected to have the following
field layout:
- contact id - integer
- event - string of values {web, email, social, webinar}
- score - a rational number with up to 2 digits after the decimal


Example:
- 1, web, 34.33
- 1, email, 3.4
- 1, social, 4
- 2, webinar, 55.4
- 2, social, 15

There will be many events per contact but only one event will be represented
per row in the file.

In order to score a contact use the following algorithm:

1) Event scores will first be weighted by type as follows:
- web = score * 1.0
- email = score * 1.2
- social = score * 1.5
- webinar = score * 2.0

2) All scores should then be summed by contact id.

3) The summed scores should then be normalized on a scale of 0 to 100.
To normalize 
the score you take the highest and lowest summed values found
across all contacts making those 100 and 0 respectively and
interoplate the scores in between. Round the score to the closest
integer.

4) Finally, the contacts should be labelled by quartile based on the
normalized score:
- 100-75 = platinum
- 74-50 = gold
- 49-25 = silver
- &lt; 25 = bronze

The output of the program should be written to console with the
following format:

contact id, quartile label, normalized score

Example output:
- 1, silver, 44
- 2, gold, 99
