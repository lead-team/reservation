from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .serializers import MealSerializer,ShiftMealSerializer,ReservationSerializer,ShiftSerializer,FoodSerializer,CombinedMealShiftSerializer,CombinedFoodCreationSerializer,UserSerializer
from rest_framework.decorators import api_view,permission_classes
from .models import ShiftMeal,Meal,Reservation,Shift,Food,FoodType,DailyMeal
import jdatetime
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .swagger_helper import token
import json
from .permissions import IsUserOrReadOnly,IsSupervisorOrReadOnly,IsUserReservation
from django.core.mail import send_mail
from django.http import HttpResponse
import jdatetime
from kavenegar import *
from django.conf import settings


def ISO_to_gregorian(date:str):
    jalali_date = jdatetime.date.fromisoformat(date)
    gregorian_date = jalali_date.togregorian()  
    return gregorian_date



        

@swagger_auto_schema(
    method="POST",
    manual_parameters=[
        token
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'date': openapi.Schema(type=openapi.TYPE_STRING, description='YYYY-MM-DD'),
            'shift': openapi.Schema(type=openapi.TYPE_STRING, description='shift name (A,B,C,D)'),
            'food1-name': openapi.Schema(type=openapi.TYPE_STRING, description='food1 name'),
            'food2-name': openapi.Schema(type=openapi.TYPE_STRING, description='food2 name'),
            'food-type':openapi.Schema(type=openapi.TYPE_STRING, description="food type ['دسر','...']"),
            'daily-meal':openapi.Schema(type=openapi.TYPE_STRING, description='[ناهار , شام]'),

        }
    ),
    operation_description="to filter the shift meals",
    responses={
        200: ShiftMealSerializer(many=True)
    }

)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def filter_meals(request:Request):
    filters={}
    date = request.data.get('date')
    shift_name = request.data.get('shift')
    food=request.data.get('food-name')
    # food2_name=request.data.get('food2-name')
    food_type=request.data.get('food-type')
    daily_meal=request.data.get('daily-meal')
    if date:
        gregorian_date=ISO_to_gregorian(date)
        filters["date"]=gregorian_date
    if shift_name:
        filters["shift__shift_name"]=shift_name
    if food:
        filters["meal__food__name"]=food
    if food_type:
        filters["meal__food_type"]=food_type
    if daily_meal:
        filters["meal__daily_meal"]=daily_meal
    meals = ShiftMeal.objects.filter(**filters)
    # meals=ShiftMeal.objects.filter(shift__shift_name=shift_name)
    serialized=ShiftMealSerializer(meals,many=True)
    return Response(serialized.data,status=status.HTTP_200_OK)

@swagger_auto_schema(
        method='get',
        operation_description="get all reserved shift meals ever",
        manual_parameters=[
            token
        ],
        responses={
            200:ShiftMealSerializer(many=True)
        }       
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_all_reservations(requrest:Request):
    my_user=requrest.user
    shift_meals=ShiftMeal.objects.filter(reservations__user=my_user)
    serialized=ShiftMealSerializer(shift_meals,many=True)
    return Response(serialized.data)


@swagger_auto_schema(
        method="post",
        operation_description="create a new reservation",
        manual_parameters=[token],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "shift-meal-id":openapi.Schema(type=openapi.TYPE_INTEGER,description="the shift_meal_id you want to reserve")   
            }
        ),
        responses={
            201:ReservationSerializer(many=False),
            306:"{'error'':'already reserved'}",
            410:"{'error':'shift meal doesn't exist'}",
            406:"unacceptable"
        }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reserve_meal(request:Request):
    shift_meal_id:dict = request.data.get('shift-meal-id')
    try:
        shift_meal:ShiftMeal=ShiftMeal.objects.get(id=shift_meal_id)
        daily_meal=shift_meal.meal.daily_meal
        date=shift_meal.date
        now=jdatetime.date.today()
        days_diff=(date - now).days
        if ( days_diff< 0):
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        other_reservation=Reservation.objects.filter(shift_meal__date=date,user=request.user,shift_meal__meal__daily_meal=daily_meal)
        print(other_reservation.exists())
        has_reserve_on_day=other_reservation.exists()
        if has_reserve_on_day:
            print("in if")
            previous_reservation=other_reservation.first()
            previous_reservation.delete()
        reservation,created=Reservation.objects.get_or_create(shift_meal=shift_meal,user=request.user,date=now)
        if not created:
            return Response(data={"error":"you have already reserve this shift meal"},status=status.HTTP_306_RESERVED)
        serialized=ReservationSerializer(reservation,many=False)
        return Response(data=serialized.data,status=status.HTTP_201_CREATED)

    except ShiftMeal.DoesNotExist:
        return Response(data={"error":f"no shift meal with id {shift_meal_id}"},status=status.HTTP_410_GONE)
    
