import numpy as np
import pandas as pd
import pickle
import os
import matplotlib.pyplot as plt

# teams. you can also write your own teams
premier_league=[
    "Arsenal","Manchester City","Manchester United","Aston Villa","Liverpool",
    "Chelsea","Brentford","Everton","Newcastle United","Brighton",
    "Sunderland","Fulham","Crystal Palace","Bournemouth","Leeds United",
    "Nottingham Forest","Tottenham Hotspur","West Ham United","Burnley","Wolverhampton"
]

championship=[
    "Coventry","Middlesbrough","Ipswich","Millwall","Hull City","Southampton",
    "Wrexham","Derby County","Watford","Norwich","Birmingham","QPR",
    "Preston","Swansea","Stoke City","Bristol City","Sheffield United","Charlton",
    "Blackburn","West Bromwich","Portsmouth","Leicester City","Oxford United","Sheffield Wednesday"
]

league_one=[
    "Lincoln City","Cardiff City","Bolton","Bradford City","Stokeport","Stevenage",
    "Polymouth","Reading","Huddersfield","Wycombe","Luton","Peterborough",
    "Barnsley","AFC Wimbledon","Doncaster","Mansfield","Leyton Orient","Burton",
    "Wigan Athletic","Exeter City","Blackpool","Rotherham","Northampton","Port Vale"
]

league_two=[
    "Bromley","Milton Keynes Dons","Cambridge United","Notts County","Swindon","Salford City",
    "Grimsby","Chesterfield","Oldham","Crewe","Walsall","Barnet",
    "Fleetwood","Colchester United","Accorington","Gillingham","Bristol Rovers","Cheltenham",
    "Shrewsbury","Tranmere","Crawley","Newport","Harrogate","Barrow"
]

np.random.seed(114514)

# Premier League big6 and three mid-table teams
BIG_6 = ["Manchester City", "Manchester United", "Arsenal", "Liverpool", "Chelsea","Tottenham Hotspur"]  

MID_3 = ["Aston Villa","Everton","Newcastle United"]
 
# teams that you want to track but are not in the big 6 or mid 3
I_WANNA_KNOW=[]

history_rankings = {team: [] for team in BIG_6 + MID_3 + I_WANNA_KNOW}

def init_team_data():
    data = {}
    for i, t in enumerate(premier_league):
        # differentiate reputation based on historical status
        if t in BIG_6:
            data[t] = {'reputation': 100, 'poach_penalty': 0}
        elif t in MID_3:
            data[t] = {'reputation': 90, 'poach_penalty': 0}
        else:
            data[t] = {'reputation': 80 - (i * 20 / len(premier_league)), 'poach_penalty': 0}
            
    for i, t in enumerate(championship):
        data[t] = {'reputation': 60 - (i * 20 / len(championship)), 'poach_penalty': 0}
    for i, t in enumerate(league_one):
        data[t] = {'reputation': 40 - (i * 15 / len(league_one)), 'poach_penalty': 0}
    for i, t in enumerate(league_two):
        data[t] = {'reputation': 25 - (i * 15 / len(league_two)), 'poach_penalty': 0}
    return data


# every league has its own teams, scores, promotion/relegation rules, and links to upper/lower leagues
class League:
    def __init__(self, name, teams, direct_up=0, playoff_start=0, playoff_end=0, direct_down=0, up_league=None, down_league=None):
        self.name = name
        self.teams = teams
        self.scores = []
        self.direct_up = direct_up
        self.direct_down = direct_down
        self.playoff_start = playoff_start
        self.playoff_end = playoff_end
        self.up_league = up_league
        self.down_league = down_league
        self.up = []
        self.down = []

