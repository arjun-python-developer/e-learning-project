from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import ManagerCourseForm, TeacherSignUpForm, StudentSignUpForm

# Registration Views
def teacher_register(request):
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.is_approved = False
            teacher.save()
            return redirect('login')
    else:
        form = TeacherSignUpForm()
    return render(request, 'teacher_register.html', {'form': form})

def student_register(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = StudentSignUpForm()
    return render(request, 'student_register.html', {'form': form})

# Dashboard redirection based on user_type
@login_required
def dashboard_redirect(request):
    user = request.user
    if user.user_type == 1:
        return redirect('manager_dashboard')
    elif user.user_type == 2:
        return redirect('teacher_dashboard')
    else:
        return redirect('student_dashboard')


# Dashboard Views
@login_required
def teacher_dashboard(request):
    return render(request, 'teacher_dashboard.html')

def student_dashboard(request):
    unread_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()
    return render(request, 'student_dashboard.html', {
        'unread_count': unread_count
    })

def landing_page(request):
    return render(request, 'landing_page.html')

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Redirect based on user_type
            if user.is_superuser or user.user_type == 1:  # Manager / Superuser
                return redirect('manager_dashboard')
            elif user.user_type == 2 and not user.is_approved:
                messages.error(request, "Your account is awaiting manager approval.")
                return redirect('login')
            elif user.user_type == 2: # Teacher
                return redirect('teacher_dashboard')
            elif user.user_type == 3: # Student
                return redirect('student_dashboard')
            else:
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    return render(request, 'login.html')


from .models import Certificate, Course, CustomUser, LessonCompletion, Notification, QuizResult
from .decorators import manager_only
from django.contrib.auth.decorators import login_required

@login_required
@manager_only
def manage_users(request):
    teachers = CustomUser.objects.filter(user_type=2)
    students = CustomUser.objects.filter(user_type=3)
    return render(request, 'manage_users.html', {'teachers': teachers, 'students': students})

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django import forms

# User Edit Form
class EditUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']

@login_required
@manager_only
def edit_user(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('manage_users')
    else:
        form = EditUserForm(instance=user_obj)
    return render(request, 'edit_user.html', {'form': form, 'user_obj': user_obj})

@login_required
@manager_only
def delete_user(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)
    user_obj.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('manage_users')

    










#teacher

from .forms import CourseForm
from .decorators import teacher_only
from django.contrib import messages

@teacher_only
def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, "Course added successfully!")
            return redirect('teacher_dashboard')
    else:
        form = CourseForm()

    return render(request, 'add_course.html', {'form': form})


@teacher_only
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'teacher_dashboard.html', {'courses': courses})

from django.shortcuts import get_object_or_404

@teacher_only
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('teacher_dashboard')
    else:
        form = CourseForm(instance=course)

    return render(request, 'edit_course.html', {'form': form, 'course': course})


from .models import Lesson, Course
from django.contrib.auth.decorators import login_required

@login_required
def add_lesson(request, course_id):
    course = Course.objects.get(id=course_id)
    
    if request.method == "POST":
        title = request.POST.get("title")
        text_content = request.POST.get("text_content")
        video = request.FILES.get("video")
        pdf = request.FILES.get("pdf")
        order = request.POST.get("order") or 0

        Lesson.objects.create(
            course=course,
            title=title,
            text_content=text_content,
            video=video,
            pdf=pdf,
            order=order
        )

        return redirect("teacher_dashboard")

    return render(request, "add_lesson.html", {"course": course})


from .models import Course, Lesson

def view_lessons(request, course_id):
    course = Course.objects.get(id=course_id)
    lessons = Lesson.objects.filter(course=course).order_by("order")

    return render(request, "view_lessons.html", {
        "course": course,
        "lessons": lessons
    })

from .models import Course, Lesson, Enrollment, EnrollmentRequest

@login_required
@teacher_only
def teacher_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    enrolled_students = Enrollment.objects.filter(course=course)
    pending_applications = EnrollmentRequest.objects.filter(course=course, status='pending')
    rejected_applications = EnrollmentRequest.objects.filter(course=course, status='rejected')
    quizzes = Quiz.objects.filter(course=course)


    return render(request, "course_detail.html", {
        "course": course,
        "enrolled_students": enrolled_students,
        "pending_applications": pending_applications,
        "rejected_applications": rejected_applications,
        "quizzes": quizzes,
    })


