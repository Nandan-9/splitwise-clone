from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from decimal import Decimal
from django.db.models import F

from core.models import Expense,ExpenseSplit,Group,User,Balance


def normalize_splits(
    *,
    split_type: str,
    amount: Decimal,
    splits: list[dict],
) -> list[dict]:

    if split_type == "EXACT":
        total = sum(Decimal(s["amount"]) for s in splits)
        if total != amount:
            raise ValueError("Exact splits must sum to total amount")

        return [
            {"user_id": s["user_id"], "amount": Decimal(s["amount"])}
            for s in splits
        ]

    elif split_type == "EQUAL":
        if not splits:
            raise ValueError("No users to split with")

        per_head = (amount / len(splits)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        return [
            {"user_id": s["user_id"], "amount": per_head}
            for s in splits
        ]

    elif split_type == "PERCENTAGE":
        total_percent = sum(Decimal(s["percentage"]) for s in splits)
        if total_percent != Decimal("100"):
            raise ValueError("Percentages must sum to 100")

        return [
            {
                "user_id": s["user_id"],
                "amount": (amount * Decimal(s["percentage"]) / 100).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
            }
            for s in splits
        ]

    else:
        raise ValueError(f"Unknown split type: {split_type}")


def add_shared_expense(
    *,
    group: Group,
    paid_by: User,
    amount: Decimal,
    description: str,
    split_type: str,
    splits: list[dict],
) -> Expense:
    
    
    user_ids_in_splits = {s["user_id"] for s in splits}

    if paid_by.id not in user_ids_in_splits:
        splits.append({"user_id": paid_by.id})

    normalized_splits = normalize_splits(
        split_type=split_type,
        amount=amount,
        splits=splits,
    )

    final_total = sum(s["amount"] for s in normalized_splits)
    if final_total != amount:
        raise ValueError("Final split total mismatch after normalization")

    with transaction.atomic():
        expense = Expense.objects.create(
            group=group,
            paid_by=paid_by,
            amount=amount,
            description=description,
        )

        ExpenseSplit.objects.bulk_create([
            ExpenseSplit(
                expense=expense,
                user_id=s["user_id"],
                amount=s["amount"],
            )
            for s in normalized_splits
        ])
        for s in normalized_splits:
            Balance.objects.filter(
                group=group,
                user_id=s["user_id"]
            ).update(balance=F("balance") - s["amount"])

        # 🔺 Payer gets credited full amount
        Balance.objects.filter(
            group=group,
            user=paid_by
        ).update(balance=F("balance") + amount)

    return expense
