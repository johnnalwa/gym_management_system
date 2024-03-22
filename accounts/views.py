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
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render, get_object_or_404



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
    success_message = None  # Initialize a variable to store the success message
    if request.method == 'POST':
        form = OnDemandWorkoutForm(request.POST)
        if form.is_valid():
            form.instance.instructor = request.user
            form.save()
            success_message = 'Workout created successfully.'
            # Optionally, you can also use Django's messages framework here
            # messages.success(request, 'Workout created successfully.')
            # return redirect('workout_list')
    else:
        form = OnDemandWorkoutForm()
    return render(request, 'trainers/create_workout.html', {'form': form, 'success_message': success_message})




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