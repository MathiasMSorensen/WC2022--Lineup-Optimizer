def Pulp_optimization(Teams, N, Data, Value, PlayerList,xPointsTotal, Positions, ExcludePlayers, IncludePlayers, ExcludeTeam, timeout,Budget, Names, xPoints):
    
    import numpy as np
    import pulp

    # list(np.where(np.isin(list(Data['Name']), PlayerList),0,np.array(Value)*0))
    Transfer = np.zeros(N) #Value*0,01 if on team    
    TotalPoints = list(np.array(xPointsTotal)  - np.array(Transfer))
    Cost = list(np.array(Value) + np.array(Transfer)) # Value+transfer
    Budget = int(50000000)
    # Set up model:
    model = pulp.LpProblem("Constrained_maximisation", pulp.LpMaximize)
    
    players = [
        pulp.LpVariable("x{}".format(i), lowBound=0, upBound=1, cat='Integer') for i in range(N)
    ]
    captain = [
        pulp.LpVariable("y{}".format(i), lowBound=0, upBound=1, cat='Integer') for i in range(N)
    ]

    # Objective function:
    model += sum((captain[i] + players[i]) * TotalPoints[i] for i in range(N))
    
    # Team constraint
    model += sum(players) == 11
    
    # Cost constraint
    model += sum(players[i] * Cost[i] for i in range(N)) <= Budget
    # Position constraints
    model += sum(players[i] for i in range(N) if Positions[i] == 'Mål') == 1
    model += sum(players[i] for i in range(N) if Positions[i] == 'Forsvar') >= 3
    model += sum(players[i] for i in range(N) if Positions[i] == 'Forsvar') <= 5
    model += sum(players[i] for i in range(N) if Positions[i] == 'Midtbane') >= 3
    model += sum(players[i] for i in range(N) if Positions[i] == 'Midtbane') <= 5
    model += sum(players[i] for i in range(N) if Positions[i] == 'Angreb') >= 1
    model += sum(players[i] for i in range(N) if Positions[i] == 'Angreb') <= 3  
    
    
    # Club constraint
    for team in np.unique(Teams):
        model += sum(players[i] for i in range(N) if Teams[i] == team) <= 4
    
    # Captain constraint
    model += sum(captain) == 1
    for i in range(N):  #
        model += (players[i] - captain[i]) >= 0
    
    # Include/Exclude players
    for i in range(N):
        if Names[i] in IncludePlayers:
            model += players[i] == 1
            
        
    for i in range(N):
        if Names[i] in ExcludePlayers:
            model += players[i] == 0
        
    # Exclude teams
    for i in range(N):
        if Teams[i] in ExcludeTeam:
            model += players[i] == 0 
    
    # Solve problem:
    model.solve()
    
    if model.solve()==1:

        # Print results:
        ExpPoints = 0
        TotalCost = 0
        TransferCost = 0
        CaptainPTS = 0
        n = 0
        Squad = []
        Squad_Position = []
        Squad_Team = []
        Squad_xPoints = []
        Squad_Captain = []
        for i in range(N):
            if players[i].value()!=0:
                ExpPoints += int(xPoints[i] - Transfer[i])
                TotalCost += int(Cost[i])
                TransferCost += int(Transfer[i])
                print('{},Position = {},Team = {}, xPoints = {}, Cost = {}'.format(Names[i], Positions[i], Teams[i], int(xPoints[i]), int(Cost[i])))
                Squad.append(Names[i])
                Squad_Position.append(Positions[i])
                Squad_Team.append(Teams[i])
                Squad_xPoints.append(int(xPoints[i]))
                if xPoints[i]>CaptainPTS:
                    Captain = Names[i]
                    CaptainPTS = xPoints[i]
                n += 1
                if n==11:
                    ExpPoints += int(CaptainPTS)
                    
        nShare = round(TotalCost/Budget*100,1)
        print('\nCaptain: {}'.format(Captain))
        print('\nExpected points in this round = {}'.format(ExpPoints))
        print('\nTransfer cost = {} \nTotal cost = {} \nBudget = {} \nShare = {}% \nBank = {}'.format(TransferCost,TotalCost, Budget, round(TotalCost/Budget*100,1),  Budget-TotalCost))
        
        sell_list = []
        sell_list_team = []
        sell_list_position=[]
        sell_list_xPoints=[]
        print('\nSell:')
        Old_players = PlayerList
        for i in range(N):
            if Names[i] not in Squad:
                if Names[i] in Old_players:
                    sell_list.append(Names[i])
                    sell_list_team.append(Teams[i])
                    sell_list_position.append(Positions[i])
                    sell_list_xPoints.append(round(xPoints[i]))

        ## Sort
        GK_index = [i for i, x in enumerate(sell_list_position) if x == "Mål"]
        DEF_index = [i for i, x in enumerate(sell_list_position) if x == "Forsvar"]
        MID_index = [i for i, x in enumerate(sell_list_position) if x == "Midtbane"]
        STR_index = [i for i, x in enumerate(sell_list_position) if x == "Angreb"]

        sell_list = [sell_list[i] for i in GK_index]+[sell_list[i] for i in DEF_index]+[sell_list[i] for i in MID_index]+[sell_list[i] for i in STR_index]
        sell_list_team = [sell_list_team[i] for i in GK_index]+[sell_list_team[i] for i in DEF_index]+[sell_list_team[i] for i in MID_index]+[sell_list_team[i] for i in STR_index]
        sell_list_position = [sell_list_position[i] for i in GK_index]+[sell_list_position[i] for i in DEF_index]+[sell_list_position[i] for i in MID_index]+[sell_list_position[i] for i in STR_index]
        sell_list_xPoints = [sell_list_xPoints[i] for i in GK_index]+[sell_list_xPoints[i] for i in DEF_index]+[sell_list_xPoints[i] for i in MID_index]+[sell_list_xPoints[i] for i in STR_index]

        buy_list = []
        buy_list_team = []
        buy_list_position=[]
        buy_list_xPoints=[]
        print('\nBuy:')
        Old_players = PlayerList
        for i in range(N):
            if Names[i] in Squad:
                if Names[i] not in Old_players:
                    buy_list.append(Names[i])
                    buy_list_team.append(Teams[i])
                    buy_list_position.append(Positions[i])
                    buy_list_xPoints.append(round(xPoints[i]))
           
        ## Sort
        GK_index = [i for i, x in enumerate(buy_list_position) if x == "Mål"]
        DEF_index = [i for i, x in enumerate(buy_list_position) if x == "Forsvar"]
        MID_index = [i for i, x in enumerate(buy_list_position) if x == "Midtbane"]
        STR_index = [i for i, x in enumerate(buy_list_position) if x == "Angreb"]

        buy_list = [buy_list[i] for i in GK_index]+[buy_list[i] for i in DEF_index]+[buy_list[i] for i in MID_index]+[buy_list[i] for i in STR_index]
        buy_list_team = [buy_list_team[i] for i in GK_index]+[buy_list_team[i] for i in DEF_index]+[buy_list_team[i] for i in MID_index]+[buy_list_team[i] for i in STR_index]
        buy_list_position = [buy_list_position[i] for i in GK_index]+[buy_list_position[i] for i in DEF_index]+[buy_list_position[i] for i in MID_index]+[buy_list_position[i] for i in STR_index]
        buy_list_xPoints = [buy_list_xPoints[i] for i in GK_index]+[buy_list_xPoints[i] for i in DEF_index]+[buy_list_xPoints[i] for i in MID_index]+[buy_list_xPoints[i] for i in STR_index]

        ## Sort
        GK_index = [i for i, x in enumerate(Squad_Position) if x == "Mål"]
        DEF_index = [i for i, x in enumerate(Squad_Position) if x == "Forsvar"]
        MID_index = [i for i, x in enumerate(Squad_Position) if x == "Midtbane"]
        STR_index = [i for i, x in enumerate(Squad_Position) if x == "Angreb"]

        
        Squad = [Squad[i] for i in GK_index]+[Squad[i] for i in DEF_index]+[Squad[i] for i in MID_index]+[Squad[i] for i in STR_index]
        Squad_Position = [Squad_Position[i] for i in GK_index]+[Squad_Position[i] for i in DEF_index]+[Squad_Position[i] for i in MID_index]+[Squad_Position[i] for i in STR_index]
        Squad_Team = [Squad_Team[i] for i in GK_index]+[Squad_Team[i] for i in DEF_index]+[Squad_Team[i] for i in MID_index]+[Squad_Team[i] for i in STR_index]
        Squad_xPoints = [Squad_xPoints[i] for i in GK_index]+[Squad_xPoints[i] for i in DEF_index]+[Squad_xPoints[i] for i in MID_index]+[Squad_xPoints[i] for i in STR_index]
        Squad_Captain = [''] * 11
        Captain_index = [i for i, x in enumerate(Squad) if x == Captain]
        print(Captain_index)
        Squad_Captain[int(Captain_index[0])] = 'Captain'
    
        Budget = Budget-TotalCost 
        
    else:
        print("""System crashed""")
        
        Squad = 0 
        Squad_Team = 0 
        Squad_xPoints = 0 
        Squad_Position = 0 
        Squad_Captain = 0 
        Budget = 0 
        TransferCost = 0 
        nShare = 0 
        Squad_xPoints = [0,2] 
        sell_list = 0
        buy_list = 0
        buy_list_position = 0
        buy_list_team, buy_list_xPoints = 0
        sell_list_team, sell_list_position = 0
        sell_list_xPoints = 0
        
    return  Squad, Squad_Team, Squad_xPoints, Squad_Position, Squad_Captain, Budget, TransferCost, nShare, sum(Squad_xPoints), buy_list, sell_list,  buy_list_position, buy_list_team, buy_list_xPoints, sell_list_team, sell_list_position, sell_list_xPoints
 
