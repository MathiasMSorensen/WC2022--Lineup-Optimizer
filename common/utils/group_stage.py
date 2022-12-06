import joblib 
import pandas as pd
from common.utils.holdet_utils import get_holdet_data, get_play_off_opps

def get_groups():

    odds = []
    team = []
    for i in range(294,294+32):
        str_temp = soup.find_all('li')[i].text
        if '+' in str_temp:
            team.append(str_temp.split('+')[0].strip())
            odds.append(float(str_temp.split('+')[1]))
        else:
            team.append(str_temp.split('-')[0].strip())
            odds.append(-float(str_temp.split('-')[1]))
            
    df_grop_stage = pd.concat([pd.Series(team),pd.Series(odds)],axis=1)
    df_grop_stage.columns = ["Team","odds_to_win"]

    import numpy as np
    df_grop_stage["odds_to_win"] = np.where(df_grop_stage["odds_to_win"]>0,(df_grop_stage["odds_to_win"] + 100)/100,(-100/df_grop_stage["odds_to_win"])+1)

    group_stage =['A','B','C','D','E','F','G','H']
    loop_list = list(range(0,33,4))
    df_grop_stage["group"] = "A"
    for i in range(8):
        df_grop_stage.loc[loop_list[i]:loop_list[i+1],"group"] = group_stage[i]
        
    df_grop_stage['pb_percent'] = 1/df_grop_stage["odds_to_win"]
    df_grop_stage['temp_column'] = 1/df_grop_stage.groupby('group')['pb_percent'].transform('sum')
    df_grop_stage["prob_to_win"]=df_grop_stage["temp_column"]/df_grop_stage["odds_to_win"]
    df_grop_stage.drop(columns = {"pb_percent","temp_column"}, inplace = True)

    df_grop_stage[["Team","group"]].to_csv("common/utils/df_groups.csv")
    
        
import scipy.optimize as opt
import math
import pandas as pd 

def func(zGuess, _lambda):
    val = _lambda
    x = zGuess
    eq_1 = math.exp(-x)+math.exp(-x)*x+(math.exp(-x)*x**2)/2-val 
    return eq_1[0]

def get_group_stage(df_get_group_stage_OU, df_group_stage, ROUND, eng2dan):
    zGuess = 2.4
    df_get_group_stage_OU['lambda']= df_get_group_stage_OU['prob_under'].apply(lambda x: opt.fsolve(func,zGuess,args=(x))[0])
    df_get_group_stage_OU['xG'] = df_get_group_stage_OU['lambda']
    
    df_group_stage = df_group_stage.merge(df_get_group_stage_OU[['home_team','away_team','xG']], on = ['home_team','away_team'])
    df_group_stage["xGH"] = df_group_stage["xG"]*df_group_stage["prob1"]/(df_group_stage["prob1"]+df_group_stage["prob2"])
    df_group_stage["xGA"] = df_group_stage["xG"]*df_group_stage["prob2"]/(df_group_stage["prob1"]+df_group_stage["prob2"])
    
    # df_schedule = pd.read_csv("common/ressources/schedule.csv")
    # df_schedule.rename(columns = {"Home Team":"home_team", "Away Team":"away_team", "Round Number":"round"}, inplace = True)
    # rounds = range(ROUND,4)
    # df_schedule = df_schedule[df_schedule["round"].isin([str(_) for _ in rounds])]
    # df_schedule.loc[(df_schedule["home_team"]=="Korea Republic"),"home_team"]="South_Korea"
    # df_schedule.loc[(df_schedule["away_team"]=="Korea Republic"),"away_team"]="South_Korea"
    # df_group_stage.loc[(df_group_stage["home_team"]=="South Korea"),"home_team"]="South_Korea"
    # df_group_stage.loc[(df_group_stage["away_team"]=="South Korea"),"away_team"]="South_Korea"

    # df_group_stage = df_group_stage.merge(df_schedule[["home_team","away_team","round"]], on = ['home_team','away_team'])
    # df_group_stage.sort_values("round", inplace=True)
    # df_group_stage.reset_index(drop=True, inplace = True)
    df_group_stage["home_team"] = df_group_stage["home_team"].apply(lambda x: eng2dan[x])
    df_group_stage["away_team"] = df_group_stage["away_team"].apply(lambda x: eng2dan[x])
    
    return df_group_stage


