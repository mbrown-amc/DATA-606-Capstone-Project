import os
import pandas as pd

def get_data():
    """
    Loads and cleans the data, and combines it.
    """
    import os
    import pandas as pd
    
    #!git clone https://github.com/mbrown-amc/DATA-606-Capstone-Project #Cloning the repository
    
    #Loading and cleaning the fantasy data
    
    df = []
    for i in range(1970, 2020):
        df.append("/content/DATA-606-Capstone-Project/Data/Fantasy_Data/" + str(i) + ".csv")
    
    fdata = []

    for f in df:
         fdata.append(pd.read_csv(f))
    
    i = 1970
    for f in fdata:
        f.insert(1, "Year", i)
        i += 1
        
    fullfdata = pd.concat(fdata, ignore_index=True)
    fullfdata.drop("Unnamed: 0", axis = 'columns', inplace = True)
    fullfdata2 = fullfdata[fullfdata.Pos != "0"]
    fullfdata2 = fullfdata2.rename(columns = {"Tm": "Team", "Att":"Passing_Att", "Yds":"Passing_Yards", "Att.1":"Rushing_Att", "Yds.1":"Rushing_Yards", "Yds.2":"Receiving_Yards", "Y/R":"Yards/Rec"})
    fullfdata2.drop("PassingYds", axis = 'columns', inplace = True)
    fullfdata2.drop("PassingAtt", axis = 'columns', inplace = True)
    fullfdata2.drop("RushingYds", axis = 'columns', inplace = True)
    fullfdata2.drop("RushingAtt", axis = 'columns', inplace = True)
    fullfdata2.drop("ReceivingYds", axis = 'columns', inplace = True)
    fullfdata2.drop("Tgt", axis = 'columns', inplace = True)
    fullfdata2 = fullfdata2[["Year", "Player", "Pos", "Age", "Team", "G", "GS", "Passing_Att", "Cmp", "Passing_Yards", "PassingTD", "Int", "Rushing_Att", "Rushing_Yards", "RushingTD", "Rec", "Receiving_Yards", "Yards/Rec", "ReceivingTD", "Fumbles", "FumblesLost", "FantasyPoints"]]
    
    #Loading and cleaning the season by season wins data
    
    sdf = []

    for i in range(1970, 2020):
        sdf.append("/content/DATA-606-Capstone-Project/Data/Team_Standings/" + str(i) + "AFC.xlsx")
        sdf.append("/content/DATA-606-Capstone-Project/Data/Team_Standings/" + str(i) + "NFC.xlsx")
        
    sfdataAFC = []
    sfdataNFC = []

    for f in sdf:
        if f[-8] == "A":
            sfdataAFC.append(pd.read_excel(f, 0))
        elif f[-8] == "N":
            sfdataNFC.append(pd.read_excel(f, 0))
            
    i = 1970
    for f in sfdataAFC:
        f.insert(1, "Year", i)
        i += 1

    i = 1970
    for f in sfdataNFC:
        f.insert(1, "Year", i)
         i += 1
            
    fullsfdataAFC = pd.concat(sfdataAFC, ignore_index=True)
    fullsfdataNFC = pd.concat(sfdataNFC, ignore_index=True)
    fullsfdata = fullsfdataAFC.append(fullsfdataNFC, ignore_index=True)
    fullsfdata = fullsfdata.sort_values(by = 'Year', ignore_index=True)
    fullsfdataWins = fullsfdata.drop(["PF", "PA", "PD", "MoV", "SoS", "SRS", "OSRS", "DSRS"], axis = 1)
    fullsfdataWins.Tm = fullsfdataWins.Tm.str.strip("*+")
    
    #Removing the players who played for multiple teams in a year for simplicity
    
    OneTeamOnly = fullfdata2.loc[(fullfdata2.Team != "2TM")]
    OneTeamOnly = OneTeamOnly.loc[(OneTeamOnly.Team !="3TM")]
    OneTeamOnly = OneTeamOnly.loc[(OneTeamOnly.Team != '4TM')]
   
    TestPoints = pd.DataFrame(OneTeamOnly.groupby(["Team", "Year", "Pos"])["FantasyPoints"].sum())
    
    TTestPoints = TestPoints.reset_index()
    
    TTestPoints.loc[(TTestPoints.Pos == "QB"), "QB"] = TTestPoints["FantasyPoints"]
    TTestPoints.loc[(TTestPoints.Pos == "RB"), "RB"] = TTestPoints["FantasyPoints"]
    TTestPoints.loc[(TTestPoints.Pos == "TE"), "TE"] = TTestPoints["FantasyPoints"]
    TTestPoints.loc[(TTestPoints.Pos == "WR"), "WR"] = TTestPoints["FantasyPoints"]
    TTestPoints.fillna(0)
    
    PosTestPoints = pd.DataFrame(TTestPoints.groupby(["Team", "Year"])["QB", "RB", "TE", "WR"].sum())
    PosTestPoints["FantasyPoints"] = PosTestPoints["QB"] + PosTestPoints["RB"] + PosTestPoints["TE"] + PosTestPoints["WR"]
    
    TPosTestPoints = PosTestPoints.reset_index()
    
    #Combining all of the data
    
    ForCombine = TPosTestPoints
    
    ForCombine.loc[(ForCombine.Year < 1984) & (ForCombine.Team == "BAL"), "Team"] = 'Baltimore Colts'
    ForCombine.loc[(ForCombine.Year >= 1984) & (ForCombine.Team == "BAL"), "Team"] = 'Baltimore Ravens'
    ForCombine.loc[(ForCombine.Team == "RAM"), "Team"] = 'Los Angeles Rams'
    ForCombine.loc[(ForCombine.Team == "LAR"), "Team"] = 'Los Angeles Rams'
    ForCombine.loc[(ForCombine.Team == "SFO"), "Team"] = 'San Francisco 49ers'
    ForCombine.loc[(ForCombine.Team == "CHI"), "Team"] = 'Chicago Bears'
    ForCombine.loc[(ForCombine.Team == "GNB"), "Team"] = 'Green Bay Packers'
    ForCombine.loc[(ForCombine.Team == "DET"), "Team"] = 'Detroit Lions'
    ForCombine.loc[(ForCombine.Team == "MIN"), "Team"] = 'Minnesota Vikings'
    ForCombine.loc[(ForCombine.Team == "PHI"), "Team"] = 'Philadelphia Eagles'
    ForCombine.loc[(ForCombine.Team == "WAS"), "Team"] = 'Washington Commanders'
    ForCombine.loc[(ForCombine.Year < 1988) & (ForCombine.Team == "STL"), "Team"] = 'St. Louis Cardinals'
    ForCombine.loc[(ForCombine.Year >= 1988) & (ForCombine.Team == "STL"), "Team"] = 'St. Louis Rams'
    ForCombine.loc[(ForCombine.Team == "NYG"), "Team"] = 'New York Giants'
    ForCombine.loc[(ForCombine.Team == "DAL"), "Team"] = 'Dallas Cowboys'
    ForCombine.loc[(ForCombine.Team == "NOR"), "Team"] = 'New Orleans Saints'
    ForCombine.loc[(ForCombine.Team == "ATL"), "Team"] = 'Atlanta Falcons'
    ForCombine.loc[(ForCombine.Team == "CIN"), "Team"] = 'Cincinnati Bengals'
    ForCombine.loc[(ForCombine.Team == "KAN"), "Team"] = 'Kansas City Chiefs'
    ForCombine.loc[(ForCombine.Team == "OAK"), "Team"] = 'Oakland Raiders'
    ForCombine.loc[(ForCombine.Year < 1997) & (ForCombine.Team == "HOU"), "Team"] = 'Houston Oilers'
    ForCombine.loc[(ForCombine.Year >= 1997) & (ForCombine.Team == "HOU"), "Team"] = 'Houston Texans'
    ForCombine.loc[(ForCombine.Team == "PIT"), "Team"] = 'Pittsburgh Steelers'
    ForCombine.loc[(ForCombine.Team == "CLE"), "Team"] = 'Cleveland Browns'
    ForCombine.loc[(ForCombine.Team == "BOS"), "Team"] = 'Boston Patriots'
    ForCombine.loc[(ForCombine.Team == "BUF"), "Team"] = 'Buffalo Bills'
    ForCombine.loc[(ForCombine.Team == "NYJ"), "Team"] = 'New York Jets'
    ForCombine.loc[(ForCombine.Team == "MIA"), "Team"] = 'Miami Dolphins'
    ForCombine.loc[(ForCombine.Team == "SDG"), "Team"] = 'San Diego Chargers'
    ForCombine.loc[(ForCombine.Team == "DEN"), "Team"] = 'Denver Broncos'
    ForCombine.loc[(ForCombine.Team == "NWE"), "Team"] = 'New England Patriots'
    ForCombine.loc[(ForCombine.Team == "TAM"), "Team"] = 'Tampa Bay Buccaneers'
    ForCombine.loc[(ForCombine.Team == "SEA"), "Team"] = 'Seattle Seahawks'
    ForCombine.loc[(ForCombine.Team == "RAI"), "Team"] = 'Los Angeles Raiders'
    ForCombine.loc[(ForCombine.Team == "IND"), "Team"] = 'Indianapolis Colts'
    ForCombine.loc[(ForCombine.Team == "PHO"), "Team"] = 'Phoenix Cardinals'
    ForCombine.loc[(ForCombine.Team == "ARI"), "Team"] = 'Arizona Cardinals'
    ForCombine.loc[(ForCombine.Team == "CAR"), "Team"] = 'Carolina Panthers'
    ForCombine.loc[(ForCombine.Team == "JAX"), "Team"] = 'Jacksonville Jaguars'
    ForCombine.loc[(ForCombine.Year < 1999) & (ForCombine.Team == "TEN"), "Team"] = 'Tennessee Oilers'
    ForCombine.loc[(ForCombine.Year >= 1999) & (ForCombine.Team == "TEN"), "Team"] = 'Tennessee Titans'
    ForCombine.loc[(ForCombine.Team == "LAC"), "Team"] = 'Los Angeles Chargers'
    fullsfdataWins.loc[(fullsfdataWins.Tm == "Washington Redskins"), "Tm"] = 'Washington Commanders'
    fullsfdataWins = fullsfdataWins.rename(columns = {"Tm": "Team"})
    fullsfdataWins['T'] = fullsfdataWins['T'].fillna(0)
    fullsfdataWins["G"] = fullsfdataWins["W"] + fullsfdataWins["L"] + fullsfdataWins ["T"]
    
    alldata = fullsfdataWins.merge(ForCombine, how = 'outer', on = ["Team", "Year"])
    
    alldata["FantasyPoints/G"] = alldata["FantasyPoints"]/alldata["G"]
    alldata["QB/G"] = alldata["QB"]/alldata["G"]
    alldata["RB/G"] = alldata["RB"]/alldata["G"]
    alldata["TE/G"] = alldata["TE"]/alldata["G"]
    alldata["WR/G"] = alldata["WR"]/alldata["G"]
    
    return alldata