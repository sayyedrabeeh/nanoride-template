from django.shortcuts import render,get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_protect
import random
from django.views.decorators.csrf import csrf_exempt
import time
from threading import Thread
from django.contrib.auth import logout
from django.contrib.auth import password_validation
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from management.models import Project,services,ContactForm
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from myproject.brevo_client import brevo_client
from myproject.email_service import send_otp_email
from myproject.email_service import send_email

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:  
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('users')  
            else:
                messages.error(request, 'You do not have permission to access this area.')
                return redirect('admin_login') 
    return render(request, 'adminside/login1.html')


def generate_otp():
    return str(random.randint(100000, 999999))

def usersignup(request):
    if request.user.is_authenticated:
        return redirect('users')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1)<6:
            messages.error(request, 'Passwords must be six charecter.')
        else:
            user = User(username=username, email=email)
            user.set_password(password1)
            otp = generate_otp()
            success = send_otp_email(email, otp)
            if success:
                 
                request.session['otp'] = otp 
                request.session['otp_generated_time'] = time.time() 
                request.session['otp_expiration_time'] = 300
                request.session['resend_otp_time'] = 30   
                request.session['user_data'] = {'username': username, 'email': email, 'password': password1}
                return redirect('verify_otp')
            else:
                messages.error(request, 'Error sending email. Try again later.')
                return render(request, 'userside/otp.html') 
    return render(request, 'account/signup.html')  


@csrf_protect
def verify_otp(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        otp_inputs = [
            request.POST.get('otp_1'),
            request.POST.get('otp_2'),
            request.POST.get('otp_3'),
            request.POST.get('otp_4'),
            request.POST.get('otp_5'),
            request.POST.get('otp_6'),
        ]
        entered_otp = ''.join(filter(None, otp_inputs))
        generated_otp = request.session.get('otp')
        user_data = request.session.get('user_data')
        otp_generated_time = request.session.get('otp_generated_time')
        otp_expiration_time = request.session.get('otp_expiration_time', 300)  
        current_time = time.time()
        if otp_generated_time is None:
            messages.error(request, 'No OTP generated. Please request a new one.')
            return redirect('request_otp')  
        if current_time - otp_generated_time > otp_expiration_time:
            messages.error(request, 'Your OTP has expired. Please request a new one.')
            return render(request, 'userside/otp.html', context={'otp_form': True})
        if entered_otp == generated_otp:
            if user_data:
                user = User(username=user_data['username'], email=user_data['email'])
                user.set_password(user_data['password'])
                try:
                    user.full_clean()  
                    user.save()  
                    messages.success(request, 'Account created successfully!')
                    login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
                    del request.session['otp']
                    del request.session['user_data']
                    return redirect('userlogin') 
                except ValidationError as e:
                    messages.error(request, f'Error creating account: {str(e)}')
            else:
                messages.error(request, 'User data not found in session.')
        else:
            messages.error(request, 'Invalid OTP or expired OTP. Please try again.')
        return render(request, 'userside/otp.html', context={'otp_form': True})
    return render(request, 'userside/otp.html', context={'otp_form': True})


@csrf_exempt  
def resend_otp(request):
    if request.method == 'POST':
        last_resend_time = request.session.get('otp_generated_time', 0) + request.session.get('resend_otp_time', 0)
        email = request.session.get('user_data', {}).get('email')  
        if time.time() < last_resend_time:
            return JsonResponse({'status': 'error', 'message': 'Please wait before requesting a new OTP.'})
        email = request.session.get('user_data', {}).get('email')
        if not email:
            return JsonResponse({'status': 'error', 'message': 'User not found in session.'})
        otp = generate_otp()
        subject = 'Your OTP Code'
        message = f'Your new OTP code is {otp}'
        from_email = settings.EMAIL_HOST_USER
        try:
            send_mail(subject, message, from_email, [email])
            request.session['otp'] = otp
            request.session['otp_generated_time'] = time.time()  
            request.session['otp_expiration_time'] = 300  
            return JsonResponse({'status': 'success', 'message': 'OTP has been resent.'})  
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})  
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}) 