def playoffs(df_winner,_df_group_stage, eng2dan):
    df_winner["name"] = df_winner["name"].replace("South Korea","South_Korea")
    df_winner["country"] = df_winner["name"].apply(lambda x: eng2dan[x])

    temp_list = []
    for team in pd.concat([_df_group_stage["home_team"],_df_group_stage["away_team"]], axis=0).unique():
        xG, pwin, xGa = 0, 0, 0
        if len(_df_group_stage.loc[_df_group_stage["home_team"]==team,"xGH"])>0:
            xG += _df_group_stage.loc[_df_group_stage["home_team"]==team,"xGH"].values[0]
            xGa += _df_group_stage.loc[_df_group_stage["home_team"]==team,"xGA"].values[0]
            pwin += (_df_group_stage.loc[_df_group_stage["home_team"]==team,"prob1"]/(_df_group_stage.loc[_df_group_stage["home_team"]==team,["prob1","prob2"]].sum(axis=1))).sum()
        if len(_df_group_stage.loc[_df_group_stage["away_team"]==team,"xGA"])>0:
            xG += _df_group_stage.loc[_df_group_stage["away_team"]==team,"xGA"].values[0]
            xGa += _df_group_stage.loc[_df_group_stage["away_team"]==team,"xGH"].values[0]
            pwin += (_df_group_stage.loc[_df_group_stage["away_team"]==team,"prob2"]/(_df_group_stage.loc[_df_group_stage["away_team"]==team,["prob1","prob2"]].sum(axis=1))).sum()
        temp_list.append([team, xG/3, pwin/3, xGa/3])
        
    df_temp = pd.DataFrame(temp_list)
    df_temp.columns = ["country","xG","pwin", "xGa"]
    df_winner = df_winner.merge(df_temp, on = "country")
    
    sims = joblib.load("common/ressources/sims")
    df_winner["name"] = df_winner["name"].replace("South_Korea","South Korea")
    for country in df_winner["name"]:
        R16, QF, SF, Final = get_play_off_opps(country, sims)
        df_winner.loc[(df_winner["name"]==country),"R16"] = R16
        df_winner.loc[(df_winner["name"]==country),"QF"] = QF
        df_winner.loc[(df_winner["name"]==country),"SF"] = SF
        df_winner.loc[(df_winner["name"]==country),"Final"] = Final
        
    # df_grid = pd.read_csv("common/ressources/df_grid")
    # df_grid.columns = ["R16_prob", "QF_prob", "SF_prob" ,"Final_prob","W_prob", "name"]
    # df_winner = df_winner.merge(df_grid, on = "name")

    # df_winner["Final"] = df_winner["Final"].replace("null","Argentina")
    # df_winner["R16"] = df_winner["R16"].replace("null","Argentina")
    # df_winner["QF"] = df_winner["QF"].replace("null","Argentina")
    # df_winner["SF"] = df_winner["SF"].replace("null","Argentina")
    
    # for country in df_winner["name"]:
    #     df_winner.loc[df_winner["name"]==country,"prob_to_win_R16"] = df_winner.loc[df_winner["name"] == df_winner.loc[df_winner["name"]==country,"R16"].values[0],"prob_to_win"].values[0]
    #     df_winner.loc[df_winner["name"]==country,"prob_to_win_QF"] = df_winner.loc[df_winner["name"] == df_winner.loc[df_winner["name"]==country,"QF"].values[0],"prob_to_win"].values[0]
    #     df_winner.loc[df_winner["name"]==country,"prob_to_win_SF"] = df_winner.loc[df_winner["name"] == df_winner.loc[df_winner["name"]==country,"SF"].values[0],"prob_to_win"].values[0]
    #     df_winner.loc[df_winner["name"]==country,"prob_to_win_Final"] = df_winner.loc[df_winner["name"] == df_winner.loc[df_winner["name"]==country,"Final"].values[0],"prob_to_win"].values[0]

    # df_winner["prob_to_win_R16"] = df_winner["prob_to_win"]/(df_winner["prob_to_win_R16"]+df_winner["prob_to_win"])
    # df_winner["prob_to_win_QF"] = df_winner["prob_to_win"]/(df_winner["prob_to_win_QF"]+df_winner["prob_to_win"])
    # df_winner["prob_to_win_SF"] = df_winner["prob_to_win"]/(df_winner["prob_to_win_SF"]+df_winner["prob_to_win"])
    # df_winner["prob_to_win_Final"] = df_winner["prob_to_win"]/(df_winner["prob_to_win_Final"]+df_winner["prob_to_win"])

    # df_winner["xG_R16"] = df_winner["prob_to_win_R16"]/df_winner["pwin"]*df_winner["xG"]
    # df_winner["xG_QF"] = df_winner["prob_to_win_QF"]/df_winner["pwin"]*df_winner["xG"]
    # df_winner["xG_SF"] = df_winner["prob_to_win_SF"]/df_winner["pwin"]*df_winner["xG"]
    # df_winner["xG_Final"] = df_winner["prob_to_win_Final"]/df_winner["pwin"]*df_winner["xG"]

    # df_winner["xGa_R16"] = df_winner["prob_to_win_R16"]/df_winner["pwin"]*df_winner["xGa"]
    # df_winner["xGa_QF"] = df_winner["prob_to_win_QF"]/df_winner["pwin"]*df_winner["xGa"]
    # df_winner["xGa_SF"] = df_winner["prob_to_win_SF"]/df_winner["pwin"]*df_winner["xGa"]
    # df_winner["xGa_Final"] = df_winner["prob_to_win_Final"]/df_winner["pwin"]*df_winner["xGa"]
    # df_winner.to_csv("common/ressources/df_winner", index = False)
    
    return df_winner