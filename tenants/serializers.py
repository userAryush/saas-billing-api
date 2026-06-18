from rest_framework import serializers
from .models import Organisation, Membership
from django.utils.text import slugify
import uuid


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['id','name']
        
    def create(self, validated_data):
        user = self.context['request'].user
        org = Organisation.objects.create(**validated_data,slug=slugify(validated_data['name']) + '-' + str(uuid.uuid4())[:8])
        Membership.objects.create(user=user, org=org, role='owner')

        return org



class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['id', 'user', 'org', 'role']
        extra_kwargs = {'role': {'read_only': True}}

class InviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=Membership.ROLE_CHOICES, default='member')
        