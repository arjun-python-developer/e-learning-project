from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.custom_login, name='login'),
    path('teacher/register/', views.teacher_register, name='teacher_register'),
    path('student/register/', views.student_register, name='student_register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    path('manager/manage-users/', views.manage_users, name='manage_users'),
    path('manager/edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manager/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),


    path('add-course/', views.add_course, name='add_course'),
    path('edit-course/<int:course_id>/', views.edit_course, name='edit_course'),
    path("course/<int:course_id>/add_lesson/", views.add_lesson, name="add_lesson"),
    path("course/<int:course_id>/lessons/", views.view_lessons, name="view_lessons"),
    path("teacher/course/<int:course_id>/", views.teacher_course_detail, name="teacher_course_detail"),
    path('course/<int:course_id>/remove-student/<int:student_id>/', views.remove_student,name='remove_student'),





    path('courses/', views.available_courses, name='available_courses'),
    path('courses/enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path("student/course/<int:course_id>/lessons/", views.student_lessons, name="student_lessons"),





    path("teacher/course/<int:course_id>/", views.teacher_course_detail, name="teacher_course_detail"),
    path('course/<int:course_id>/remove-student/<int:student_id>/', views.remove_student,name='remove_student'),

    # NEW: application approve / reject
    path('course/<int:course_id>/applications/<int:application_id>/approve/',views.approve_enrollment, name='approve_enrollment'),
    path('course/<int:course_id>/applications/<int:application_id>/reject/',views.reject_enrollment, name='reject_enrollment'),
    path("my-applications/", views.my_applications, name="my_applications"),

    


    #Quiz
    path('course/<int:course_id>/quiz/add/', views.add_quiz, name='add_quiz'),
    path('quiz/<int:quiz_id>/questions/', views.manage_quiz, name='manage_quiz'),
    path('quiz/<int:quiz_id>/questions/add/', views.add_question, name='add_question'),
    path('question/<int:question_id>/choices/add/', views.add_choice, name='add_choice'),

    path("student/course/<int:course_id>/quiz/", views.student_quiz_list, name="student_quiz_list"),
    path("quiz/<int:quiz_id>/take/", views.take_quiz, name="take_quiz"),
    path('quiz/<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),

    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('choice/<int:choice_id>/delete/', views.delete_choice, name='delete_choice'),




    path('approve-teacher/<int:user_id>/', views.approve_teacher, name='approve_teacher'),
    path('reject-teacher/<int:user_id>/', views.reject_teacher, name='reject_teacher'),
    path('manager/application/<int:id>/approve/', views.manager_approve, name='manager_approve'),
    path('manager/application/<int:id>/reject/', views.manager_reject, name='manager_reject'),

    path('manager/add-course/', views.manager_add_course, name='manager_add_course'),
    path('manager/course/edit/<int:course_id>/', views.manager_edit_course, name='manager_edit_course'),
    path('manager/course/delete/<int:course_id>/', views.manager_delete_course, name='manager_delete_course'),





    path("lessons/<int:lesson_id>/complete/", views.mark_lesson_complete, name="mark_lesson_complete"),


    path("manager/student-progress/", views.manager_student_progress, name="manager_student_progress"),
    path("manager/certificate/generate/<int:student_id>/<int:course_id>/",views.manager_generate_certificate,name="manager_generate_certificate"),

    path("student/certificate/download/<int:cert_id>/", views.student_download_certificate, name="student_download_certificate"),
    path("student/notifications/", views.student_notifications, name="student_notifications"),





    path("manager/pending-teachers/", views.manager_pending_teachers, name="manager_pending_teachers"),
    path("manager/pending-applications/", views.manager_pending_applications, name="manager_pending_applications")



]
