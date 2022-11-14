import urllib.request, json
import pandas as pd
import numpy as np

def get_holdet_data():
    cols = ["name1", "name2" ,"name3","name4","name5","name6", "name7"]
    df_final = pd.DataFrame(columns = cols)
    for j in range(40):
        try:
            url = f"""https://www.holdet.dk/handlers/tradedata.ashx?language=da&game=2022-world-manager&userteam=&partial-name=&positions=&team=&formation=&minimum-value=0&maximum-value=0&lineup=&original-lineup=&sort=&addable-only=false&direction=-1&page={j}&include-headers=true&include-formations=true&include-lineup=true&include-fields=true&r=1666622443519"""
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            for i in range(len(data["Dataset"]["Items"])):
                # cols = ["name1", "name2" ,"name3","name4","name5","name6", "name7","country"]
                df_new = pd.DataFrame()
                df_new.loc[i,"name1"] = data["Dataset"]["Items"][i]["Values"][1]
                df_new.loc[i,"name2"] = data["Dataset"]["Items"][i]["Values"][2]
                df_new.loc[i,"name3"] = data["Dataset"]["Items"][i]["Values"][3]
                df_new.loc[i,"name4"] = data["Dataset"]["Items"][i]["Values"][4]
                df_new.loc[i,"name5"] = data["Dataset"]["Items"][i]["Values"][5]
                df_new.loc[i,"name6"] = data["Dataset"]["Items"][i]["Values"][6]
                df_new.loc[i,"name7"] = data["Dataset"]["Items"][i]["Values"][7]
                df_new.loc[i,"country"] = data["Dataset"]["Items"][i]["Values"][9]
                df_new.loc[i,"price"] = data["Dataset"]["Items"][i]["Values"][16]
                df_new.loc[i,"position"] = data["Dataset"]["Items"][i]["Texts"][15]
                df_final = pd.concat([df_final, df_new])
        except:
            print(f"""no such page: {j}""")
            
            
    return df_final


def get_play_off_opps(teamname,sims):
    Nsims = float(len(sims))
    group_stages = list(np.full(int(Nsims),"Group D"))
    R16_opponents = list(np.full(int(Nsims),"null"))
    QF_opponents = list(np.full(int(Nsims),"null"))
    SF_opponents = list(np.full(int(Nsims),"null"))
    Final_opponents = list(np.full(int(Nsims),"null"))
    count = 0
    for count, s in enumerate(sims):
        for i in range(len(s.KnockOut.R16matches)):
            if teamname==s.KnockOut.R16matches[i].team1.name: 
                R16_opponents[count] = s.KnockOut.R16matches[i].team2.name
            elif teamname==s.KnockOut.R16matches[i].team2.name: 
                R16_opponents[count] = s.KnockOut.R16matches[i].team1.name
        
        for i in range(len(s.KnockOut.QFmatches)):
            if teamname==s.KnockOut.QFmatches[i].team1.name: 
                QF_opponents[count] = s.KnockOut.QFmatches[i].team2.name
            elif teamname==s.KnockOut.QFmatches[i].team2.name: 
                QF_opponents[count] = s.KnockOut.QFmatches[i].team1.name
                
        for i in range(len(s.KnockOut.SFmatches)):
            if teamname==s.KnockOut.SFmatches[i].team1.name: 
                SF_opponents[count] = s.KnockOut.SFmatches[i].team2.name
            elif teamname==s.KnockOut.SFmatches[i].team2.name: 
                SF_opponents[count] = s.KnockOut.SFmatches[i].team1.name
        
        for i in range(len(s.KnockOut.Final)):
            if teamname==s.KnockOut.Final[i].team1.name: 
                Final_opponents[count] = s.KnockOut.Final[i].team2.name
            elif teamname==s.KnockOut.Final[i].team2.name: 
                Final_opponents[count] = s.KnockOut.Final[i].team1.name
                
        count += 1 

    df_finals = pd.concat([pd.Series(group_stages),
                        pd.Series(R16_opponents),
                        pd.Series(QF_opponents),
                        pd.Series(SF_opponents),
                        pd.Series(Final_opponents)], axis = 1)

    df_finals.columns = ["Group","R16", "QF", "SF", "Final"]
    df_finals["count"] = 0
    df_finals = df_finals.groupby(["Group","R16", "QF", "SF", "Final"], sort=False).size().reset_index(name='count')

    if len(df_finals.groupby("R16")["count"].agg('sum'))>0:
        R16 = df_finals.groupby("R16")["count"].agg('sum').index[0]
    else: 
        R16 = np.nan
        
    if len(df_finals.groupby("QF")["count"].agg('sum'))>0:
        QF = df_finals.groupby("QF")["count"].agg('sum').index[0]
    else: 
        QF = np.nan
        
    if len(df_finals.groupby("SF")["count"].agg('sum'))>0:
        SF = df_finals.groupby("SF")["count"].agg('sum').index[0]
    else: 
        SF = np.nan
        
    if len(df_finals.groupby("SF")["count"].agg('sum'))>0:
        SF = df_finals.groupby("SF")["count"].agg('sum').index[0]
    else: 
        SF = np.nan
        
    if len(df_finals.groupby("Final")["count"].agg('sum'))>0:
        Final = df_finals.groupby("Final")["count"].agg('sum').index[0]
    else: 
        Final = np.nan
        
    return R16, QF, SF, Final

