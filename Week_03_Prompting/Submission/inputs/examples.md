Question: give me some italian restaurants in exampleville with a rating above 2?
SQL: SELECT l.HOUSE_NUMBER, r.NAME FROM RESTAURANT r JOIN LOCATION l ON l.RESTAURANT_ID=r.ID WHERE r.CITY_NAME='exampleville' AND r.FOOD_TYPE='italian' AND r.RATING>2;

Question: give me some restaurants in the example region?
SQL: SELECT l.HOUSE_NUMBER, r.NAME FROM RESTAURANT r JOIN LOCATION l ON l.RESTAURANT_ID=r.ID JOIN GEOGRAPHIC g ON g.CITY_NAME=r.CITY_NAME WHERE g.REGION='example region';
