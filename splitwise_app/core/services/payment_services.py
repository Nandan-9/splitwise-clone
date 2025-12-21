from django.db import transaction
from django.db.models import F
from core.models import Settlement, Balance


def record_settlement(*, group, paid_by, paid_to, amount):
    with transaction.atomic():
        Settlement.objects.create(
            group=group,
            paid_by=paid_by,
            paid_to=paid_to,
            amount=amount
        )

        # Debtor pays → balance increases toward 0
        Balance.objects.filter(
            group=group,
            user=paid_by
        ).update(balance=F("balance") + amount)

        # Creditor receives → balance decreases toward 0
        Balance.objects.filter(
            group=group,
            user=paid_to
        ).update(balance=F("balance") - amount)
