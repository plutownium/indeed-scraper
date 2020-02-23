import re

# They work.

salaries = ["$40,000", "$65,000 - $95,000", "$25.00 an hour"]

set_salary = re.compile(r"[$]?[0-9]+[,]\d\d\d$")
range_salary = re.compile(r"[$]?[0-9]+[,]\d\d\d\s[-]\s[$]?[0-9]+[,]\d\d\d$")
hourly = re.compile(r"[$]?[0-9]+[.]\d\d\s[a][n]\s[h][o][u][r]$")

print(set_salary.match(salaries[0]))
print(range_salary.match(salaries[1]))
print(hourly.match(salaries[2]))