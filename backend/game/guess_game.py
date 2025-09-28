import backend.api.endpoints.players as players

class GuessGame:
    """Manages the state and logic for a single instance of the Guess the Teammate game."""

    def __init__(self):
        self.guesses = []
        self.game_over = False
        self.winner = None
        self.options = {}

    async def start_new_game(self, user1_id: int, user2_id: int, options: dict = {}):
        """Starts a new game with two players."""
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.current_user_turn = user1_id
        self.current_player = await players.get_random_player(
            teams=options.get("teams") or None,
            start_year=options.get("start_year") or None,
            end_year=options.get("end_year") or None,
            game_types=options.get("game_types") or None,
        )
        self.guesses = []
        self.game_over = False
        self.winner = None
        self.options = options or {}

    def get_current_player_turn(self) -> int:
        return self.current_user_turn

    async def make_guess(self, guessing_player_id: int, guessed_player_id: int) -> dict:
        """
        Processes a player's guess.
        Returns the updated game state and whether the guess was correct.
        """
        if self.game_over:
            return {"error": "Game is over.", "game_over": True, "winner": self.winner}

        if guessing_player_id != self.current_user_turn:
            return {"error": "It's not your turn."}
        
        player_teammates = await players.get_player_teammates(
            player_id=self.current_player.id,
            teams=self.options.get("teams") or None,
            start_year=self.options.get("start_year") or None,
            end_year=self.options.get("end_year") or None,
            game_types=self.options.get("game_types") or None,
        )

        is_correct_guess = guessed_player_id in map(lambda p: p['id'], player_teammates)

        self.guesses.append({
            "guesser": guessing_player_id,
            "guessed": guessed_player_id,
            "correct": is_correct_guess
        })

        if is_correct_guess:
            self.current_player = await players.get_player_by_id(guessed_player_id)
            return {
                "message": f"Player {guessing_player_id} correctly guessed Player {guessed_player_id}! Game Over!",
                "game_over": False,
                "last_guess": self.guesses[-1],
                "current_player": self.current_player.id
            }
        else:
            # Switch turn
            self.current_user_turn = self.user2_id if guessing_player_id == self.user1_id else self.user1_id
            return {
                "message": f"Player {guessing_player_id} incorrectly guessed Player {guessed_player_id}! Try again!",
                "game_over": False,
                "last_guess": self.guesses[-1],
                "current_player": self.current_player.id
            }