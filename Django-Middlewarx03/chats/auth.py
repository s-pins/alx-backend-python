# messaging_app/chats/auth.py

# This file is reserved for potential custom JWT functionality, 
# such as a custom TokenObtainPairSerializer or a custom 
# authentication class if needed later.

# Example structure for custom claims (optional for this task, but good practice):
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # Add custom claims
#         token['username'] = user.username
#         # token['role'] = user.profile.role

#         return token