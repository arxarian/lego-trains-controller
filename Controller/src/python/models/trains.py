from __future__ import annotations

from PySide6.QtCore import Property, Signal, Slot

from python.models.object_based_model import ObjectBasedModel
from python.items.train import Train
from python.train_plan import snapshot_train, valid_orders


class Trains(ObjectBasedModel[Train]):

    _item_class = Train

    def __init__(self, network, train_devices, planner=None, parent=None):
        super().__init__(parent)
        self._network = network
        self._planner = planner
        self._project = None
        self._last_order_hint = ""
        train_devices.device_connected.connect(self.add_train)
        network.marker_node_ids_changed.connect(self._drop_stale_orders)

    def set_project(self, project):
        self._project = project
        for train in self._items:
            self._apply_stored_plan(train)

    def add_train(self, device):
        train = Train(device=device, network=self._network, planner=self._planner, parent=self)
        device.disconnected.connect(lambda d: self.remove_by_device(d))
        self.append(train)
        self._apply_stored_plan(train)
        return train

    def remove_by_device(self, device):
        train = next((t for t in self._items if t.device == device), None)
        if train is None:
            print(f"cannot remove train {train}, not in the list")
            return

        self._sync_train(train)
        self.remove(train)

    def sync_live_into_project(self, project=None):
        project = project if project is not None else self._project
        if project is None:
            return

        seen = set()
        for train in self._items:
            key = train.device.name
            if key in seen:
                self._set_last_order_hint(f"Duplicate train key {key!r}; last writer wins")
            seen.add(key)
            project.upsert_train_plan(snapshot_train(train))

    def last_order_hint(self):
        return self._last_order_hint

    last_order_hint_changed = Signal()
    last_order_hint = Property(str, last_order_hint, notify=last_order_hint_changed)

    def _set_last_order_hint(self, message: str):
        print(f"Trains: {message}")
        if self._last_order_hint == message:
            return
        self._last_order_hint = message
        self.last_order_hint_changed.emit()

    def _sync_train(self, train):
        if self._project is None:
            return
        self._project.upsert_train_plan(snapshot_train(train))

    def _valid_node_ids(self):
        graph = self._network.graph()
        if graph is None:
            return None
        return list(graph.nodes)

    def _apply_stored_plan(self, train):
        if self._project is None:
            return

        plan = self._project.train_plan_for(train.device.name)
        warnings = []
        dropped = train.apply_plan(plan, valid_node_ids=self._valid_node_ids(), warnings=warnings)
        if dropped:
            self._hint_dropped(dropped)
            self._sync_train(train)
        elif warnings:
            self._set_last_order_hint(warnings[0])

    def _hint_dropped(self, dropped):
        unique = list(dict.fromkeys(dropped))
        noun = "stop" if len(unique) == 1 else "stops"
        self._set_last_order_hint(f"Dropped {len(unique)} stale {noun}: {', '.join(unique)}")

    def _drop_stale_orders(self):
        node_ids = self._valid_node_ids()
        if node_ids is None:
            return

        all_dropped = []
        live_keys = set()
        for train in self._items:
            live_keys.add(train.device.name)
            dropped = train.drop_stale_orders(node_ids)
            if dropped:
                all_dropped.extend(dropped)
                self._sync_train(train)

        if self._project is not None:
            for plan in list(self._project.train_plans()):
                key = plan.get("key")
                if key in live_keys:
                    continue
                kept, dropped = valid_orders(plan, node_ids)
                if not dropped:
                    continue
                all_dropped.extend(dropped)
                updated = dict(plan)
                updated["orders"] = kept
                index = int(updated.get("current_order_index") or 0)
                if kept:
                    updated["current_order_index"] = min(index, len(kept) - 1)
                else:
                    updated["current_order_index"] = 0
                self._project.upsert_train_plan(updated)

        if all_dropped:
            self._hint_dropped(all_dropped)

    @Slot(int, int, str, int, result=bool)
    def add_order_for_marker(self, train_index: int, rail_id: int, path_id: str, distance: int) -> bool:
        train = self.get(train_index)
        if train is None:
            self._set_last_order_hint("No planning-target train")
            return False

        node_id = self._network.node_id_for_marker(rail_id, path_id, distance)
        if not node_id:
            if not self._network.has_graph:
                self._set_last_order_hint("No graph")
            else:
                self._set_last_order_hint("Marker is not a graph node")
            return False

        train.add_order(node_id, 0.0)
        self._set_last_order_hint(f"Added order {node_id}")
        return True
