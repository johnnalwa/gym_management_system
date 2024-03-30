from xml.etree.ElementTree import tostring
from django.shortcuts import render
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from .models import *
from .forms import *
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .decorators import *
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render, get_object_or_404
from .forms import EquipmentForm

def create_equipment(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_equipment')  # Redirect to a success page
    else:
        form = EquipmentForm()
    return render(request, 'members/equipment_form.html', {'form': form})



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