import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.services.user_service import create_user
from core.services.grp_service import create_group, add_member
from core.models import User, GroupMember, Group, Expense,ExpenseSplit,Balance
from core.services.expense_service import add_shared_expense
from core.services.payment_services import record_settlement
from core.services.balance_services import simplify_balances
from decimal import Decimal

def get_all(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    users = User.objects.all().values("id", "email")
    return JsonResponse(list(users), safe=False)

@csrf_exempt
def create_user_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.loads(request.body)

    user = create_user(
        name=data["name"],
        email=data.get("email"),
        password=data.get("password"),
    )

    return JsonResponse(
        {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at,
        },
        status=201,
    )


@csrf_exempt
def create_grp_api(request):
    if request.method != "POST":
        return JsonResponse({"error":"Method not allowed"}, status=400)
    
    data = json.loads(request.body)
    member_ids = set(data["member_ids"])
    print(member_ids)

    try:
        user = User.objects.get(id=data["user_id"])
        member_ids.add(str(user.id))
        print("...",member_ids)
        members = User.objects.filter(id__in=member_ids)

    except User.DoesNotExist:
        return JsonResponse({"error": "Some User error occured"}, status=404)
    

    if members.count() != len(data["member_ids"])+1:
        return JsonResponse({"error": "Invalid member IDs"}, status=404)


    
    group = create_group(created_by=user,members=members)
    print(group)

    
    return JsonResponse(
        {
            "id": str(group.id),
            "created_by": str(group.created_by.id),
            "created_at": group.created_at,
        },
        status=201,
    )


@csrf_exempt
def add_group_member_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.loads(request.body)

    try:
        group = Group.objects.get(id=data["group_id"])
        user = User.objects.get(id=data["user_id"])
    except (Group.DoesNotExist, User.DoesNotExist):
        return JsonResponse({"error": "Group or User not found"}, status=404)

    try:
        membership = add_member(group=group, user=user)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse(
        {
            "group_id": str(membership.group.id),
            "user_id": str(membership.user.id),
            "joined_at": membership.joined_at,
        },
        status=201,
    )




@csrf_exempt
def add_expense(request, group_id):
    print("eeeeeeeeeeeeeee")
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.loads(request.body)

    try:
        expense = add_shared_expense(
            group=Group.objects.get(id=group_id),
            paid_by=User.objects.get(id=data["paid_by"]),
            amount=Decimal(data["amount"]),
            description=data["description"],
            split_type=data["split_type"],
            splits=data["splits"],
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse(
        {
            "expense_id": str(expense.id),
            "status": "created",
        },
        status=201,
    )
def get_group_balances(request, group_id):
    print("dfsdsdsd")
    balances = Balance.objects.filter(group_id=group_id)

    return JsonResponse(
        {
            "balances": [
                {
                    "user_id": str(b.user.id),
                    "balance": str(b.balance)
                }
                for b in balances
            ]
        }
    )
@csrf_exempt
def record_settlement_api(request, group_id):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)

        group = Group.objects.get(id=group_id)
        paid_by = User.objects.get(id=data["paid_by"])
        paid_to = User.objects.get(id=data["paid_to"])
        amount = Decimal(data["amount"])

        if amount <= 0:
            return JsonResponse(
                {"error": "Amount must be positive"},
                status=400
            )

        record_settlement(
            group=group,
            paid_by=paid_by,
            paid_to=paid_to,
            amount=amount,
        )

    except Group.DoesNotExist:
        return JsonResponse(
            {"error": "Group not found"},
            status=404
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid user"},
            status=400
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=400
        )

    return JsonResponse(
        {"message": "Settlement recorded successfully"},
        status=201
    )


def group_debts_api(request, group_id):
    balances = Balance.objects.filter(group_id=group_id)

    data = [
        {
            "user_id": str(b.user_id),
            "balance": b.balance
        }
        for b in balances
        if b.balance != 0
    ]

    simplified = simplify_balances(data)

    return JsonResponse({
        "debts": simplified
    })


def user_summary_api(request, group_id, user_id):
    balances = Balance.objects.filter(group_id=group_id)

    data = [
        {
            "user_id": str(b.user_id),
            "balance": b.balance
        }
        for b in balances
        if b.balance != 0
    ]

    settlements = simplify_balances(data)

    owes = []
    owed_to_me = []

    for s in settlements:
        if s["from"] == user_id:
            owes.append({
                "to": s["to"],
                "amount": s["amount"]
            })
        elif s["to"] == user_id:
            owed_to_me.append({
                "from": s["from"],
                "amount": s["amount"]
            })

    return JsonResponse({
        "user_id": user_id,
        "you_owe": owes,
        "others_owe_you": owed_to_me
    })
