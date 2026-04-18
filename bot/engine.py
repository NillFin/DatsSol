import asyncio
import time
from bot.api import GameAPI
from bot.game_state import GameState
from bot.strategy import Strategy
import keyboard

class GameEngine:
    def __init__(self):
        self.api = GameAPI()
        self.strategy = Strategy()
        self.listeners = []
        self.round_info = None
        self.last_command_turn = None
        self.last_round_fetch = 0
        self.start_input_listener()

    def handle_input(self, user_input):
        user_input = user_input.lower().strip()

        key_map = {
            "w": "up",
            "s": "down",
            "a": "left",
            "d": "right"
        }

        direction = key_map.get(user_input)

        if direction:
            print("📥 Input:", direction)
            self.strategy.pending_direction = direction

    def start_input_listener(self):
        def on_key(event):
            key_map = {
                "w": "up",
                "s": "down",
                "a": "left",
                "d": "right"
            }

            if event.name in key_map:
                direction = key_map[event.name]
                print("📥 Input:", direction)
                if direction:
                    self.strategy.pending_direction = direction


        keyboard.on_press(on_key)

    def register_listener(self, callback):
        self.listeners.append(callback)

    async def notify(self, state):
        for callback in self.listeners:
            await callback(state)

    async def run(self):
        while True:
            try:
                # обновляем инфу о раундах раз в 30 секунд
                if time.time() - self.last_round_fetch > 30:
                    self.round_info = self.api.get_round_info()
                    self.last_round_fetch = time.time()

                raw = self.api.get_arena()
                state = GameState(raw)

                if self.last_command_turn != state.turn:
                    relocate = self.strategy.decide_relocation(state)
                    actions = self.strategy.decide_actions(state)
                    upgrade = self.strategy.choose_upgrade(state)


                    if actions or upgrade or relocate:
                        response = self.api.send_command(
                            command=actions,
                            upgrade=upgrade,
                            relocate=relocate
                        )
                        print("Command response:", response)

                    self.last_command_turn = state.turn

                # ✅ Найдём активный раунд
                active_round = None
                if self.round_info and "rounds" in self.round_info:
                    active_round = next(
                        (r for r in self.round_info["rounds"] if r.get("status") == "active"),
                        None
                    )
                    # если нет активного — возьмём последний
                    if not active_round and self.round_info["rounds"]:
                        active_round = self.round_info["rounds"][-1]

                raw["roundInfo"] = active_round

                await self.notify(raw)

                await asyncio.sleep(max(0.3, state.next_turn_in - 0.1))

            except Exception as e:
                print("Engine error:", e)
                await asyncio.sleep(1)