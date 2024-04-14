import base64
from datetime import datetime  
import json
from django.shortcuts import render
from django.shortcuts import redirect, render
from django.views.generic import CreateView
import requests
from .models import *
from .forms import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .decorators import *
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from .forms import EquipmentForm
import logging

logger = logging.getLogger(__name__)



def login(request):
    form = LoginForm
    context = {
        'form': form
    }
    return render(request, 'login.html', context)


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_member:
                return reverse('member_dashboard')
            elif user.is_management:
                return reverse('management_dashboard')
            else:
                return reverse('login')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)

class RegisterMemberView(CreateView):
    model = User
    form_class = MemberSignUpForm
    template_name = 'members/register.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'member'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        #login(self.request, user)
        return redirect('login')
  
    
class RegisterManagementView(CreateView):
    model = User
    form_class = ManagementSignUpForm
    template_name = 'trainers/register.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'management'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        #login(self.request, user)
        return redirect('login')
    

@login_required
@member_required
def MemberDashboard(request):
     # Fetch all gym classes from the database
    gym_classes = GymClass.objects.all()

    context = {
        'gym_classes': gym_classes
    }
    return render(request, 'members/dashboard.html', context)



@login_required
@management_required
def ManagementDashboard(request):
    # Fetch all gym classes from the database
    gym_classes = GymClass.objects.all()

    # Count the total number of gym classes
    total_classes = gym_classes.count()

    context = {
        'gym_classes': gym_classes,
        'total_classes': total_classes
    }
    return render(request, 'trainers/dashboard.html', context)


@login_required
@management_required

def create_workout(request):
    if request.method == 'POST':
        form = OnDemandWorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.instructor = request.user  # Associate currently logged-in user as instructor
            workout.save()
            messages.success(request, 'Workout created successfully.')
            # Redirect to workout list view after successful creation
    else:
        form = OnDemandWorkoutForm()
    return render(request, 'trainers/create_workout.html', {'form': form})


def workout_list(request):
    workouts = OnDemandWorkoutTable.objects.all()
    return render(request, 'members/workout_list.html', {'workouts': workouts})


def member_list(request):
    members = Member.objects.all()
    return render(request, 'trainers/member_list.html', {'members': members})





def add_class(request):
    if request.method == 'POST':
        form = GymClassForm(request.POST)
        if form.is_valid():
            gym_class = form.save()
            return JsonResponse({'success': True, 'message': 'Class added successfully!', 'class_id': gym_class.pk})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = GymClassForm()
    return render(request, 'trainers/add_class.html', {'form': form})


def class_info(request, class_id):
    gym_class = get_object_or_404(GymClass, id=class_id)
    return render(request, 'members/class_info.html', {'gym_class': gym_class})


def schedule_appointment(request, class_id):
    gym_class = get_object_or_404(GymClass, id=class_id)
    user = request.user  # Get the currently logged-in user

    # Create an appointment object and associate it with the user and gym class
    appointment = Appointment.objects.create(
        user=user,
        gym_class=gym_class,
        day=gym_class.day,
        time=gym_class.time   # Assuming gym_class has a 'time' field
    )

    # Optionally, you can add a success message
    messages.success(request, 'Appointment scheduled successfully!')

    return redirect('class_info', class_id=class_id)



def appointment_list(request):
    # Retrieve all appointments
    appointments = Appointment.objects.all()
    context = {'appointments': appointments}
    return render(request, 'members/appointment_list.html', context)


def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully!')
    
    # Retrieve all appointments after deletion
    appointments = Appointment.objects.all()
    
    return render(request, 'members/appointment_list.html', {'appointments': appointments})



def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            form.save()
            # Return success message as plain text
            return HttpResponse('Video uploaded successfully!')
    else:
        form = VideoForm()

    # Fetch all videos from the database
    videos = Video.objects.all()
    return render(request, 'trainers/upload_video.html', {'form': form, 'videos': videos})


def video_list(request):
    videos = Video.objects.all()
    return render(request, 'members/video_list.html', {'videos': videos})


