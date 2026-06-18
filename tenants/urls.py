from django.urls import path
from .views import OrganisationCreateView, InviteMemberView, OrganisationMembersView
urlpatterns = [
    path('org-create/', OrganisationCreateView.as_view(), name='org_create'),
    path('org-invite/', InviteMemberView.as_view(), name='org_invite'),
    path('org-members/', OrganisationMembersView.as_view(), name='org_members'),
]
