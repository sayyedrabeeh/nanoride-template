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
from .models import services,Project,ProjectImage
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

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


@login_required(login_url='admin_login')
@require_http_methods(["GET", "POST"])
def add_services(request):
    if request.method == "POST":
        try:
            Service = services.objects.create(
                name =  request.POST.get('name'),
                category = request.POST.get("category"),
                starting_price = request.POST.get('starting_price'),
                project_duration = request.POST.get('project_duration'),
                description = request.POST.get('description'),
                features =  request.POST.get('features'),
                status = 'Active',
                image = request.FILES.get('image')
            )
            messages.success(request,f'Service {Service.name} added successfully ')
            return redirect(service_admin)
        except Exception as e :
            messages.error(request,f'error in adding service :{str(e)}')
            return redirect(service_admin)
        
    return render(request,'adminside/service_admin')

@login_required(login_url='admin_login')
@require_http_methods(["GET", "POST"])
def edit_service(request,service_id):
    service = get_object_or_404(services,id = service_id)
    if request.method  == 'POST':
        try:
            service.name =  request.POST.get('name'),
            service.category = request.POST.get("category"),
            service.starting_price = request.POST.get('starting_price'),
            service.project_duration = request.POST.get('project_duration'),
            service.description = request.POST.get('description'),
            service.features =  request.POST.get('features'),

            if request.FILES.get('image'):
                service.image = request.FILES.get('image')
            service.save()
            messages.success(request,f'service {service.name} updated successfully')
            return redirect(service_admin)
        except Exception as e :
                messages.error(request,f'error in adding service :{str(e)}')
                return redirect(service_admin)
            
    return render(request,'adminside/service_admin')


@login_required
@require_http_methods(["POST"])
def delete_service(request,service_id):
    if request.method == 'POST':
        service = get_object_or_404(services,id = service_id)
        service_name = service.name
        service.delete()
        messages.success(request,f'service {service_name} deleted successfully')
        return redirect(service_admin)
    
@login_required
@require_http_methods(["POST"])
def toggle_service(request,service_id):
    service = get_object_or_404(services,id = service_id)
    service.status = 'Inactive' if service.status == 'Active' else 'Active'
    service.save()
    messages.success(request,f'service  status Updated successfully')
    return redirect(service_admin)

@login_required
def view_service(request,service_id):
    service = get_object_or_404(services,id = service_id)
    context = {'service': service}
    return render(request,'adminside/service_admin',context)


@login_required
def Project_list(request):

 
    projects = Project.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status')

    if status_filter and status_filter != 'all':
        projects = Services.filter(status = status_filter)
    category_filter  = request.GET.get('category')

    if category_filter  and category_filter  != 'all':
        projects = Services.filter(status = category_filter )

    search_query = request.GET.get('search')

    if search_query:
        Services = projects.filter(title__icontains = search_query) |projects.filter(overview__icontains = search_query)|projects.filter(client_name__icontains = search_query) 
    context = {
        'projects': projects,
        'total_projects': Project.objects.count(),
        'published_projects': Project.objects.filter(status='published').count(),
        'draft_projects': Project.objects.filter(status='draft').count(),
        'featured_projects': Project.objects.filter(featured=True).count(),
    }
    return render(request,'adminside/admin_projects.html',context)

@login_required
@require_http_methods(["GET", "POST"])
def add_project(request):
    if request.method == 'POST':
        try:
            project = Project.objects.create(
                title=request.POST.get('title'),
                category=request.POST.get('category'),
                overview=request.POST.get('overview'),
                client_name=request.POST.get('client_name'),
                location=request.POST.get('location'),
                year=request.POST.get('year'),
                area=request.POST.get('area'),
                duration=request.POST.get('duration'),
                budget=request.POST.get('budget'),
                property_type=request.POST.get('property_type', ''),
                bedrooms=request.POST.get('bedrooms', 0),
                bathrooms=request.POST.get('bathrooms', ''),
                style=request.POST.get('style', ''),
                challenge=request.POST.get('challenge', ''),
                solution=request.POST.get('solution', ''),
                feature1_title=request.POST.get('feature1_title', ''),
                feature1_desc=request.POST.get('feature1_desc', ''),
                feature2_title=request.POST.get('feature2_title', ''),
                feature2_desc=request.POST.get('feature2_desc', ''),
                feature3_title=request.POST.get('feature3_title', ''),
                feature3_desc=request.POST.get('feature3_desc', ''),
                feature4_title=request.POST.get('feature4_title', ''),
                feature4_desc=request.POST.get('feature4_desc', ''),
                tags=request.POST.get('tags', ''),
                testimonial=request.POST.get('testimonial', ''),
                status=request.POST.get('status', 'draft'),
                featured=request.POST.get('featured') == 'yes',
                hero_image=request.FILES.get('hero_image')
            )
            gallery_images = request.FILES.getlist('gallery_images')
            for img in gallery_images:
                img_obj = ProjectImage.objects.create(image=img)
                project.gallery_images.add(img_obj)
            messages.success(request, f'Project "{project.title}" added successfully!')
            return redirect('admin_projects')
        except Exception as e:
            messages.error(request,f'error in creating Project : {str(e)}')
            return redirect('admin_projects')
    context = {
        'categories': [
            ('residential', 'Residential Design'),
            ('commercial', 'Commercial Design'),
            ('hospitality', 'Hospitality Design'),
            ('retail', 'Retail Design'),
            ('office', 'Office Design'),
        ]
    }
    return render(request,'adminside/admin_projects.html',context)