def league(league):
    global team_data 
    max_score = len(league.teams) * 4 - 30
    id = 0
    raw_scores=[]
    
    for team in league.teams:
        rep = team_data[team]['reputation']
        poach_penalty = team_data[team]['poach_penalty']
        
        # scores are partly based on ranking from last season and there reputation
        form_score = max_score - (id * 35 / len(league.teams))
        rep_score = (rep / 100.0) * 35 
        
        raw_score = form_score + rep_score + np.random.randn() * 10 - poach_penalty
        raw_scores.append(raw_score)
        team_data[team]['poach_penalty']=0
        id+=1
        
        team_data[team]['poach_penalty'] = 0
        id += 1
    
    s_max= max(raw_scores)
    s_min= min(raw_scores)
    diff=s_max-s_min
    final_score=[]
    for s in raw_scores:
        norm_s=int((s-s_min)/diff*75+20)
        final_score.append(norm_s)

    idx = np.argsort(final_score)[::-1]
    teams_sorted = [league.teams[i] for i in idx]
    scores_sorted = [final_score[i] for i in idx]

    league.teams = teams_sorted
    league.scores = scores_sorted
    
    # write down the rankings of the teams we care about for history tracking
    for rank, team in enumerate(teams_sorted):
        if team in history_rankings:
            if league.name == "Premier League":
                history_rankings[team].append(rank + 1)
            else: 
                history_rankings[team].append(None) 

        if league.name == "Premier League":
            if team in BIG_6:
                # big6 have very stable reputation
                team_data[team]['reputation'] = max(95, team_data[team]['reputation'] + 0.5)
                if team_data[team]['reputation'] > 120:
                    team_data[team]['reputation'] = 120
                if np.random.rand()<0.1:
                    team_data[team]['reputation']-=40
                    print(f"⚠️ Oh no:【{team}】 had a meltdown! Reputation plummets!")
            elif team in MID_3:
                if rank < 3:
                    team_data[team]['reputation'] = min(100, team_data[team]['reputation'] + 1.5)
                    if team_data[team]['reputation'] < 101:
                        penalty = 15
                        print(f"⚠️ Although 【{team}】 ranked {rank+1}, but core players were immediately bought by stronger clubs!")
                        team_data[team]['poach_penalty'] = penalty
                elif rank < 5: 
                    team_data[team]['reputation'] = min(90, team_data[team]['reputation'] + 1)
                elif rank >= len(teams_sorted) - 5:
                    team_data[team]['reputation'] = max(10, team_data[team]['reputation'] - 1)
                if np.random.rand()<0.15:
                    team_data[team]['reputation']-=30
                    print(f"⚠️ Oh no:【{team}】 had a meltdown! Reputation plummets!")
            else:
                if rank < 5: # Small teams that break into top 5 will get poached hard
                    team_data[team]['reputation'] = min(100, team_data[team]['reputation'] + 1.5)
                    # Without a high reputation, they are very vulnerable to poaching
                    if team_data[team]['reputation'] < 101:
                        penalty = 30 
                        print(f"⚠️ Although 【{team}】 ranked {rank+1}, but core players were immediately bought by stronger clubs!")
                        team_data[team]['poach_penalty'] = penalty
                    if np.random.rand()<0.2:
                        team_data[team]['reputation']-=30
                        print(f"⚠️ Oh no:【{team}】 had a meltdown! Reputation plummets!")
                if rank < 10: # Small teams that make it to the top 10 will be targeted!
                    team_data[team]['reputation'] = min(100, team_data[team]['reputation'] + 1.5)
                    # Without a high reputation, they are very vulnerable to poaching
                    if team_data[team]['reputation'] < 85:
                        # 惩罚力度按排名来算：第一名被扣15分，第十名被扣6分
                        penalty = 10 
                        print(f"⚠️ Although 【{team}】 ranked {rank+1}, but core players were immediately bought by stronger clubs!")
                        team_data[team]['poach_penalty'] = penalty
                    if np.random.rand()<0.2:
                        team_data[team]['reputation']-=30
                        print(f"⚠️ Oh no:【{team}】 had a meltdown! Reputation plummets!")
                elif rank >= len(teams_sorted) - 3: 
                    team_data[team]['reputation'] = max(10, team_data[team]['reputation'] - 2)
                    if np.random.rand()<0.2:
                        team_data[team]['reputation']-=20
                        print(f"⚠️ Oh no:【{team}】 had a meltdown! Reputation plummets!")
        else:
            if rank < 3: 
                team_data[team]['reputation'] = min(120, team_data[team]['reputation'] + 1)
            elif rank >= len(teams_sorted) - 4:
                team_data[team]['reputation'] = max(10, team_data[team]['reputation'] - 1)
            # big teams in lower leagues will maintain higher reputation, making it easier for them to bounce back
            if team in BIG_6:
                team_data[team]['reputation']=150
            elif team in MID_3:
                team_data[team]['reputation']=120


    if league == pl:
        df = pd.DataFrame({'Team': teams_sorted, 'Score': scores_sorted})
        df.index += 1
        print(f"{league.name} League Standings:")
        print(df)
        for team in league.teams:
            print(f"  - {team}: Reputation={team_data[team]['reputation']:.1f}, Poach Penalty={team_data[team]['poach_penalty']}")

    league.scores = []

    if league.direct_up > 0:
        league.up = league.teams[:league.direct_up]
        league.teams = league.teams[league.direct_up:]
    if league.playoff_start > 0 and league.playoff_end > 0:
        playoff = np.random.choice(league.teams[0:league.playoff_end-league.playoff_start+league.direct_up+1], 1)
        league.up += playoff.tolist()
        league.teams.remove(playoff[0])
    if league.direct_down > 0:
        league.down = league.teams[-league.direct_down:]
        league.teams = league.teams[:-league.direct_down]

    return league


