class QueryBuilder:
    def __init__(self):
        self.query = ""

    def build_query(self, destination, dates, travelers, budget, interests):
        self.query = f"Find travel packages to {destination} for {travelers} travelers from {dates[0]} to {dates[1]} with a budget of {budget}. Interests include {', '.join(interests)}."
        return self.query