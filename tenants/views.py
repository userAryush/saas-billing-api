from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from .serializers import OrganisationSerializer, MembershipSerializer, InviteSerializer
from .models import Organisation, Membership
from accounts.models import User
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
# Create your views here.


class OrganisationCreateView(CreateAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer

def get_current_organisation(user):
    membership = Membership.objects.filter(user=user, role='owner').first()
    return membership.org if membership else None

    
class OrganisationMeView(RetrieveAPIView):
    serializer_class = OrganisationSerializer

    def get_object(self):
        org = get_current_organisation(self.request.user)
        if org is None:
            
            raise NotFound("You don't belong to any organisation.")
        return org
        


class InviteMemberView(CreateAPIView):
    serializer_class = InviteSerializer

    def perform_create(self, serializer):
        org = get_current_organisation(self.request.user)

        # Requesting user must be owner or admin in this org.
        requester_membership = Membership.objects.filter(org=org, user=self.request.user).first()
        
        if requester_membership is None or requester_membership.role not in ("owner", "admin"):
            raise PermissionDenied("Only owners or admins can invite members.")

        # Org must not have hit its member cap.
        if Membership.objects.filter(org=org).count() >= org.subscription.plan.max_members:
            raise ValidationError("This organisation has reached its maximum number of members.")

        email = serializer.validated_data["email"]
        invited_user, created = User.objects.get_or_create(
            email=email,
            defaults={"full_name": "", "is_active": False}, 
        )

        # Don't create a duplicate membership.
        if Membership.objects.filter(org=org, user=invited_user).exists():
            raise ValidationError("This user is already a member of the organisation.")

        # Create the membership.
        role = serializer.validated_data.get("role", "member")
        Membership.objects.create(org=org, user=invited_user, role=role)


class OrganisationMembersView(ListAPIView):
    serializer_class = MembershipSerializer

    def get_queryset(self):
        return Membership.objects.filter(
            org=get_current_organisation(self.request.user)
        )