@swagger_auto_schema(
        method="DELETE",
        manual_parameters=[
            token,]
)
@api_view(['DELETE'])
@permission_classes([IsUserReservation])
def delete_reservation(request:Request,id:int):
    try:
        reservation=Reservation.objects.get(pk=id)
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Reservation.DoesNotExist:
        return Response(data={"error":f"no reservation with id {id}"},status=status.HTTP_406_NOT_ACCEPTABLE)
    
@swagger_auto_schema(
        method="GET",
        manual_parameters=[token],
        responses={
            200:ReservationSerializer(many=True)
        }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_pending_reservations(request:Request):
    now=jdatetime.datetime.today()
    reservations=Reservation.objects.filter(user=request.user,date__gte=now)
    serialized=ReservationSerializer(reservations,many=True)
    return Response(data=serialized.data,status=status.HTTP_200_OK)
    


    






class ShiftMealAPIView(APIView):
    permission_classes=[IsSupervisorOrReadOnly]

    @swagger_auto_schema(
            manual_parameters=[
                token,
                openapi.Parameter(
                    name="shift-name",
                    in_=openapi.IN_QUERY,
                    type=openapi.TYPE_STRING,
                    description="shift name (A,B,C,D)",
                    required=True
                ),
                openapi.Parameter(
                    name="date",
                    in_=openapi.IN_QUERY,
                    type=openapi.TYPE_STRING,
                    description="date with format : YYYY-MM-DD",
                    required=True
                ),
                openapi.Parameter(
                    name="meal-id",
                    type=openapi.TYPE_INTEGER,
                    in_=openapi.IN_QUERY,
                    description="meal id",
                    required=True
                ),

            ],
            operation_description="create a new shift meal",
            responses={
                400:json.dumps({"error": "shift or date or meal is required."}),
                201:ShiftMealSerializer(many=True),
                306:json.dumps({"error":"you have already create this shift meal"}),
                204:json.dumps({"error":f"there no existing meal or shift with these id's"})
            } 
    )


    def post(self,request:Request,*args,**kwargs):
        shift_name=request.data.get('shift-name')
        date=request.data.get('date')
        meal_id=request.data.get('meal-id') 
        if not shift_name or not date or not meal_id:
            return Response({"error": "shift or date or meal is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            shift,created=Shift.objects.get_or_create(shift_name=shift_name)
            meal=Meal.objects.get(id=meal_id)
            shift_meal,created=ShiftMeal.objects.get_or_create(shift=shift,date=ISO_to_gregorian(date),meal=meal)
            if not created:
                return Response(data={"error":"you have already create this shift meal"},status=status.HTTP_306_RESERVED)
            serialized=ShiftMealSerializer(shift_meal,many=False)
            return Response(data=serialized.data,status=status.HTTP_201_CREATED)
        except Meal.DoesNotExist:
            return Response(data={"error":f"there no existing meal with id {meal_id}"},status=status.HTTP_204_NO_CONTENT)
        except Shift.DoesNotExist:
            return Response(data={"error":f"there no existing shift with name {shift_name}"},status=status.HTTP_204_NO_CONTENT)
        
    @swagger_auto_schema(
            operation_description="get needed fields for shiftmeal creation form",

            manual_parameters=[token],
            responses={
                200:CombinedMealShiftSerializer
            }
    )
    
    def get(self,request,*args,**kwargs):
        meals=Meal.objects.all()
        meal_serialized=MealSerializer(meals,many=True)
        shifts=Shift.objects.all()
        shift_serialized=ShiftSerializer(shifts,many=True)
        return Response(data={"meals":meal_serialized.data,"shifts":shift_serialized.data},status=status.HTTP_200_OK)
    

class MealAPIView(APIView):

    permission_classes=[IsSupervisorOrReadOnly]
    @swagger_auto_schema(
            operation_description="create a new meal",
            manual_parameters=[
                token,
                openapi.Parameter(
                    name="food1-id",
                    in_=openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    required=True
                ),
                openapi.Parameter(
                    name="food2-id",
                    in_=openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    required=True
                ),
                openapi.Parameter(
                    name="daily-meal",
                    in_=openapi.IN_QUERY,
                    type=openapi.TYPE_STRING,
                    required=True
                ),
                openapi.Parameter(
                    name="diet-id",
                    in_=openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    required=False
                ),
                openapi.Parameter(
                    name="dessert-id",
                    in_=openapi.IN_QUERY,
                    type=openapi.TYPE_INTEGER,
                    required=False
                ),

            ],
            responses={
                400:json.dumps({"error": "food-name or food-type or daily-meal is required."}),
                201:MealSerializer(many=False),
                306:json.dumps({"error":f"you have already create this meal and it's id is <meal id>"})
            }
    )
    def post(self,request:Request,*args,**kwargs):
        food1_id=request.data.get('food1-id')
        food2_id=request.data.get('food2-id')
        # food_type=request.data.get('food-type')
        daily_meal=request.data.get('daily-meal')
        diet_id=request.data.get('diet-id')
        dessert_id=request.data.get('dessert-id')
        if not food1_id or not food2_id  or not daily_meal:
            return Response({"error": "food-name or food-type or daily-meal is required."}, status=status.HTTP_400_BAD_REQUEST)
        food1=Food.objects.get(id=food1_id)
        food2=Food.objects.get(id=food2_id)
        meal,created=Meal.objects.get_or_create(food1=food1,food2=food2,diet__id=diet_id,dessert__id=dessert_id,daily_meal=daily_meal)
        if not created:
            return Response(data={"error":f"you have already create this meal and its id is {meal.id}"},status=status.HTTP_306_RESERVED)
        serialized=MealSerializer(meal,many=False)
        return Response(serialized.data,status=status.HTTP_201_CREATED)
        

    @swagger_auto_schema(
            operation_description="get fields required for meal creation form",
            manual_parameters=[token],
            responses={
                200:CombinedFoodCreationSerializer
            }
    )
    def get(self,request:Request,*args,**kwargs):
        foods=Food.objects.all()
        food_types=[food_type.label for food_type in FoodType]
        daily_meals=[daily_meal.label for daily_meal in DailyMeal]
        foods_serialized=FoodSerializer(foods,many=True)
        return Response(data={
            "foods":foods_serialized.data,
            "food_types":food_types,
            "daily_meals":daily_meals  
        },status=status.HTTP_200_OK)
        # print(food_types)


class ProfileAPIView(APIView):
    permission_classes=[IsUserOrReadOnly]
    @swagger_auto_schema(
            operation_description="get profile details",
            manual_parameters=[token],
            responses={
                200:UserSerializer
            }
    )
    def get(self,request:Request,*args,**kwargs):
        user=request.user
        serialized=UserSerializer(user,many=False)
        return Response(data=serialized.data,status=status.HTTP_200_OK)
    

    @swagger_auto_schema(
            operation_description="update profile details",
            manual_parameters=[token],
            request_body=UserSerializer,
            responses={
                200:UserSerializer,
                400:json.dumps({"error":"something"})
            }
    )
    def put(self,request:Request,*args,**kwargs):
        user=request.user
        user_data=request.data
        serializer=UserSerializer(user, data=user_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FoodAPIView(APIView):
    permission_classes=[IsSupervisorOrReadOnly]

    @swagger_auto_schema(
            manual_parameters=[token],
            responses={
                200:FoodSerializer(many=True),
                403:json.dumps({"error":"don't have permission"})
            },
            operation_description="get all foods"
    )
    def get(self,request:Request,*args,**kwargs):
        foods=Food.objects.all()
        serializer=FoodSerializer(foods,many=True)
        return Response(data=serializer.data,status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
            request_body=FoodSerializer(many=False),
            responses={
                201:FoodSerializer(many=False),
                400:json.dumps({"error":"something"}),
                403:json.dumps({"error":"don't have permission"})
            }
    )
    
    def post(self,request:Request,*args,**kwargs):
        serializer=FoodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

def send_test_email(request):
    try:
        send_mail(
            'Test Email',
            'This is a test email.',
            'erfank20041382@gmail.com',
            ['amir7007.sed@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse("Test email sent.")
    except Exception as e:
        return HttpResponse(f"Failed to send email: {str(e)}")
    

def send_sms(request:Request):
    api = KavenegarAPI('4F6763536138714F4658476C764D534F6F5A2B48614F463173763364636670796B2B6F502B4371437473383D')
    params = { 'sender' : '1000689696', 'receptor': '09335658101', 'message' :'.وب سرویس پیام کوتاه کاوه نگار' }
    response = api.sms_send( params)
    return Response(status=response.status)
    





    



    







