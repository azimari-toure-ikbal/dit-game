class GameData:
    def __init__(self, ui):
        self.ui = ui
        self._score = 0
        self._health = 5
        self.ui.create_hearts(self.health)

        self.unlocked_levels = 3
        self.current_level = 0

    @property
    def health(self):
        return self._health
    
    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, value):
        self._score = value
        if self.score >= 500:
            self.score -= 500
            self.health += 1
        self.ui.update_score(self.score)


    @health.setter
    def health(self, value):
        self._health = value
        self.ui.create_hearts(value)