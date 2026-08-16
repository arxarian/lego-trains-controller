# This Python file uses the following encoding: utf-8
"""Persisted per-train plans keyed by device.name.

Identity key is ``device.name`` (sim default: ``"Simulator"``; BLE: advertised hub name).
Attach matches on that key only. Kind (``sim`` / ``ble``) is stored for readability
and future multi-sim keys; it is not required to match on attach.

If two devices share a name, last writer wins.
"""

from __future__ import annotations

WAIT_TYPE_SECONDS = "seconds"
CONTROL_MANUAL = "manual"
CONTROL_AUTOMATIC = "automatic"
KIND_SIM = "sim"
KIND_BLE = "ble"


def plan_key_for_device(device) -> str:
    return device.name


def kind_for_device(device) -> str:
    from python.items.train_device_sim import TrainDeviceSim

    return KIND_SIM if isinstance(device, TrainDeviceSim) else KIND_BLE


def wait_to_json(seconds: float) -> dict:
    return {"type": WAIT_TYPE_SECONDS, "seconds": float(seconds)}


def wait_from_json(wait) -> tuple[float, str | None]:
    """Return (seconds, warning). Unknown or missing type is 0s wait."""
    if not isinstance(wait, dict):
        return 0.0, None

    wait_type = wait.get("type")
    if wait_type is None or wait_type == WAIT_TYPE_SECONDS:
        try:
            return float(wait.get("seconds", 0) or 0), None
        except (TypeError, ValueError):
            return 0.0, None

    return 0.0, f"Unknown wait type {wait_type!r}; using 0s"


def control_mode_to_json(mode) -> str:
    if int(mode) == 2:
        return CONTROL_AUTOMATIC
    return CONTROL_MANUAL


def control_mode_from_json(value) -> tuple[int, str | None]:
    if value == CONTROL_AUTOMATIC:
        return 2, None
    if value == CONTROL_MANUAL or value is None:
        return 1, None
    return 1, f"Unknown control_mode {value!r}; using manual"


def snapshot_train(train) -> dict:
    orders = []
    for index in range(train.orders.rowCount()):
        order = train.orders.get(index)
        orders.append({
            "target_node_id": order.target_node_id,
            "wait": wait_to_json(order.wait_seconds),
        })
    return {
        "key": plan_key_for_device(train.device),
        "kind": kind_for_device(train.device),
        "control_mode": control_mode_to_json(train.control_mode),
        "allow_reverse": bool(train.allow_reverse),
        "current_order_index": int(train.current_order_index),
        "orders": orders,
    }


def parse_plans(raw) -> dict[str, dict]:
    """Parse a ``trains`` JSON list into a dict keyed by plan key. Last writer wins."""
    plans: dict[str, dict] = {}
    if not isinstance(raw, list):
        return plans

    for item in raw:
        if not isinstance(item, dict):
            continue
        key = item.get("key")
        if not key:
            continue
        key = str(key)
        if key in plans:
            print(f"Train plan: duplicate key {key!r}; last writer wins")
        plans[key] = item
    return plans


def valid_orders(plan, node_ids) -> tuple[list[dict], list[str]]:
    """Keep orders whose target is in ``node_ids``. ``node_ids is None`` keeps all."""
    raw_orders = plan.get("orders") or []
    kept = []
    dropped = []
    node_set = None if node_ids is None else set(node_ids)

    for order in raw_orders:
        if not isinstance(order, dict):
            continue
        node_id = order.get("target_node_id")
        if not node_id:
            continue
        if node_set is not None and node_id not in node_set:
            dropped.append(node_id)
            continue
        kept.append(order)
    return kept, dropped
