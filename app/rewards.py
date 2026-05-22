from typing import Optional
from app.config import REWARD_RULES


def calculate_points(
    txn_type: str,
    amount: float,
    category: Optional[str],
) -> tuple[int, float, str]:
    rule = REWARD_RULES.get(txn_type)
    if not rule:
        return 0, 1.0, "unknown_type"

    if txn_type == "referral":
        return rule["flat_points"], 1.0, "flat_bonus"

    if amount < rule["min_amount"]:
        return 0, 1.0, "below_minimum"

    base_rate  = rule["base_points_per_dollar"]
    multiplier = 1.0
    tier       = "standard"

    if category and category in rule.get("bonus_categories", {}):
        bonus      = rule["bonus_categories"][category]
        multiplier = bonus["multiplier"]
        tier       = category

    points = int(amount * base_rate * multiplier)
    return points, multiplier, tier


def build_reward_question(
    txn_type: str,
    amount: float,
    points: int,
    multiplier: float,
    tier: str,
    category: Optional[str] = None,
    merchant: Optional[str] = None,
) -> str:
    question = (
        f"A transaction just completed: {txn_type} of ${amount:.2f}"
        + (f" in the {category} category" if category else "")
        + (f" at {merchant}" if merchant else "")
        + f". The member earned {points} points"
        + (f" with a {multiplier}x {tier} multiplier" if multiplier > 1.0 else "")
        + ". Explain why in 2-3 friendly sentences, citing the relevant policy section."
    )
    return question