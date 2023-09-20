import uuid
from rest_framework import serializers
from rest_framework.response import Response
from applications.bilets.utils import send_order_email
from applications.bilets.models import *


class LikeSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Like
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Favorite
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Comment
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Rating
        fields = ('rating',)


class TicketSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['like_count'] = instance.likes.filter(is_like=True).count()

        rating_result = 0
        for rating in instance.ratings.all():
            rating_result += rating.rating

        if rating_result:
            rep['rating'] = rating_result / instance.ratings.all().count()
        else:
            rep['rating'] = 0

        return rep


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('ticket', 'name', 'phone_number', 'created_at')

    def create(self, validated_data):
        request = self.context.get('request')
        instance = super().create(validated_data)
        instance.create_activation_code()

        send_order_email(request.user.email, instance.activation_code, request.user.name)
        return instance
        # return Response('Отлично, Мы отправили вам на почту подверждение покупки')

