#!/usr/bin/python3

import re

recordpattern = re.compile("([0-9]+) - ([0-9]+)( - ([0-9]+))?")
year = 2020
raw_in = f"team_grades_{year}.txt"
csv_out = f"team_grades_{year}.csv"


with open(raw_in, "r") as raw:
    with open(csv_out, "w") as csv:
        content = raw.readlines()
        teams = ["" for t in range(32)]
        t = -1
        for line in content:
            if line.find("-") > -1 or len(line) > 6:
                t = (t + 1) % 32
                if len(line) > 12:
                    teams[t] += line.strip() + ","
                else:
                    match = recordpattern.search(line).groups()
                    wins = match[0]
                    losses = match[1]
                    ties = 0
                    if match[3]:
                        ties = match[3]
                    teams[t] += f"{wins},{losses},{ties},"
                
            else:
                teams[t] += line.strip() + ","

        csv.write("TEAM,W,L,T,PF,PA,OVER,OFF,PASS,PBLK,RECV,RUN,RBLK,DEF,RDEF,TACK,PRSH,COV,SPEC")
        for team in teams:
            csv.write("\n" + team[:-1])