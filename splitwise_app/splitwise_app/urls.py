"""
URL configuration for splitwise_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import create_user_api, create_grp_api, add_group_member_api,get_all,add_expense,get_group_balances,record_settlement_api,simplify_balances,user_summary_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/all", get_all),
    path("api/users/", create_user_api),
    path("api/groups/", create_grp_api),
    path("api/groups/add-member/", add_group_member_api),
    path("api/groups/<uuid:group_id>/expenses/", add_expense),
    path("api/groups/<uuid:group_id>/balances/", get_group_balances,name="group-balances"),
    path("api/groups/<uuid:group_id>/settlements/",record_settlement_api,name="record-settlement"),
    path("/api/groups/<uuid:group_id>/debts/",simplify_balances),
    path("/api/groups/<uuid:group_id>/users/<uuid:group_id>/summary/",user_summary_api),







]