def next_season():
    global pl, c, lo, lt, team_data
    
    # Saudi richers won't buy huge clubs
    if np.random.rand() < 0.5:
        all_teams = pl.teams + c.teams
        eligible_teams = [t for t in all_teams if t not in BIG_6]
        if eligible_teams:
            lucky_team = np.random.choice(eligible_teams)
            # After being bought, the team's reputation will be boosted to a high level
            if lucky_team in pl.teams:
                print(f"\n💰💰💰 Breaking news! Premier League team 【{lucky_team}】 has been acquired by a Middle Eastern consortium! Massive investment expected, with the potential to become a new powerhouse!\n")
                team_data[lucky_team]['reputation'] = 100
            else:
                print(f"\n💰💰💰 Breaking news! Championship team 【{lucky_team}】 has been acquired by a Middle Eastern consortium! Massive investment expected, with the potential to become a new powerhouse!\n")
                team_data[lucky_team]['reputation'] = 120
    # teams in lower leagues have a higher chance to be bought, as they are cheaper and have more potential to grow
    if np.random.rand() < 0.99:
        all_teams = lo.teams + lt.teams
        eligible_teams = [t for t in all_teams if t not in BIG_6]
        if eligible_teams:
            lucky_team = np.random.choice(eligible_teams)
            if lucky_team in lo.teams:
                print(f"\n💰💰💰 Breaking news! League One team 【{lucky_team}】 has been acquired by a Middle Eastern consortium! Massive investment expected, with the potential to become a new powerhouse!\n")
                team_data[lucky_team]['reputation'] = 100
            else:
                print(f"\n💰💰💰 Breaking news! League Two team 【{lucky_team}】 has been acquired by a Middle Eastern consortium! Massive investment expected, with the potential to become a new powerhouse!\n")
                team_data[lucky_team]['reputation'] = 120

    # create four leagues for the new season
    pl = league(pl)
    c = league(c)
    lo = league(lo)
    lt = league(lt)
    pl.teams += c.up
    c.teams = pl.down + c.teams + lo.up
    lo.teams = c.down + lo.teams + lt.up
    lt.teams = lo.down + lt.teams


def save_leagues(filename, leagues, seasons, team_data):
    with open(filename, "wb") as f:
        pickle.dump((leagues, seasons, team_data), f)

def load_leagues(filename):
    with open(filename, "rb") as f:
        data = pickle.load(f)
        if len(data) == 2:
            return data[0], data[1], init_team_data()
        else:
            return data

SAVE_FILE = "league_save.pkl"

if os.path.exists(SAVE_FILE):
    print("Loading save file, continuing season simulation...")
    leagues, seasons, team_data = load_leagues(SAVE_FILE)
    pl, c, lo, lt = leagues
else:
    print("No save file found, creating new leagues...")

    pl = League("Premier League", premier_league, direct_down=3)
    c  = League("Championship", championship, direct_up=2, playoff_start=3, playoff_end=6, direct_down=3)
    lo = League("League One", league_one, direct_up=2, playoff_start=3, playoff_end=6, direct_down=4)
    lt = League("League Two", league_two, direct_up=3, playoff_start=4, playoff_end=7)
    seasons = 0
    
    team_data = init_team_data()

    # link the leagues together
    pl.down_league = c
    c.up_league = pl;  c.down_league = lo
    lo.up_league = c;  lo.down_league = lt
    lt.up_league = lo

leagues = [pl, c, lo, lt]

for _ in range(10):
    seasons += 1
    print(f"🎉Season {seasons}🎉")
    next_season()
    print("===================================")

save_leagues(SAVE_FILE, leagues, seasons, team_data)

plt.figure(figsize=(12, 6))
seasons_range = range(1, 11)

for team in BIG_6 + MID_3 + I_WANNA_KNOW:
    plt.plot(seasons_range, history_rankings[team], marker='o', label=team, linewidth=2)

plt.gca().invert_yaxis()
plt.yticks(range(1, 21))
plt.xlabel('Season')
plt.ylabel('Rank')
plt.title('BIG 6, MID_3 and I_WANNA_KNOW in Last 10 Seasons') 
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.show()