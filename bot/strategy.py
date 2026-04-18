class Strategy:

    def __init__(self):
        self.pending_direction = None
        self.new_main = None
        self.vision_range_count = 0
        self.repair_power_count = 0
        self.signal_range_count = 0

    def choose_upgrade(self, state):
        """
        Возвращает название апгрейда или None
        """
        # TODO: продвинутая логика выбора
        if state.upgrades.get("points", 0) > 0:
            if self.vision_range_count < 5:
                self.vision_range_count += 1
                return "vision_range"
            elif self.repair_power_count < 5:
                self.repair_power_count += 1
                return "repair_power"
            elif self.signal_range_count < 5:
                self.signal_range_count += 1
                return "signal_range"
            else:
                return "beaver_damage_mitigation"

        return None

    def decide_relocation(self, state):
        actions = []

        x_main, y_main = -1, -1
        terra_status = -1
        for p in state.plantations:
            if p["isMain"]:
                x_main, y_main = p["position"]
                self.new_main = [x_main, y_main]
                break

        for cell in state.cells:
            if cell["position"] == [x_main, y_main]:
                terra_status = cell["terraformationProgress"]

        for p in state.plantations:
            if not p["isMain"]:
                x, y = p["position"]

                for cell in state.cells:
                    if cell["position"] == [x, y]:
                        if cell["terraformationProgress"] < terra_status:
                            actions.extend([[x_main, y_main], [x, y]])
                            self.new_main = [x, y]
                            return actions

        return None

    def decide_actions(self, state):
        x, y = self.new_main

        width, height = state.size

        # Карта направлений
        dir_map = {
            "up": (0, 1),
            "down": (0, -1),
            "left": (-1, 0),
            "right": (1, 0)
        }

        # ✅ Если уже есть стройка — продолжаем
        if state.construction:
            tx, ty = state.construction[0]["position"]

            return [{
                "path": [
                    [x, y],
                    [x, y],
                    [tx, ty]
                ]
            }]

        # ✅ Если есть сохранённое направление — строим туда
        if self.pending_direction in dir_map:
            dx, dy = dir_map[self.pending_direction]
            tx, ty = x + dx, y + dy

            occupied = {tuple(p["position"]) for p in state.plantations}

            if 0 <= tx < width and 0 <= ty < height and (tx, ty) not in occupied:
                print(f"✅ Building {self.pending_direction}: {tx, ty}")

                return [{
                    "path": [
                        [x, y],
                        [x, y],
                        [tx, ty]
                    ]
                }]

            else:
                self.pending_direction = None

        return []