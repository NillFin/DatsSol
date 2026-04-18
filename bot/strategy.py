from copy import deepcopy


class Strategy:

    def __init__(self):
        self.pending_direction = None
        self.new_main = None
        self.vision_range_count = 0
        self.repair_power_count = 0
        self.signal_range_count = 0
        self.focus_target = None
        self.decay_mitigation_count = 0

    def choose_upgrade(self, state):
        """
        Возвращает название апгрейда или None
        """
        # TODO: продвинутая логика выбора
        if state.upgrades.get("points", 0) > 0:
            if self.signal_range_count < 10:
                self.signal_range_count += 1
                return "signal_range"

            elif self.vision_range_count < 5:
                self.vision_range_count += 1
                return "vision_range"
            elif self.repair_power_count < 5:
                self.repair_power_count += 1
                return "repair_power"
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
        if terra_status < 40:
            return None
        # Ищем только ПРИЛЕГАЮЩИЕ плантации (без диагоналей)
        candidates = []
        for p in state.plantations:
            if not p["isMain"]:
                x, y = p["position"]
                # прилегание = манхэттенское расстояние 1
                if abs(x - x_main) + abs(y - y_main) == 1:
                    for cell in state.cells:
                        if cell["position"] == [x, y]:
                            prog = cell["terraformationProgress"]
                            if prog < terra_status: # есть смысл переезжать
                                candidates.append((prog, x, y))

        if candidates:
            candidates.sort(key=lambda t: t[0]) # самая свежая
            _, x, y = candidates[0]
            actions.extend([[x_main, y_main], [x, y]])
            self.new_main = [x, y]
            return actions

        return None

    def decide_actions(self, state):
        print(f"state: {state}")
        if self.new_main is None:
            for p in state.plantations:
                if p.get("isMain"):
                    self.new_main = p["position"]
                    break

        actions = []
        width, height = state.size

        x_main, y_main = self.new_main

        sr = 3 + self.signal_range_count
        ar = getattr(state, "actionRange", 2)

        occupied = set()
        for p in state.plantations:
            occupied.add(tuple(p["position"]))
        if hasattr(state, "enemy") and state.enemy:
            for e in state.enemy:
                occupied.add(tuple(e["position"]))
        if hasattr(state, "beavers") and state.beavers:
            for b in state.beavers:
                x = b["position"][0]
                y = b["position"][1]
                occupied.add((x, y))
                occupied.add((x-2, y-2))
                occupied.add((x - 2, y - 1))
                occupied.add((x - 2, y - 0))
                occupied.add((x - 2, y + 1))
                occupied.add((x - 2, y + 2))
                occupied.add((x - 1, y - 2))
                occupied.add((x - 1, y - 1))
                occupied.add((x - 1, y - 0))
                occupied.add((x - 1, y + 1))
                occupied.add((x - 1, y + 2))

                occupied.add((x, y - 2))
                occupied.add((x, y - 1))
                occupied.add((x, y - 0))
                occupied.add((x, y + 1))
                occupied.add((x, y + 2))

                occupied.add((x + 1, y - 2))
                occupied.add((x + 1, y - 1))
                occupied.add((x + 1, y - 0))
                occupied.add((x + 1, y + 1))
                occupied.add((x + 1, y + 2))

                occupied.add((x + 2, y - 2))
                occupied.add((x + 2, y - 1))
                occupied.add((x + 2, y - 0))
                occupied.add((x + 2, y + 1))
                occupied.add((x + 2, y + 2))
        if hasattr(state, "mountains") and state.mountains:
            for m in state.mountains:
                occupied.add(tuple(m))
        if hasattr(state, "cells") and state.cells:
            for c in state.cells:
                if c["terraformationProgress"] > 0:
                    occupied.add(tuple(c["position"]))

        occupied_except_constructions = deepcopy(occupied)

        constructions = set()
        if hasattr(state, "construction") and state.construction:
            for c in state.construction:
                pos = tuple(c["position"])
                constructions.add(pos)
                occupied.add(pos)

        # --- 1. исполнители в пределах SR от ЦУ ---
        available_executors = []
        for p in state.plantations:
            if p.get("isIsolated"):
                continue
            px, py = p["position"]
            # простая оценка SR по манхэттену (в игре SR считается по сети, но для выбора хватит)
            if abs(px - x_main) + abs(py - y_main) <= sr:  # +4 запас для сети
                available_executors.append((px, py))

        if not available_executors:
            return []
        primary_target = None

        # --- 2. выбираем ОДНУ следующую клетку для ЦУ ---
        if self.focus_target:
            tx, ty = self.focus_target
            if 0 <= tx < width and 0 <= ty < height and (tx, ty) not in occupied_except_constructions and abs(x_main - tx) + abs(y_main - ty) <= sr:
                primary_target = (tx, ty)
                # цель ещё свободна — оставляем

            # 2b. если старой нет или она занята — выбираем новую
        if not primary_target:
            # сначала 4 соседа ЦУ (как и раньше)
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                tx, ty = x_main + dx, y_main + dy
                if 0 <= tx < width and 0 <= ty < height and (tx, ty) not in occupied:
                    primary_target = (tx, ty)
                    break
            # если вокруг всё занято — ищем в радиусе 2-3
            if not primary_target:
                for r in range(2, 4):
                    for dx in range(-r, r + 1):
                        for dy in range(-r, r + 1):
                            if abs(dx) + abs(dy) != r: continue
                            tx, ty = x_main + dx, y_main + dy
                            if 0 <= tx < width and 0 <= ty < height and (tx, ty) not in occupied:
                                primary_target = (tx, ty);
                                break
                        if primary_target: break
                    if primary_target: break

            # сохраняем новую цель
            self.focus_target = list(primary_target) if primary_target else None

        if not primary_target:
            return []  # строить некуда

        # --- 3. ФОКУС: большая часть строит primary_target ---
        focus_count = max(1, int(len(available_executors)))
        # сортируем по близости к цели, чтобы не тратить дальних
        available_executors.sort(key=lambda e: abs(e[0] - primary_target[0]) + abs(e[1] - primary_target[1]))

        used = set()
        for i in range(min(focus_count, len(available_executors))):
            ex, ey = available_executors[i]
            # проверяем actionRange
            if abs(ex - primary_target[0]) <= ar and abs(ey - primary_target[1]) <= ar:
                actions.append({
                    "path": [[ex, ey], [ex, ey], [primary_target[0], primary_target[1]]]
                })
                used.add((ex, ey))

        # --- 4. КЛАСТЕР: остальные строят кучно вокруг primary_target ---
        remaining = [e for e in available_executors if e not in used]  # чтобы не дублировать одну и ту же вторичную цель

        # генерируем кольцо клеток вокруг primary_target
        cluster_cells = []
        for r in range(1, 4):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r: continue
                    tx, ty = primary_target[0] + dx, primary_target[1] + dy
                    if 0 <= tx < width and 0 <= ty < height and (tx, ty) not in occupied_except_constructions:
                        cluster_cells.append((tx, ty))
        # ближе к центру — в приоритете
        cluster_cells.sort(key=lambda c: abs(c[0] - primary_target[0]) + abs(c[1] - primary_target[1]))

        for ex, ey in remaining:
            for tx, ty in cluster_cells:
                if abs(ex - tx) <= ar and abs(ey - ty) <= ar:
                    actions.append({
                        "path": [[ex, ey], [ex, ey], [tx, ty]]
                    })
                    occupied.add((tx, ty))
                    break

        actions.reverse()  # как у тебя было
        print(f"actions: {actions}")
        print(f"focus target {primary_target}, executors {len(actions)}")
        return actions

