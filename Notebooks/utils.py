import os
import pandas as pd

def get_data(QB = 1, RB = 2, TE = 2, WR = 3):
    """
    Loads and cleans the data, and combines it.
    
    QB: The number of QB per team to include in the data. Default = 1
    RB: The number of RB per team to include in the data. Default = 2
    TE: The number of TE per team to include in the data. Default = 2
    WR: The number of WR per team to include in the data. Default = 3
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
    
    #Offsetting the data so that the stats are from the year prior
    testmerge1 = OneTeamOnly
    testmerge1["Pred_Year"] = testmerge1["Year"] + 1
    
    testmerge2 = OneTeamOnly
    testmerge2 = testmerge2[["Year", "Player", "Pos", "Team"]]
    testmerge2 = testmerge2.rename(columns = {'Year': "Pred_Year"})
    
    testmerge3 = testmerge2.merge(testmerge1, how = 'outer', on = ["Pred_Year", "Player"])
    testmerge3 = testmerge3.loc[(testmerge3.Pred_Year != 1970)]
    testmerge3 = testmerge3.loc[(testmerge3.Pred_Year != 2020)]
    
    #For the moment, removing entries where the pred team is NaN because that means the player either did not play in the year we are predicting, or did nothing the whole year. This is sort of cheating, since when predicting for the future, we won't know whether a player will play that year or get injured or suspended or something. However, we can possibly argue that the intended use of our model would recalculate every time there was an injury or a suspension.
    
    testmerge4 = testmerge3
    testmerge4 = testmerge4.dropna(subset = ["Pos_x"])
    
    #Also removing rookies or players who got injured the year before we are predicting. We might revisit this later, but for now, the idea is kind of trying to only use stats from the prior season to predict wins for that season, and since these players have no prior season stats, they cannot be used for that aim.

    testmerge5 = testmerge4
    testmerge5 = testmerge5.dropna(subset = ["Year"])
    testmerge5 = testmerge5.rename(columns = {'Team_x': "Team", 'Team_y':"Last_Team", 'Pos_x':'Pos', 'Pos_y':'Last_Pos', 'Year':'Last_Year', 'Pred_Year': 'Year'})
    
    #Adding in the ability to set number of players per position included
    #First step is to sort the original data
    
    testsort = testmerge5
    testsort2 = testsort.sort_values(by = ["Year", "Team", "Pos", "FantasyPoints"], ascending = [True, True, True, False])
    testsort2 = testsort2.reset_index()
    
    #Getting list of unique teams to use for the next step
    uniqueteams = testsort2["Team"].unique()
    
    #Breaking the data into mini lists to then combine back into the main frame
    testfunct = []
    for i in range(1971, 2020):
        for j in range(len(uniqueteams)):
            if testsort2.loc[(testsort2.Year == i) & (testsort2.Team == uniqueteams[j])].empty:
        else:
            newtest = testsort2.loc[(testsort2.Year == i) & (testsort2.Team == uniqueteams[j]) & (testsort2.Pos == "QB")]
            testfunct.append(newtest[0:QB])
            newtest = testsort2.loc[(testsort2.Year == i) & (testsort2.Team == uniqueteams[j]) & (testsort2.Pos == "RB")]
            testfunct.append(newtest[0:RB])
            newtest = testsort2.loc[(testsort2.Year == i) & (testsort2.Team == uniqueteams[j]) & (testsort2.Pos == "TE")]
            testfunct.append(newtest[0:TE])
            newtest = testsort2.loc[(testsort2.Year == i) & (testsort2.Team == uniqueteams[j]) & (testsort2.Pos == "WR")]
            testfunct.append(newtest[0:WR])
            
    #Recombining the data
    testmergenumpos = pd.concat(testfunct).reset_index(drop=True)
    
    TestPoints = pd.DataFrame(testmergenumpos.groupby(["Team", "Year", "Pos"])["FantasyPoints"].sum())
    
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