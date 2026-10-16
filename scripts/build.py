import pandas as pd, json, sys, collections
D=sys.argv[1]; OUT=sys.argv[2]
a=pd.read_parquet(f'{D}/Appearances.parquet')[['yearID','teamID','playerID','G_all']]
p=pd.read_parquet(f'{D}/People.parquet').set_index('playerID')
t=pd.read_parquet(f'{D}/Teams.parquet')[['yearID','teamID','name','franchID']]
fr=pd.read_parquet(f'{D}/TeamsFranchises.parquet').set_index('franchID')
hof=pd.read_parquet(f'{D}/HallOfFame.parquet')
hof=set(hof[(hof.inducted=='Y')&(hof.category=='Player')].playerID)
asg=pd.read_parquet(f'{D}/AllstarFull.parquet').groupby('playerID').yearID.nunique()
aw=pd.read_parquet(f'{D}/AwardsPlayers.parquet')
aw=aw[aw.awardID.isin(['Most Valuable Player','Cy Young Award','Rookie of the Year'])].groupby('playerID').size()
a['G_all']=a.G_all.fillna(0)
car=a.groupby('playerID').agg(G=('G_all','sum'),y0=('yearID','min'),y1=('yearID','max'))
# order players by career games desc so famous folks get small indices
car=car.sort_values('G',ascending=False)
ids=list(car.index); idx={pid:i for i,pid in enumerate(ids)}
players=[]
for pid,r in car.iterrows():
    pp=p.loc[pid]
    fn=pp.nameFirst if isinstance(pp.nameFirst,str) else ""; ln=pp.nameLast if isinstance(pp.nameLast,str) else ""
    name=f"{fn} {ln}".strip()
    by=pp.birthYear; bm=pp.birthMonth
    bage=0 if pd.isna(by) else int(by)+(1 if (not pd.isna(bm) and int(bm)>=7) else 0)
    a_=int(asg.get(pid,0)); h_=pid in hof; w_=int(aw.get(pid,0))
    eligible = h_ or a_>=1 or r.G>=400
    fame = 1 + r.G/200 + 3*a_ + 15*h_ + 5*w_
    bd=0 if (pd.isna(pp.birthMonth) or pd.isna(pp.birthDay)) else int(pp.birthMonth)*100+int(pp.birthDay)
    players.append([name,int(r.y0),int(r.y1),pid,round(fame,1) if eligible else 0,1 if h_ else 0,ln+" "+fn,bage,bd])
tn={(r.yearID,r.teamID):r['name'] for _,r in t.iterrows()}
tf={(r.yearID,r.teamID):r['franchID'] for _,r in t.iterrows()}
# franchise display name = most recent team name; active flag
last=t.sort_values('yearID').groupby('franchID').last()
fids=sorted(last.index,key=lambda f:(str(fr.loc[f,'active'])!='Y',last.loc[f,'name']))
fidx={f:i for i,f in enumerate(fids)}
franch=[[last.loc[f,'name'],1 if str(fr.loc[f,'active'])=='Y' else 0,int(t[t.franchID==f].yearID.min()),int(last.loc[f,'yearID'])] for f in fids]
names=[]; nidx={}
teams=[]
for (y,tid),g in a.groupby(['yearID','teamID']):
    n=tn.get((y,tid),tid)
    if n not in nidx: nidx[n]=len(names); names.append(n)
    g=g.sort_values('G_all',ascending=False)
    teams.append([int(y),nidx[n],[idx[x] for x in g.playerID],fidx[tf[(y,tid)]]])
json.dump({'v':'lahman-2025','players':players,'teamNames':names,'teams':teams,'franchises':franch},open(OUT,'w'),separators=(',',':'))
print(len(players),len(teams),sum(1 for x in players if x[4]),'eligible')
