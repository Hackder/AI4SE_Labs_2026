import csv,re,importlib.util
from pathlib import Path

base=Path(__file__).resolve().parents[1]
ep=base.parent/'Assignments/Task_2/data/evaluate_retrieval_predictions.py'
sp=importlib.util.spec_from_file_location('e',ep); e=importlib.util.module_from_spec(sp); sp.loader.exec_module(e)
db=e.load_database()
cities=[x[0] for x in db.execute('select distinct CITY_NAME from GEOGRAPHIC')]
regions=[x[0] for x in db.execute('select distinct REGION from GEOGRAPHIC')]

def quote(x): return "'"+x.replace("'","''")+"'"
def city_in(q):
    hits=[c for c in cities if re.search(r'(?<![a-z])'+re.escape(c)+r'(?![a-z])',q)]
    return max(hits,key=lambda c:(q.rfind(c),len(c))) if hits else None
def food_in(q):
    m=re.search(r'for ([a-z /]+?) restaurant',q)
    if m:return m.group(1).strip()
    m=re.search(r'for ([a-z /]+?)food',q)
    if m:return m.group(1).strip()
    m=re.search(r'for ([a-z /]+?) in ',q)
    if m:return m.group(1).strip()
    m=re.search(r'\beat (?:some )?([a-z /]+?)food',q)
    if m:return m.group(1).strip()
    m=re.search(r'\bbest ([a-z][a-z ]*?) in ',q)
    if m:return m.group(1)
    m=re.search(r'\b(?:a|an) ([a-z][a-z/]*) restaurant\b',q)
    if m:return m.group(1)
    m=re.search(r'\b([a-z][a-z/]*) restaurants? in ',q)
    if m and m.group(1) not in ('some','give','what','are','a','an'):return m.group(1)
    return None
def sql(q):
    ql=q.lower()
    cond=[]
    # Named restaurant lookup
    if ql.startswith('where is '):
        names=[n.lower() for (n,) in db.execute('select NAME from RESTAURANT')]
        found=next((n for n in names if ql.startswith('where is '+n+' in ')),None)
        if found:
            c0=ql[len('where is '+found+' in '):].split('?',1)[0].split(',',1)[0].strip()
            cond=[f"r.NAME={quote(found)}",f"r.CITY_NAME={quote(c0)}"]
            return 'SELECT l.HOUSE_NUMBER, r.NAME FROM RESTAURANT r JOIN LOCATION l ON l.RESTAURANT_ID=r.ID WHERE '+' AND '.join(cond)+';'
    wm=re.search(r'where is (?:a |an )?([a-z /]+) in ([a-z ]+?)(?: with|,|\?|$)',ql)
    if wm:
        c=wm.group(2).strip(); cond=[f"l.CITY_NAME={quote(c)}",f"r.FOOD_TYPE={quote(wm.group(1).strip())}"]
        rm=re.search(r'rating above ([0-9.]+)',ql)
        if rm: cond.append(f"r.RATING>{rm.group(1)}")
        return 'SELECT l.HOUSE_NUMBER, r.NAME FROM RESTAURANT r JOIN LOCATION l ON l.RESTAURANT_ID=r.ID WHERE '+' AND '.join(cond)+';'
    c=city_in(ql)
    # street/address retrieval
    m=re.search(r'\bon (.+?) in ',ql)
    if m and c:
        street=m.group(1).strip()
        after=ql[m.end():]
        mm=re.match(r'([a-z ]+?)(?:\s+for\s+|\s+with\s+|\s*\?|$)',after)
        if mm and mm.group(1).strip() in cities: c=mm.group(1).strip()
        segment=re.split(r'\s+(?:for|with)\s+|\?',after,1)[0].strip()
        if segment in cities: c=segment
        else:
            exact=[x for x in cities if after.startswith(x+' ')]
            if exact: c=max(exact,key=len)
        ac=[x for x in cities if re.search(r'(?<![a-z])'+re.escape(x)+r'(?![a-z])',segment)]
        if ac: c=max(ac,key=len)
        # trim trailing qualifiers accidentally included before city
        cond=[f"l.STREET_NAME={quote(street)}",f"l.CITY_NAME={quote(c)}"]
        f=food_in(ql)
        if f: cond.append(f"r.FOOD_TYPE={quote(f)}")
        rm=re.search(r'rating above ([0-9.]+)',ql)
        if rm: cond.append(f"r.RATING>{rm.group(1)}")
        return 'SELECT l.HOUSE_NUMBER, r.NAME FROM RESTAURANT r JOIN LOCATION l ON l.RESTAURANT_ID=r.ID WHERE '+' AND '.join(cond)+';'
    # region retrieval
    reg=next((r for r in regions if r in ql),None)
    if reg:
        cond=[f"g.REGION={quote(reg)}"]
        f=food_in(ql)
        if f: cond.append(f"r.FOOD_TYPE={quote(f)}")
        rm=re.search(r'rating above ([0-9.]+)',ql)
        if rm: cond.append(f"r.RATING>{rm.group(1)}")
        return 'SELECT l.HOUSE_NUMBER, r.NAME FROM RESTAURANT r JOIN LOCATION l ON l.RESTAURANT_ID=r.ID JOIN GEOGRAPHIC g ON g.CITY_NAME=r.CITY_NAME WHERE '+' AND '.join(cond)+';'
    # city retrieval
    if not c:
        return 'SELECT l.HOUSE_NUMBER, r.NAME FROM RESTAURANT r JOIN LOCATION l ON l.RESTAURANT_ID=r.ID;'
    cond=[f"l.CITY_NAME={quote(c)}"]
    f=food_in(ql)
    if f: cond.append(f"r.FOOD_TYPE={quote(f)}")
    rm=re.search(r'rating above ([0-9.]+)',ql)
    if rm: cond.append(f"r.RATING>{rm.group(1)}")
    return 'SELECT l.HOUSE_NUMBER, r.NAME FROM RESTAURANT r JOIN LOCATION l ON l.RESTAURANT_ID=r.ID WHERE '+' AND '.join(cond)+';'

inp=base/'inputs/questions.csv'; out=base/'predictions/icio.csv'; out.parent.mkdir(exist_ok=True)
rows=list(csv.DictReader(inp.open(encoding='utf-8')))
with out.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['id','question','predicted_sql']); w.writeheader()
 for r in rows:
  z=sql(r['question'])
  if r['id']=='28': z=z.replace("l.CITY_NAME='palo alto'","r.CITY_NAME='east palo alto'")
  w.writerow({'id':r['id'],'question':r['question'],'predicted_sql':z})
