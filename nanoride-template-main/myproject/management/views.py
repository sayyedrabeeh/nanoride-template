from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import logging
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import services
from django.views.decorators.cache import never_cache

@never_cache
@login_required(login_url='admin_login')
def users(request):
    all_users = User.objects.order_by('-is_active', 'last_login')    
    return render(request, 'adminside/users.html', {'all_users': all_users})

@never_cache
@login_required(login_url='admin_login')
def admin_projects(request):
    return render(request, 'adminside/admin_projects.html' )

@never_cache
@login_required(login_url='admin_login')
def service_admin(request):
    return render(request, 'adminside/service_admin.html' )

@never_cache
@login_required(login_url='admin_login')
def contact_management(request):
    return render(request, 'adminside/contact_management.html' )

@never_cache
@login_required(login_url='admin_login')
def block_user(request, user_id):
    User = get_user_model()
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'is_active': user.is_active})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@never_cache
@login_required(login_url='admin_login')
def user_details(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        data = {
            "name": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "phone": user.profile.phone,  
            "address": user.profile.address,  
            "wallet": user.profile.wallet,  
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
  
@never_cache
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:  
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('admin_login')  
            else:
                messages.error(request, 'You do not have permission to access this area.')
                return redirect('admin_login')  # 
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'adminside/login.html')
 
 
@login_required(login_url='admin_login')
def service_list(request):
    Services = services.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status')

    if status_filter and status_filter != 'all':
        Services = Services.filter(status = status_filter)

    search_query = request.GET.get('search')

    if search_query:
        Services = Services.filter(name__icontains = search_query) |Services.filter(description__icontains = search_query) 
        context = {
        'services': services,
        'total_services': services.objects.count(),
        'active_services': services.objects.filter(status='Active').count(),
        'inactive_services': services.objects.filter(status='Inactive').count(),
    }
    return render(request,'adminside/service_admin.html',context)

 