db = db.getSiblingDB("yelp");

db.createCollection("business");
db.createCollection("review");
db.createCollection("user");
