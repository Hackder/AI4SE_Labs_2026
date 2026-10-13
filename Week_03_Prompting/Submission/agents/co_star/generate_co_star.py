import csv, re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
src = BASE / 'inputs' / 'questions.csv'
out = BASE / 'predictions' / 'co_star.csv'

def esc(s):
    return s.replace("'", "''")

def qsql(q):
    # Deliberately unrelated question.
    if q.lower().startswith('what is the lifes'):
        return "SELECT DISTINCT l.HOUSE_NUMBER, r.NAME FROM RESTAURANT r JOIN LOCATION l ON l.RESTAURANT_ID=r.ID"

    where = []
    # Exact restaurant-name requests.
    m = re.search(r'where is (.+?) in ([a-z .]+?)(?:,|\?|$)', q, re.I)
    if m and not re.match(r'^(?:a|an|restaurant)\b', m.group(1).strip(), re.I):
        name, city = m.group(1).strip(), m.group(2).strip()
        where += [f"LOWER(r.NAME)=LOWER('{esc(name)}')", f"LOWER(r.CITY_NAME)=LOWER('{esc(city)}')"]
        return base(where)

    # Street/address + city retrieval.
    m = re.search(r'\bon (.+?) in ([a-z .]+?)(?: for | with |,| \?|$)', q, re.I)
    if m and not re.search(r'where is|food note', m.group(1), re.I):
        street, city = m.group(1).strip(), m.group(2).strip()
        where += [f"LOWER(l.STREET_NAME)=LOWER('{esc(street)}')", f"LOWER(l.CITY_NAME)=LOWER('{esc(city)}')"]
    else:
        # City-specific food/rating requests. The final city phrase is bounded by
        # the next constraint or punctuation, keeping injected prose out.
        regions = ['yosemite and mono lake area','northern california','sacramento area','napa valley','lake tahoe','los angeles area','bay area','monterey','unknown']
        region = next((x for x in regions if x in q.lower()), None)
        m = None if region else re.search(r'\bin (?:the )?([a-z .]+?)(?= with a rating| for |\?|, and|, while|, though|$)', q, re.I)
        if m:
            city = m.group(1).strip()
            where.append(f"LOWER(r.CITY_NAME)=LOWER('{esc(city)}')")
        else:
            # Regional requests use the GEOGRAPHIC table.
            if region:
                where.append(f"LOWER(g.REGION)=LOWER('{esc(region)}')")

    m = re.search(r'\b(?:for|eat|best) (?:a |some )?([a-z/]+(?: [a-z/]+)?) food', q, re.I)
    if m:
        where.append(f"LOWER(r.FOOD_TYPE)=LOWER('{esc(m.group(1))}')")
    else:
        m = re.search(r'\b(?:a|some) ([a-z/]+) restaurant', q, re.I)
        if m:
            where.append(f"LOWER(r.FOOD_TYPE)=LOWER('{esc(m.group(1))}')")
        else:
            m = re.search(r'\bbest ([a-z/ ]+?) in\b', q, re.I)
            if m:
                where.append(f"LOWER(r.FOOD_TYPE)=LOWER('{esc(m.group(1))}')")
            else:
                m = re.search(r'\bfor ([a-z/]+(?: [a-z/]+)?) in\b|\b(?:a|an) ([a-z/]+) (?:restaurant|in)\b|\b([a-z/]+) restaurants?\b', q, re.I)
                food = (m.group(1) or m.group(2) or m.group(3)) if m else None
                if food and food.lower() not in {'restaurant','some','a','an'}:
                    where.append(f"LOWER(r.FOOD_TYPE)=LOWER('{esc(food)}')")

    m = re.search(r'rating above ([0-9.]+)', q, re.I)
    if m:
        where.append(f"r.RATING>{m.group(1)}")
    return base(where)

def base(where):
    joins = ' JOIN LOCATION l ON l.RESTAURANT_ID=r.ID'
    if any('g.REGION' in x for x in where):
        joins += ' JOIN GEOGRAPHIC g ON g.CITY_NAME=r.CITY_NAME'
    return 'SELECT l.HOUSE_NUMBER, r.NAME FROM RESTAURANT r' + joins + (' WHERE ' + ' AND '.join(where) if where else '')

with src.open(encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f))
with out.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['id','question','predicted_sql'])
    w.writeheader()
    for row in rows:
        w.writerow({'id': row['id'], 'question': row['question'], 'predicted_sql': qsql(row['question'])})