def get_rw(df_holdet):
    import mechanize
    import difflib
    import html5lib
    from http.cookiejar import LWPCookieJar
    import requests
    import json
    import pandas as pd
    browser = mechanize.Browser()
    cj = LWPCookieJar()
    browser.set_cookiejar(cj)
    browser.set_handle_equiv(True)
    browser.set_handle_redirect(True)
    browser.set_handle_robots(False)
    browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    browser.open('http://www.rotowire.com/users/loginnow.htm')
    browser.select_form(nr = 0)
    browser.form['username'] = 'mklarskov'
    browser.form['password'] = 'mads1234'
    browser.submit()
    url = browser.open('https://www.rotowire.com/soccer/tables/projections.php?position=All&league=WOC&type=weekly&myLeagueID=0')
    json_file_rw = url.read()

    js_read = json.loads(json_file_rw.decode('utf-8'))
    rw_data = pd.DataFrame(js_read)

    rw = rw_data[['player', 'team',  'opp','position', 'minutes', 'goals', 'assists', 'shots', 'sog', 'chancecreated',\
            'passes', 'totalpasses', 'crosses', 'accucrosses', 'aerials','dribbles', 'dispossessed','int','tackles',\
            'tackleswon', 'blocks','clearances', 'cleansheet', 'goalsconc', 'saves', 'fouldrawn','foulscommit', 'yellowcard', 'redcard']]

    rw.columns = ['Player', 'Team', 'Opp', 'Pos', 'MIN', 'G', 'A', 'S', 'SOG', 'CC', 'P','AP', 'CR', 'ACR', 'AW', 'DR', 'DSP', 'INT', 'TKL', 'TKLW', 'BLK', 'CL','CS', 'GC', 'SV', 'FS', 'FC', 'Y', 'R']

    rw['Player_match'] = ""
    for i in range(len(rw)):
            try:
                    rw.loc[i,'Player_match'] = difflib.get_close_matches(rw.loc[i,'Player'], df_holdet['name1'])[0]
            except: 
                    rw.loc[i,'Player_match'] = "null"
            
    rw.loc[rw["Player"]=="Bono","Player_match"]="Yassine 'Bono' Bounou"
    rw.loc[rw["Player"]=="Ez Abde","Player_match"]="Abde Ezzalzouli"
    rw.loc[rw["Player"]=="Hwang Hee-Chan","Player_match"]="Hee-Chan Hwang"
    rw.loc[rw["Player"]=="Hwang In-beom","Player_match"]="In-Beom Hwang"
    rw.loc[rw["Player"]=="Kim Jin-su","Player_match"]="Jin-Su Kim"
    rw.loc[rw["Player"]=="Kim Min-Jae","Player_match"]="Min-jae Kim"
    rw.loc[rw["Player"]=="Roan Roberto Wilson Gordon","Player_match"]="Roan Wilson"
    rw.loc[rw["Player"]=="Milad Sarlak","Player_match"]="Milad Mohammadi"
    rw.loc[(rw["Player"]=="Danilo") & (rw["Team"]=="POR"),"Player_match"]="Danilo Pereira"
    if len(rw[rw['Player_match'] == "null"])>0:
            assert("check names, not all is found")
            
            
    return rw