def userlogin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'User does not exist. Please sign up.')
            return render(request, 'account/login.html', {'username': username})
        user = authenticate(request, username=username, password=password)
        if user is not None:
              if not user.is_active:
                    messages.error(request, "You are not allowed to log in.")
                    return render(request, 'login.html')
              auth_login(request, user)
              return redirect('home')
        else:
            messages.error(request, 'Username or Password is wrong.')
            return render(request, 'account/login.html', {'username': username})
    return render(request, 'account/login.html')


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if not user.is_active:   
                return None
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

 
def home(request):
    home_services = services.objects.filter(status='Active')[:6]
    project_count = Project.objects.count()
    featured_projects = Project.objects.filter(status='published',featured=True)[:3]
    if not featured_projects:
        featured_projects = Project.objects.filter(status='published')[:3]
    context = {
        'services': home_services,
        'projects': featured_projects,
        'project_count':project_count
    }
    return render(request,'userside/home.html',context)

@login_required
def portfolio(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request,'userside/portfolio.html',{
        'projects':projects,
        'completed_projects': projects.count()
        })

@login_required
def singleproject(request,project_id):
    project = get_object_or_404(Project,id = project_id)
    related_projects = Project.objects.filter(
        category=project.category
    ).exclude(id=project.id)[:3]
    
    return render(request,'userside/singleproject.html',{
        'project':project,
        'related_projects':related_projects
        })

def process(request):
    return render(request,'userside/process.html')

def Testimonials(request):
    return render(request,'userside/Testimonials.html')

def custom_logout(request):
    logout(request)   
    request.session.flush()   
    return redirect('home')

def restricted_view(request):
   
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to access this page.")
        return redirect('custom_login')  
    return render(request, 'restricted.html') 


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to admin users."""
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            messages.error(self.request, "You do not have permission to access this area.")
            return False 

class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = 'adminside/users.html'

    def handle_no_permission(self):
        return redirect('admin_login')  
    
def custom_logoutadmin(request):
    logout(request)  
    messages.success(request, "You have been logged out successfully.")   
    return redirect('admin_login') 

def about(request):
    return render(request,'userside/about.html')

def service(request):
    all_services = services.objects.filter(status='Active')
    overview_services = all_services.filter(category__in=['Residential', 'Commercial', 'Hospitality'])[:3]
    detail_services = all_services.exclude(category__in=['Residential', 'Commercial', 'Hospitality'])
  
    context = {
        'overview_services': overview_services,
        'detail_services': detail_services,
        'all_services': all_services,
    }
    return render(request,'userside/service.html',context)

def contact(request):
    return render(request,'userside/contact.html')
 
def send_async(func):
    Thread(target=func).start()

@csrf_exempt
def submit_contact_form(request):
    if request.method != "POST":
        return JsonResponse({"status": "invalid_request"})

    data = {
        'firstName': request.POST.get('firstName'),
        'lastName': request.POST.get('lastName'),
        'email': request.POST.get('email'),
        'phone': request.POST.get('phone'),
        'projectType': request.POST.get('projectType'),
        'budget': request.POST.get('budget'),
        'timeline': request.POST.get('timeline'),
        'message': request.POST.get("message"),
        'source': request.POST.get("source"),
    }

 
    ContactForm.objects.create(
        user=request.user if request.user.is_authenticated else None,
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        phone=data['phone'],
        project_type=data['projectType'],
        budget=data['budget'],
        timeline=data['timeline'],
        source=data['source'],
        message=data['message'],
        status="new",
    )

 
    admin_html = render_to_string('emails/admin_notification.html', data)
    user_html = render_to_string('emails/user_confirmation.html', data)

  
    def send_admin_email():
        send_email(
            to_email="sayyedrabeeh240@gmail.com",
            subject=f"New Inquiry: {data['projectType']}",
            html_content=admin_html
        )

    
    def send_user_email():
        send_email(
            to_email=data["email"],
            subject=f"Thank You for Contacting Woodora, {data['firstName']}!",
            html_content=user_html
        )

 
    send_async(send_admin_email)
    send_async(send_user_email)

    return JsonResponse({"status": "success"})