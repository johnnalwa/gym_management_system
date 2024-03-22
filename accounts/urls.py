from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('',views.login, name="login"),
    path('login/', views.LoginView.as_view(), name="user_login"),
    #path('login/',views.user_login, name="user_login"),
    # path('logout/', auth_views.LogoutView.as_view(template_name="logout.html"), name="logout"),
    
    path('member/dashboard/',views.MemberDashboard, name="member_dashboard"),
    path('member/register/',views.RegisterMemberView.as_view(), name="register_member"),
    path('members/workouts/', views.workout_list, name='workout_list'),  # URL pattern for the workout_list view
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('class/<int:class_id>/', views.class_info, name='class_info'),
    path('schedule-appointment/<int:class_id>/', views.schedule_appointment, name='schedule_appointment'),
    path('appointments/<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),


    
  
    
    path('management/dashboard/',views.ManagementDashboard, name="management_dashboard"),
    path('management/register/',views.RegisterManagementView.as_view(), name="register_management"),
    path('management/workoutcreate/', views.create_workout, name='create_workout'),
    path('members/', views.member_list, name='member_list'),
    path('management/add-class/', views.add_class, name='add_class'),  # URL for the class creation form
    


]



    
    





