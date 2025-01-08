class YahtzeeGame:
    def __init__(self):
        self.current_player = 0
        self.num_players = 0
        self.rolls_left = 3
        self.dice = [0] * 5
        self.scores = {}
        self.used_categories = {}

        
    def add_player(self):
        player_id = self.num_players
        self.num_players += 1
        self.scores[player_id] = 0
        self.used_categories[player_id] = set()
        return player_id
        
    def roll_dice(self, keep_positions):
        if self.rolls_left <= 0:
            return self.dice
            
        import random
        for i in range(5):
            if i not in keep_positions:
                self.dice[i] = random.randint(1, 6)
                
        self.rolls_left -= 1
        return self.dice
        
    def score_move(self, category):
        if category in self.used_categories[self.current_player]:
            return 0
            
        score = self._calculate_score(category)
        self.scores[self.current_player] += score
        self.used_categories[self.current_player].add(category)
        
        # Passer au joueur suivant et réinitialiser
        self.current_player = (self.current_player + 1) % self.num_players
        self.rolls_left = 3
        self.dice = [0] * 5
        
        return score
        
    def _calculate_score(self, category):
        if category in ["As", "Deux", "Trois", "Quatre", "Cinq", "Six"]:
            value = ["As", "Deux", "Trois", "Quatre", "Cinq", "Six"].index(category) + 1
            return sum(d for d in self.dice if d == value)
            
        counts = [self.dice.count(i) for i in range(1, 7)]
        
        if category == "Brelan":
            if max(counts) >= 3:
                return sum(self.dice)
                
        elif category == "Carré":
            if max(counts) >= 4:
                return sum(self.dice)
                
        elif category == "Full":
            if 2 in counts and 3 in counts:
                return 25
                
        elif category == "Petite Suite":
            for i in range(3):
                if all(j+1 in self.dice for j in range(i, i+4)):
                    return 30
                    
        elif category == "Grande Suite":
            if all(j+1 in self.dice for j in range(5)):
                return 40
                
        elif category == "Yahtzee":
            if max(counts) == 5:
                return 50
                
        elif category == "Chance":
            return sum(self.dice)
            
        return 0
        
    def is_game_over(self):
        for player in range(self.num_players):
            if len(self.used_categories[player]) < 13:
                return False
        return True
        
    def get_winner(self):
        if not self.is_game_over():
            return None
        max_score = max(self.scores.values())
        winners = [p for p, s in self.scores.items() if s == max_score]
        return winners[0]