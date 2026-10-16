import pandas as pd, json, sys, os, collections
D=sys.argv[1]; DATA=sys.argv[2]; OUT=sys.argv[3]; NS=50
P=json.load(open(DATA))['players']; idx={p[3]:i for i,p in enumerate(P)}
t=pd.read_parquet(f'{D}/Teams.parquet')[['yearID','teamID','teamIDBR']]
tbr={(r.yearID,r.teamID):r.teamIDBR for r in t.itertuples()}
n=lambda v:0 if pd.isna(v) else int(v)
cards=collections.defaultdict(dict)
b=pd.read_parquet(f'{D}/Batting.parquet').sort_values(['yearID','stint'])
for r in b.itertuples(index=False):
    i=idx.get(r.playerID)
    if i is None: continue
    cards[i].setdefault('b',[]).append([int(r.yearID),tbr.get((r.yearID,r.teamID),r.teamID),n(r.G),n(r.AB),n(r.R),n(r.H),n(r._9),n(r._10),n(r.HR),n(r.RBI),n(r.SB),n(r.BB),n(r.SO),n(r.HBP),n(r.SF)])
p=pd.read_parquet(f'{D}/Pitching.parquet').sort_values(['yearID','stint'])
for r in p.itertuples(index=False):
    i=idx.get(r.playerID)
    if i is None: continue
    cards[i].setdefault('p',[]).append([int(r.yearID),tbr.get((r.yearID,r.teamID),r.teamID),n(r.W),n(r.L),n(r.G),n(r.GS),n(r.SV),n(r.IPOuts),n(r.H),n(r.ER),n(r.BB),n(r.SO)])
asg=pd.read_parquet(f'{D}/AllstarFull.parquet')
for pid,g in asg.groupby('playerID'):
    if pid in idx: cards[idx[pid]]['as']=sorted(set(int(y) for y in g.yearID))
a=pd.read_parquet(f'{D}/Appearances.parquet')
pos=['G_p','G_c','G_1b','G_2b','G_3b','G_ss','G_lf','G_cf','G_rf','G_dh']; lab=['P','C','1B','2B','3B','SS','LF','CF','RF','DH']
s=a.groupby('playerID')[pos].sum()
pe=pd.read_parquet(f'{D}/People.parquet').set_index('playerID')
M='Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
for pid,row in s.iterrows():
    if pid not in idx: continue
    v=[n(x) for x in row]; order=sorted(range(10),key=lambda k:-v[k])
    pr=lab[order[0]]
    if order[0]==0 and v[order[1]]>=100: pr='P / '+lab[order[1]]
    elif order[0]!=0 and v[0]>=50: pr=pr+' / P'
    pp=pe.loc[pid]; bio={'pos':pr}
    for k,col in [('bats','bats'),('throws','throws')]:
        if isinstance(pp[col],str): bio[k]=pp[col]
    if not pd.isna(pp.height): bio['ht']=f"{int(pp.height)//12}' {int(pp.height)%12}\""
    if not pd.isna(pp.weight): bio['wt']=int(pp.weight)
    if not pd.isna(pp.birthYear):
        bio['born']=(f"{M[int(pp.birthMonth)-1]} {int(pp.birthDay)}, " if not pd.isna(pp.birthMonth) and not pd.isna(pp.birthDay) else "")+str(int(pp.birthYear))
    place=", ".join(x for x in [pp.birthCity, pp.birthState if isinstance(pp.birthState,str) and pp.birthCountry=='USA' else pp.birthCountry] if isinstance(x,str))
    if place: bio['from']=place
    cards[idx[pid]]['bio']=bio
os.makedirs(OUT,exist_ok=True)
sh=[{} for _ in range(NS)]
for i,c in cards.items(): sh[i%NS][i]=c
sizes=[]
for k in range(NS):
    s_=json.dumps(sh[k],separators=(',',':'));open(f'{OUT}/{k}.json','w').write(s_);sizes.append(len(s_))
print(len(cards),'cards; shard kb min/max',min(sizes)//1024,max(sizes)//1024,'total MB',sum(sizes)/1e6)