def remove_student(request, course_id, student_id):
    enrollment = Enrollment.objects.filter(course_id=course_id, student_id=student_id).first()
    if enrollment:
        enrollment.delete()
    return redirect('course_detail', course_id=course_id)


@login_required
@teacher_only
def approve_enrollment(request, course_id, application_id):
    application = get_object_or_404(
        EnrollmentRequest,
        id=application_id,
        course_id=course_id,
        course__teacher=request.user
    )

    # already approved allenkil mathram action cheyyu
    if application.status != 'approved':
        # enrollment create cheyyu
        Enrollment.objects.get_or_create(
            student=application.student,
            course=application.course
        )
        application.status = 'approved'
        application.save()
        messages.success(request, f"{application.student.username} has been approved for this course.")

    return redirect('teacher_course_detail', course_id=course_id)


@login_required
@teacher_only
def reject_enrollment(request, course_id, application_id):
    application = get_object_or_404(
        EnrollmentRequest,
        id=application_id,
        course_id=course_id,
        course__teacher=request.user
    )

    application.status = 'rejected'
    application.save()

    # in case somehow enrolled aayirunnenkil remove cheyyu
    Enrollment.objects.filter(
        student=application.student,
        course=application.course
    ).delete()

    messages.info(request, f"{application.student.username}'s application has been rejected.")
    return redirect('teacher_course_detail', course_id=course_id)



























#student
@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html')

from django.contrib import messages
from .models import Course, Enrollment

@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, "my_courses.html", {"enrollments": enrollments})


from .models import Course, Enrollment, EnrollmentRequest  # top il import update cheyyan marakkaruthe

@login_required
def available_courses(request):
    # already enrolled
    enrolled_ids = Enrollment.objects.filter(
        student=request.user
    ).values_list('course_id', flat=True)

    # already applied, still pending
    pending_ids = EnrollmentRequest.objects.filter(
        student=request.user,
        status='pending'
    ).values_list('course_id', flat=True)

    # show only courses: not enrolled + not already applied
    courses = Course.objects.exclude(id__in=enrolled_ids).exclude(id__in=pending_ids)

    return render(request, "available_courses.html", {"courses": courses})



from django.shortcuts import get_object_or_404
from .models import Course, Enrollment, EnrollmentRequest

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, "Already enrolled in this course.")
        return redirect('available_courses')

    # already applied & still pending
    if EnrollmentRequest.objects.filter(
        student=request.user,
        course=course,
        status='pending'
    ).exists():
        messages.warning(request, "You have already applied for this course. Please wait for approval.")
        return redirect('available_courses')

    # create new application with status = pending
    EnrollmentRequest.objects.create(
        student=request.user,
        course=course,
        status='pending'
    )
    messages.success(request, "Application sent! Wait for teacher approval.")
    return redirect('available_courses')





from .models import Course, Lesson, Enrollment

def student_lessons(request, course_id):
    course = Course.objects.get(id=course_id)

    # student enrolled aano enn check
    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).exists()

    if not is_enrolled:
        return render(request, "not_enrolled.html", {"course": course})

    lessons = Lesson.objects.filter(course=course).order_by("order")

    # 1️⃣ Completed lessons list
    completed = LessonCompletion.objects.filter(
        student=request.user,
        lesson__course=course
    ).values_list('lesson_id', flat=True)

    # 2️⃣ Progress calculation
    total_lessons = lessons.count()
    completed_count = len(completed)
    progress = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 0

    # 3️⃣ Pass to template
    return render(request, "student_lessons.html", {
        "course": course,
        "lessons": lessons,
        "completed_ids": completed,
        "progress": progress,
    })


from .models import EnrollmentRequest

@login_required
def my_applications(request):
    applications = EnrollmentRequest.objects.filter(student=request.user).order_by('-created_at')
    return render(request, "my_applications.html", {"applications": applications})


@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    # ensure student enrolled
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        return redirect("student_dashboard")

    LessonCompletion.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )

    return redirect('student_lessons', course_id=course.id)














#quiz

from .models import Quiz, Question, Choice

@login_required
@teacher_only
def add_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    if request.method == "POST":
        title = request.POST['title']
        Quiz.objects.create(course=course, title=title)
        messages.success(request, "Quiz created successfully!")
        return redirect('teacher_course_detail', course_id=course_id)

    return render(request, 'add_quiz.html', {'course': course})

