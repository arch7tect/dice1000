import random


class Player:
    name: str
    score: int = 0
    bolts: int = 0
    barrels: int = 0
    moves: int = 0
    in_pit200 = False
    in_pit600 = False
    on_barrel = False
    is_opened = False

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "%s - %s" % (self.name, self.score_img())

    def score_img(self) -> str:
        return "%s%s%d" % ("*" * self.bolts, "!" * self.barrels, self.score)


class Registry:
    def __init__(self, players: [Player]):
        self.players = players

    def can_stop_to_roll(self, player: Player, score: int):
        new_score = player.score + score
        if player.on_barrel and new_score < 1000:
            print("Player %s is on barrel. Need to roll again" % player.name)
            return False
        if player.in_pit600 and new_score < 700:
            print("Player %s is in pit 600-700. Need to roll again" % player.name)
            return False
        if player.in_pit200 and new_score < 300:
            print("Player %s is in pit 200-300. Need to roll again" % player.name)
            return False
        if not player.is_opened and new_score < 50:
            print("Player %s is not opened. Need to roll again" % player.name)
            return False
        return True

    def check_exceptions(self, player: Player):
        if player.score >= 1000:
            return
        if player.score >= 880:
            if not player.on_barrel:
                player.barrels += 1
            player.on_barrel = True
            player.score = 880
            print("Player %s is on barrel %d times" % (player.name, player.barrels))
        if player.in_pit600 and (700 <= player.score or player.score < 600):
            player.in_pit600 = False
            print("Player %s is out of pit 600-700" % player.name)
        if 600 <= player.score < 700:
            if not player.in_pit600:
                player.in_pit600 = True
                print("Player %s is in pit 600-700" % player.name)
        if player.in_pit200 and (300 <= player.score or player.score < 200):
            player.in_pit200 = False
            print("Player %s is out of pit 200-300" % player.name)
        if 200 <= player.score < 300:
            if not player.in_pit200:
                player.in_pit200 = True
                print("Player %s is in pit 200-300" % player.name)
        if not player.is_opened and player.score >= 50:
            player.is_opened = True
            print("Player %s is opened" % player.name)
        if player.score == 555:
            player.score = 0
            print("Player %s is in dump (555). Zeroing score" % player.name)

    def penalty(self, player: Player):
        if player.bolts >= 2:
            print("Player %s 3 bolt" % player.name)
            if player.on_barrel:
                player.on_barrel = False
                if player.barrels >= 3:
                    print("Player %s 3 barrel failed. Zeroing score" % player.name)
                    player.barrels = 0
                    player.score = 0
                else:
                    print("Player %s leave the barrel. Reduce score by 100" % player.name)
                    player.score -= 100
            else:
                print("Player %s failed. Reduce score by 100" % player.name)
                player.score -= 100
            player.bolts = 0
        else:
            player.bolts += 1
            print("Player %s %d bolt" % (player.name, player.bolts))
        if player.score < 0:
            player.score = 0
        self.check_exceptions(player)

    def update_score(self, player: Player, score: int):
        if player.in_pit600 and player.score + score < 700:
            print("Player %s is in pit 600-700. Haven't jumped out." % player.name)
            self.penalty(player)
            return False
        if player.in_pit200 and player.score + score < 300:
            print("Player %s is in pit 200-300. Haven't jumped out." % player.name)
            self.penalty(player)
            return False
        if not player.is_opened and player.score + score < 50:
            print("Player %s haven't opened." % player.name)
            self.penalty(player)
            return False
        player.bolts = 0
        if not player.on_barrel and 880 <= player.score + score < 1000:
            print("Player %s is on barrel." % player.name)
            player.score = 880
            player.barrels += 1
            player.on_barrel = True
            return False
        player.score += score
        self.check_exceptions(player)
        return player.score >= 1000


class Strategy:
    def roll_the_dices(self, registry: Registry, player: Player, dices_score: int, remain_dices: int) -> bool:
        raise NotImplementedError()


class Game:
    def __init__(self):
        self.registry = None
        self.strategies = {}
        self.players = []
        self.game_over = False

    def add_player(self, name: str, strategy: Strategy):
        player = Player(name)
        self.players.append(player)
        self.strategies[player.name] = strategy

    def roll_the_dices(self, n_dices):
        confirmed_score = 0
        confirmed = False
        while not confirmed:
            dices = [random.randint(1, 6) for _ in range(0, n_dices)]
            print("Roll %d dices: %s" % (n_dices, dices))
            counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            for dice in dices:
                counts[dice] += 1
            factors = [1, 2, 10, 20, 100]
            score = 0
            for i in range(1, 6 + 1):
                count = counts[i]
                if count > 0 and (i in [1, 5] or count >= 3):
                    nominal = i == 1 and 10 or i
                    score += nominal * factors[count - 1]
                    dices = [d for d in dices if d != i]
            n_dices = len(dices)
            if score == 0:
                confirmed_score = 0
                break
            else:
                confirmed_score += score
            print("Score: %d, remains: %d" % (score, n_dices))
            if n_dices == 0:
                print("Confirmation required")
                input("Press Enter")
                n_dices = 5
            else:
                confirmed = True
        return confirmed_score, n_dices

    def run(self):
        self.registry = Registry(self.players)
        while not self.game_over:
            for p in self.players:
                s = self.strategies[p.name]
                p.moves += 1
                print("Player %s, move %d" % (p, p.moves))
                remain_dices = 5
                tot_score = 0
                while True:
                    score, remain_dices = self.roll_the_dices(remain_dices)
                    if score == 0:
                        print("Unsuccessful attempt")
                        tot_score = 0
                        break
                    tot_score += score
                    print("Total move score %d" % tot_score)
                    if not self.registry.can_stop_to_roll(p, tot_score):
                        input("Press Enter")
                        continue
                    if not s.roll_the_dices(self.registry, p, score, remain_dices):
                        break
                if tot_score > 0:
                    if self.registry.update_score(p, tot_score):
                        print("Player %s win the game with %d" % (p.name, p.score))
                        self.game_over = True
                        break
                else:
                    self.registry.penalty(p)
                print("Move done %s\n" % p)
                input("Press Enter")


class TrivialStrategy(Strategy):
    def roll_the_dices(self, registry: Registry, player: Player, dices_score: int, remain_dices: int) -> bool:
        score = player.score + dices_score
        if score == 555:
            return True
        if score >= 1000 or \
                not player.is_opened and score >= 50 or \
                player.in_pit200 and score >= 300 or \
                player.in_pit600 and score >= 700 or \
                remain_dices < 3:
            print("Player %s stop rolling dices." % player.name)
            return False
        return True


class InteractiveStrategy(Strategy):
    def roll_the_dices(self, registry: Registry, player: Player, dices_score: int, remain_dices: int) -> bool:
        i = input("Roll again? y/[n]")
        return i.lower() == 'y'


def main():
    game = Game()
    game.add_player("Oleg", InteractiveStrategy())
    game.add_player("Computer", TrivialStrategy())
    game.run()


if __name__ == '__main__':
    main()
