from rest_framework.serializers import ModelSerializer
from .models import Meal,ShiftMeal,Shift,Reservation,User,Food,FoodType,DailyMeal,Drink,User
from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
# from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class FoodSerializer(ModelSerializer):
    class Meta:
        model = Food
        fields="__all__"


class DrinkSerializer(ModelSerializer):
    class Meta:
        model = Drink
        fields=('name',)

class MealSerializer(ModelSerializer):
    food=FoodSerializer(many=False)
    diet=FoodSerializer(many=False)
    dessert=FoodSerializer(many=False)
    drinks=DrinkSerializer(many=True)
    class Meta:
        model = Meal
        fields=('id','food','diet','dessert','daily_meal','drinks')

    # def to_internal_value(self, data):
    #     # Convert ID fields to instances for internal use
    #     internal_value = super().to_internal_value(data)
    #     food_id = data.get('food')
    #     diet_id = data.get('diet')
    #     dessert_id = data.get('dessert')
    #     drink_ids = data.get('drinks', [])

    #     if food_id:
    #         internal_value['food'] = Food.objects.get(id=food_id)
    #     if diet_id:
    #         internal_value['diet'] = Food.objects.get(id=diet_id)
    #     if dessert_id:
    #         internal_value['dessert'] = Food.objects.get(id=dessert_id)
    #     if drink_ids:
    #         internal_value['drinks'] = Drink.objects.filter(id__in=drink_ids)

    #     return internal_value

    # def create(self, validated_data):
    #     drinks_data = validated_data.pop('drinks', [])
    #     meal = Meal.objects.create(**validated_data)
    #     meal.drinks.set(drinks_data)
    #     return meal

    # def to_representation(self, instance):
    #     # Use nested serializers for output
    #     representation = super().to_representation(instance)
    #     representation['food'] = FoodSerializer(instance.food).data
    #     representation['diet'] = FoodSerializer(instance.diet).data if instance.diet else None
    #     representation['dessert'] = FoodSerializer(instance.dessert).data if instance.dessert else None
    #     representation['drinks'] = DrinkSerializer(instance.drinks.all(), many=True).data
    #     return representation



class ShiftSerializer(ModelSerializer):
    class Meta:
        model = Shift
        fields="__all__"


class ShiftMealSerializer(ModelSerializer):
    meal=MealSerializer(many=False)
    shift=ShiftSerializer(many=False)
    is_reserved=serializers.SerializerMethodField()
    class Meta:
        model = ShiftMeal
        fields=('id','meal','shift','date','is_reserved')

    def get_is_reserved(self,obj:ShiftMeal):
        return Reservation.objects.filter(shift_meal=obj,user=self.context["request"].user).exists()

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields=('id','username','email','profile','is_supervisor',"is_shift_manager")
        ref_name="UserSerializer"


class ReservationSerializer(ModelSerializer):
    shift_meal=ShiftMealSerializer(many=False)
    user=UserSerializer(many=False)
    class Meta:
        model = Reservation
        fields=('id','user','shift_meal','date')

        def to_representation(self, instance:Reservation):
            # Get the representation of the reservation instance
            representation = super().to_representation(instance)
            
            # Re-serialize the shift_meal field with context
            shift_meal_serializer = ShiftMealSerializer(instance.shift_meal, context=self.context)
            representation['shift_meal'] = shift_meal_serializer.data
            
            return representation





    

class CombinedMealShiftSerializer(serializers.Serializer):
    meals = MealSerializer(many=True)
    shifts = ShiftMealSerializer(many=True)



class CombinedFoodCreationSerializer(serializers.Serializer):
    foods=FoodSerializer(many=True)
    food_types = serializers.ListField(
        child=serializers.CharField(), 
        default=[food_type.label for food_type in FoodType]
    )
    daily_meals = serializers.ListField(
        child=serializers.CharField(),
        default=[daily_meal.label for daily_meal in DailyMeal]
    )




class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError("This email address is not registered.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value):
        """
        Check if the email exists in the database.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is not registered.")
        return value

    def validate_new_password(self, value):
        """
        Check if the new password meets the criteria.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        # Add other password validations if needed (e.g., complexity, special characters)
        return value

    def validate(self, data):
        """
        Check if the code is correct for the provided email.
        """
        email = data.get('email')
        code = data.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or code.")

        if user.reset_code != code:
            raise serializers.ValidationError("Invalid email or code.")
        
        return data
    

class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model =Drink
        fields = "__all__"


class MealCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields =('food','drinks','dessert','diet','daily_meal')


    






