

from core.models import Group, User, GroupMember
from django.db import IntegrityError
from django.db import transaction






def add_member(*, group: Group, user: User) -> GroupMember:
    try:
        return GroupMember.objects.create(
            group=group,
            user=user,
        )
    except IntegrityError:
        raise ValueError("User already a member of this group")
    


def create_group(*, created_by: User, members) -> Group:
    print(members)
    with transaction.atomic():
        group = Group.objects.create(created_by=created_by)
        for member in members:
            add_member(
                group=group,
                user=member
            )
    
    return group