@login_required
@teacher_only
def manage_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course__teacher=request.user)
    questions = quiz.questions.all()
    return render(request, 'manage_questions.html', {'quiz': quiz, 'questions': questions})

@login_required
@teacher_only
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course__teacher=request.user)
    if request.method == "POST":
        Question.objects.create(quiz=quiz, text=request.POST['text'])
        return redirect('manage_quiz', quiz_id=quiz_id)

    return render(request, 'add_question.html', {'quiz': quiz})

@login_required
@teacher_only
def add_choice(request, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__course__teacher=request.user)

    if request.method == "POST":
        Choice.objects.create(
            question=question,
            option=request.POST['option'],
            is_correct=('correct' in request.POST)
        )
        return redirect('manage_quiz', quiz_id=question.quiz.id)

    return render(request, 'add_choice.html', {'question': question})


from .models import Quiz

@login_required
def student_quiz_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # student check
    if not Enrollment.objects.filter(course=course, student=request.user).exists():
        return redirect('available_courses')

    quizzes = Quiz.objects.filter(course=course)
    return render(request, 'student_quizzes.html', {'quizzes': quizzes, 'course': course})

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    existing = QuizResult.objects.filter(
        quiz=quiz,
        student=request.user
    ).first()

    if existing:
        return render(request, 'quiz_result.html', {
            'score': existing.score,
            'total': existing.total,
            'quiz': quiz,
            'message': "You already submitted this quiz."
        })

    if request.method == 'POST':
        score = 0
        total = questions.count()

        for q in questions:
            selected = request.POST.get(str(q.id))
            if selected:
                choice = Choice.objects.get(id=selected)
                if choice.is_correct:
                    score += 1

        QuizResult.objects.update_or_create(
            quiz=quiz,
            student=request.user,
            defaults={'score': score, 'total': total}
        )

        return render(request, 'quiz_result.html', {
            'score': score,
            'total': total,
            'quiz': quiz
        })

    return render(request, 'take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })


@login_required
@teacher_only
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course__teacher=request.user)
    results = QuizResult.objects.filter(quiz=quiz)

    return render(request, 'quiz_results.html', {
        'quiz': quiz,
        'results': results,
    })


@login_required
@teacher_only
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course__teacher=request.user)
    course_id = quiz.course.id
    quiz.delete()
    messages.success(request, "Quiz deleted successfully.")
    return redirect('teacher_course_detail', course_id=course_id)

@login_required
@teacher_only
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__course__teacher=request.user)
    quiz_id = question.quiz.id
    question.delete()
    messages.success(request, "Question deleted successfully.")
    return redirect('manage_quiz', quiz_id=quiz_id)

@login_required
@teacher_only
def delete_choice(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id, question__quiz__course__teacher=request.user)
    quiz_id = choice.question.quiz.id
    choice.delete()
    messages.success(request, "Choice deleted successfully.")
    return redirect('manage_quiz', quiz_id=quiz_id)


















#manager
from .models import Course, CustomUser, Enrollment

@login_required
@manager_only
def manager_dashboard(request):
    total_teachers = CustomUser.objects.filter(user_type=2).count()
    total_students = CustomUser.objects.filter(user_type=3).count()
    total_courses = Course.objects.count()
    latest_courses = Course.objects.order_by('-created_at')[:5]
    pending_teachers = CustomUser.objects.filter(user_type=2, is_approved=False)
    pending_enrollments = EnrollmentRequest.objects.filter(status='pending')


    
    return render(request, 'manager_dashboard.html', {
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_courses': total_courses,
        'latest_courses': latest_courses,
        'pending_teachers': pending_teachers,
        'pending_enrollments': pending_enrollments,


    })


@login_required
@manager_only
def approve_teacher(request, user_id):
    teacher = get_object_or_404(CustomUser, id=user_id)
    teacher.is_approved = True
    teacher.save()
    messages.success(request, "Teacher approved.")
    return redirect('manager_dashboard')

@login_required
@manager_only
def reject_teacher(request, user_id):
    teacher = get_object_or_404(CustomUser, id=user_id)
    teacher.delete()
    messages.error(request, "Teacher rejected and removed.")
    return redirect('manager_dashboard')

@login_required
@manager_only
def manager_approve(request, id):
    application = get_object_or_404(EnrollmentRequest, id=id)
    application.status = 'approved'
    application.save()

    Enrollment.objects.get_or_create(
        student=application.student,
        course=application.course
    )

    messages.success(request, "Application Approved")
    return redirect('manager_dashboard')


