import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.services.user_service import create_user
from core.services.grp_service import create_group, add_member
from core.models import User, GroupMember, Group


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


