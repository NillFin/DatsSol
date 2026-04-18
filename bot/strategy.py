class Strategy:

    def __init__(self):
        pass

    def choose_upgrade(self, state):
        """
        Возвращает название апгрейда или None
        """
        # TODO: продвинутая логика выбора
        if state.upgrades.get("points", 0) > 0:
            return "repair_power"
        return None

    def decide_relocation(self, state): 
        """ 
        Возвращает путь переноса ЦУ или None 
        """ 
        # TODO: логика безопасности 
        actions = [] 
        print(state.plantations) 
        x, y, x_main, y_main = -1, -1, -1, -1 
        for p in state.plantations: 
            if p["isMain"]: 
                x_main, y_main = p["position"] 
            else: 
                x, y = p["position"] 
            if x != -1 and y != -1 and x_main != -1 and y_main != -1: 
                print(state.turnNo) 
                actions.append({"relocateMain": [[x_main, y_main], [x, y]]}) 
                return actions 
            else: 
                return None

    def decide_actions(self, state):

        print("---- NEW TURN ----")
        print("Turn:", state.turn)
        print("Map size:", state.size)
        print("Plantations:", state.plantations)
        print("Construction:", state.construction)

        main = next(p for p in state.plantations if p["isMain"])
        x, y = main["position"]

        width, height = state.size

        # ✅ Если уже есть стройка — продолжаем её
        if state.construction:
            print("⛔ Already building")
            tx, ty = state.construction[0]["position"]

            return [{
                "path": [
                    [x, y],
                    [x, y],
                    [tx, ty]
                ]
            }]

        # ✅ Иначе начинаем новую
        candidates = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

        occupied = {tuple(p["position"]) for p in state.plantations}

        for tx, ty in candidates:
            if 0 <= tx < width and 0 <= ty < height and (tx, ty) not in occupied:
                print("✅ Building at:", tx, ty)
                return [{
                    "path": [
                        [x, y],
                        [x, y],
                        [tx, ty]
                    ]
                }]

        return []