@login_required
@manager_only
def manager_reject(request, id):
    application = get_object_or_404(EnrollmentRequest, id=id)
    application.status = 'rejected'
    application.save()

    messages.error(request, "Application Rejected")
    return redirect('manager_dashboard')


@login_required
@manager_only
def manager_add_course(request):
    if request.method == "POST":
        form = ManagerCourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created and teacher assigned!")
            return redirect('manager_dashboard')
    else:
        form = ManagerCourseForm()

    return render(request, 'manager_add_course.html', {'form': form})

@login_required
@manager_only
def manager_edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = ManagerCourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('manager_dashboard')
    else:
        form = ManagerCourseForm(instance=course)

    return render(request, 'manager_edit_course.html', {'form': form, 'course': course})

@login_required
@manager_only
def manager_delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.success(request, "Course deleted successfully!")
    return redirect('manager_dashboard')

from .models import Enrollment, LessonCompletion

@login_required
@manager_only
def manager_student_progress(request):
    enrollments = Enrollment.objects.select_related("student", "course")

    progress_data = []

    for e in enrollments:
        course = e.course
        student = e.student
        total_lessons = course.lessons.count()

        completed = LessonCompletion.objects.filter(
            student=student,
            lesson__course=course
        ).count()

        progress = int((completed / total_lessons) * 100) if total_lessons > 0 else 0

        progress_data.append({
            "student": student,
            "course": course,
            "completed": completed,
            "total": total_lessons,
            "progress": progress
        })

    return render(request, "manager_student_progress.html", {
        "progress_data": progress_data
    })
student_quiz_list



from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import uuid
from django.core.files.base import File
from io import BytesIO

@login_required
@manager_only
def manager_generate_certificate(request, student_id, course_id):
    student = get_object_or_404(CustomUser, id=student_id)
    course = get_object_or_404(Course, id=course_id)

    # progress check
    total_lessons = course.lessons.count()
    completed = LessonCompletion.objects.filter(
        student=student,
        lesson__course=course
    ).count()

    if completed < total_lessons:
        messages.error(request, "Student has not completed the course.")
        return redirect('manager_student_progress')

    # Create / fetch certificate
    cert, created = Certificate.objects.get_or_create(
        student=student,
        course=course,
        defaults={"certificate_id": str(uuid.uuid4())[:8]}
    )

    # Create PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setFont("Helvetica-Bold", 28)
    p.drawCentredString(300, 750, "Certificate of Completion")

    p.setFont("Helvetica", 16)
    p.drawCentredString(300, 680, f"This is to certify that")
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(300, 640, student.username)

    p.setFont("Helvetica", 16)
    p.drawCentredString(300, 600, "has successfully completed the course:")
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(300, 560, course.title)

    p.setFont("Helvetica", 12)
    p.drawCentredString(300, 520, f"Certificate ID: {cert.certificate_id}")

    p.showPage()
    p.save()

    buffer.seek(0)

    # Save PDF to model
    cert.file.save(f"certificate_{cert.certificate_id}.pdf", File(buffer), save=True)

    # Create notification
    Notification.objects.create(
        user=student,
        message=f"Your certificate for {course.title} is ready!",
        link=f"/student/certificate/download/{cert.id}/"
    )

    messages.success(request, "Certificate generated successfully!")
    return redirect("manager_student_progress")


@login_required
def student_download_certificate(request, cert_id):
    cert = get_object_or_404(Certificate, id=cert_id, student=request.user)

    if not cert.file:
        return HttpResponse("Certificate file not found.", status=404)

    response = HttpResponse(cert.file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{cert.file.name}"'
    return response


@login_required
def student_notifications(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')

    # mark all as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    return render(request, "student_notifications.html", {"notifications": notes})




@login_required
@manager_only
def manager_pending_teachers(request):
    pending_teachers = CustomUser.objects.filter(
        user_type=2,
        is_approved=False
    )
    return render(request, "manager_pending_teachers.html", {
        "pending_teachers": pending_teachers
    })

@login_required
@manager_only
def manager_pending_applications(request):
    pending_enrollments = EnrollmentRequest.objects.filter(status="pending")
    return render(request, "manager_pending_applications.html", {
        "pending_enrollments": pending_enrollments
    })