def add_equipment(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment added successfully!')
            return JsonResponse({'success': True, 'message': 'Equipment added successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EquipmentForm()
        return render(request, 'trainers/add_equipment.html', {'form': form})
    


@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        try:
            # Extracting data from the request
            post_data = json.loads(request.body)
            telephone = post_data.get("phoneNumber")
            charged_amount = post_data.get("chargedAmount")
            class_name = request.POST.get('className')

            # Validate charged amount
            try:
                charged_amount = float(charged_amount)
                if charged_amount <= 0:
                    raise ValueError("Invalid amount")
            except (ValueError, TypeError):
                return JsonResponse({"success": False, "message": "Invalid amount"})

            # Save payment information to the database
            # Assuming you have a Payment model with a transaction_id field
            # Here, you'll need to replace 'transaction_id' with the actual name of your transaction_id field
            payment = Payment.objects.create(
                telephone=telephone,
                charged_amount=charged_amount,
                # transaction_id=None  # Initially set transaction_id to None
            )

            # M-PESA Credentials
            consumerKey = '4C3mkwwnUaq8AsSZ6ig0lGzEVrfNuLO9'
            consumerSecret = 'T9vB9MUhf8hRKocz'
            BusinessShortCode = '174379'
            Passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
            
            Timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            Password = base64.b64encode((BusinessShortCode + Passkey + Timestamp).encode()).decode('utf-8')
            
            access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            response = requests.get(access_token_url, auth=(consumerKey, consumerSecret))

            if response.status_code == 200:
                access_token = response.json().get("access_token")
                initiate_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                CallBackURL = 'https://35e4-197-248-229-71.ngrok-free.app/callback'

                payload = {
                    'BusinessShortCode': BusinessShortCode,
                    'Password': Password,
                    'Timestamp': Timestamp,
                    'TransactionType': 'CustomerPayBillOnline',
                    'Amount': charged_amount,
                    'PartyA': telephone,
                    'PartyB': BusinessShortCode,
                    'PhoneNumber': telephone,
                    'CallBackURL': CallBackURL,
                    'AccountReference': 'Gym Management System',
                    'TransactionDesc': f'Payment for {class_name} class',

                }

                response = requests.post(initiate_url, headers=headers, json=payload)
                response_data = response.json()  # Parse JSON response and store it in response_data variable

                if response.status_code == 200:
                    # Assuming the transaction_id is provided in the response
                    transaction_id = response_data.get('TransactionID')
                    payment.transaction_id = transaction_id
                    payment.save()  # Update the payment object with the transaction_id
                    success_message = response_data.get('ResponseDescription', 'Payment initiated successfully.')
                    return JsonResponse({"success": True, "message": success_message})
                else:
                    error_message = response_data.get('errorMessage', 'Failed to initiate payment.')
                    return JsonResponse({"success": False, "message": error_message})
            else:
                logger.error(f"Failed to get access token. Status code: {response.status_code}, Content: {response.content}")
                return JsonResponse({"success": False, "message": "Failed to get access token."})
        
        except Exception as e:
            logger.exception("Error occurred during payment initiation")
            return JsonResponse({"success": False, "message": "An error occurred during payment initiation. Please try again later."})




# @csrf_exempt
# def payment_callback(request):
#     if request.method == 'POST':
#         try:
#             # Parse the JSON data from the request body
#             callback_data = json.loads(request.body)

#             # Extract relevant information from the callback data
#             transaction_id = callback_data.get('TransactionID')
#             amount = callback_data.get('Amount')
#             status_code = callback_data.get('ResultCode')
#             status_description = callback_data.get('ResultDesc')

#             # Create a new Payment object with the received transaction ID
#             payment = Payment.objects.create(
#                 transaction_id=transaction_id,
#                 amount=amount,  # Assuming you have an 'amount' field in your Payment model
#                 status_code=status_code,
#                 status_description=status_description
#             )

#             # Return a success response to the payment gateway
#             return HttpResponse(status=200)

#         except Exception as e:
#             # Log any errors that occur during callback processing
#             print(f"Error processing payment callback: {str(e)}")
#             # Return an error response to the payment gateway
#             return HttpResponse(status=500)

#     else:
#         # Return an error response for unsupported request methods
#         return HttpResponse(status=405)




from django.shortcuts import render

def video_conference_room(request, room_name):
    return render(request, 'trainers/room.html', {
        'room_name': room_name
    })