from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

def manager_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.user_type == 1:
                return view_func(request, *args, **kwargs)
            else:
                # Other users → dashboard redirect
                if request.user.user_type == 2:
                    return HttpResponseRedirect(reverse('teacher_dashboard'))
                elif request.user.user_type == 3:
                    return HttpResponseRedirect(reverse('student_dashboard'))
        else:
            return HttpResponseRedirect(reverse('login'))
    return wrapper_func


def teacher_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 2:
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper_func


def student_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 3:
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper_func