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
from .models import services,Project,ProjectImage,ContactForm
from django.db.models import Sum
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from datetime import datetime

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
def add_service(request):
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
        
    return render(request,'adminside/service_admin.html')

@login_required(login_url='admin_login')
@require_http_methods(["GET", "POST"])
def edit_service(request,service_id):
    service = get_object_or_404(services,id = service_id)
    if request.method  == 'POST':
        try:
            service.name =  request.POST.get('name')
            service.category = request.POST.get("category")
            service.starting_price = request.POST.get('starting_price')
            service.project_duration = request.POST.get('project_duration')
            service.description = request.POST.get('description')
            service.features =  request.POST.get('features')

            if request.FILES.get('image'):
                service.image = request.FILES.get('image')
            service.save()
            messages.success(request,f'service {service.name} updated successfully')
            return redirect(service_admin)
        except Exception as e :
                messages.error(request,f'error in adding service :{str(e)}')
                return redirect(service_admin)
            
    return render(request,'adminside/service_admin.html')

@login_required(login_url='admin_login')
@require_http_methods(["POST"])
def delete_service(request,service_id):
    if request.method == 'POST':
        service = get_object_or_404(services,id = service_id)
        service_name = service.name
        service.delete()
        messages.success(request,f'service {service_name} deleted successfully')
        return redirect(service_admin)
    
@login_required(login_url='admin_login')
@require_http_methods(["POST"])
def toggle_service(request,service_id):
    service = get_object_or_404(services,id = service_id)
    service.status = 'Inactive' if service.status == 'Active' else 'Active'
    service.save()
    messages.success(request,f'service  status Updated successfully')
    return redirect(service_admin)

@login_required(login_url='admin_login')
def view_service(request,service_id):
    service = get_object_or_404(services,id = service_id)
    context = {'service': service}
    return render(request,'adminside/service_admin.html',context)


@login_required(login_url='admin_login')
def Project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        projects = projects.filter(status = status_filter)
    category_filter  = request.GET.get('category')
    if category_filter  and category_filter  != 'all':
        projects = projects.filter(status = category_filter )
    search_query = request.GET.get('search')
    current_year = now().year
    projects_this_year = Project.objects.filter(created_at__year=current_year).count()
    if search_query:
        projects = projects.filter(title__icontains = search_query) |projects.filter(overview__icontains = search_query)|projects.filter(client_name__icontains = search_query) 
    context = {
        'projects': projects,
        'projects_this_year':projects_this_year,
        "residential_count": projects.filter(category="residential").count(),
        "commercial_count": projects.filter(category="commercial").count(),
        'total_projects': Project.objects.count(),
        'published_projects': Project.objects.filter(status='published').count(),
        'draft_projects': Project.objects.filter(status='draft').count(),
        'featured_projects': Project.objects.filter(featured=True).count(),
    }
    return render(request,'adminside/admin_projects.html',context)




@login_required(login_url='admin_login')
@require_http_methods(["GET", "POST"])
def add_project(request):
    if request.method == 'POST':
        try:
            project = Project.objects.create(
                title=request.POST.get('title'),
                category=request.POST.get('category'),
                overview=request.POST.get('overview'),
                client_field =request.POST.get('client_name'),
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
            return redirect('Project_list')
        except Exception as e:
            messages.error(request,f'error in creating Project : {str(e)}')
            return redirect('Project_list')
    context = {
        "mode": "add",
        'categories': [
            ('residential', 'Residential Design'),
            ('commercial', 'Commercial Design'),
            ('hospitality', 'Hospitality Design'),
            ('retail', 'Retail Design'),
            ('office', 'Office Design'),
        ]
    }
    return render(request,'adminside/admin_projects.html',context)




@login_required(login_url='admin_login')
@require_http_methods(["GET", "POST"])
def edit_project(request,project_id):
    project = get_object_or_404(Project,id = project_id)
    if request.method == 'POST':
        try:
  
            project.title = request.POST.get('title',project.title)
            project.category = request.POST.get('category',project.category)
            project.overview = request.POST.get('overview',project.overview)
            project.client_field  = request.POST.get('client_name', project.client_field )
            project.location = request.POST.get('location',project.location)
            project.year = request.POST.get('year',project.year)
            project.area = request.POST.get('area',project.area)
            project.duration = request.POST.get('duration',project.duration)
            project.budget = request.POST.get('budget',project.budget)
            project.property_type = request.POST.get('property_type', project.property_type)
            project.bedrooms = request.POST.get('bedrooms', project.bedrooms)
            project.bathrooms = request.POST.get('bathrooms',  project.bathrooms)
            project.style = request.POST.get('style', project.style)
            project.challenge = request.POST.get('challenge', project.challenge)
            project.solution = request.POST.get('solution', project.solution)
            project.feature1_title = request.POST.get('feature1_title', project.feature1_title)
            project.feature1_desc = request.POST.get('feature1_desc', project.feature1_desc)
            project.feature2_title = request.POST.get('feature2_title', project.feature2_title)
            project.feature2_desc = request.POST.get('feature2_desc', project.feature2_desc)
            project.feature3_title = request.POST.get('feature3_title', project.feature3_title)
            project.feature3_desc = request.POST.get('feature3_desc', project.feature3_desc)
            project.feature4_title = request.POST.get('feature4_title', project.feature4_title)
            project.feature4_desc = request.POST.get('feature4_desc', project.feature4_desc)
            project.tags = request.POST.get('tags',  project.tags)
            project.testimonial=request.POST.get('testimonial', '')
            project.status = request.POST.get('status',project.status)
            project.featured=request.POST.get('featured') == 'yes'
            if request.FILES.get('hero_image'):
                project.hero_image=request.FILES.get('hero_image')
            
            project.save()
            messages.success(request, f'Project "{project.title}" updated successfully!')
            return redirect('Project_list')
        except Exception as e:
            messages.error(request,f'error in updating Project : {str(e)}')
            return redirect('Project_list')
    context = {
        "mode": "edit",
        'project' : project,
        'categories': [
            ('residential', 'Residential Design'),
            ('commercial', 'Commercial Design'),
            ('hospitality', 'Hospitality Design'),
            ('retail', 'Retail Design'),
            ('office', 'Office Design'),
        ]
    }
    return render(request,'adminside/admin_projects.html',context)


@login_required(login_url='admin_login')
@require_http_methods(["POST"])
def delete_project(request,project_id):

    project = get_object_or_404(Project,id = project_id)
    project_name = project.name
    project.delete()
    messages.success(request,f'service {project_name} deleted successfully')
    return redirect('Project_list')

@login_required
def view_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    context = {'project': project}
    return render(request,'adminside/admin_projects.html',context)

@login_required(login_url='admin_login')
@require_http_methods(["POST"])
def toggle_featured(request,project_id):
    project = get_object_or_404(services,id = project_id)
    project.featured =  not project.featured
    project.save()
    status = 'Featured' if project.featured else 'Unfeatured'
    messages.success(request, f'Project marked as {status}!')
    return redirect('Project_list')


@login_required(login_url='admin_login')
def Contact_form_list(request):
    contacts = ContactForm.objects.all().order_by('-created_at')

    status_filter = request.GET.get('status')

    if status_filter and status_filter != 'all':
        contacts = contacts.filter(status = status_filter)
    search_query = request.GET.get('search')

    if search_query:
        contacts = contacts.filter(user__first_name__icontains = search_query) |contacts.filter(user__email__icontains = search_query)|contacts.filter(subject__icontains = search_query) 
  
    context = {
        'contacts': contacts,
        'total_contacts': ContactForm.objects.count(),
        'pending_contacts': ContactForm.objects.filter(status__in=['new', 'pending']).count(),
        'replied_contacts': ContactForm.objects.filter(status='replied').count(),
    }
    return render(request, 'adminside/contact_management.html', context)


@login_required
def view_contact(request,contact_id):
    contact = get_object_or_404(ContactForm,id = contact_id)
    context = { 'contact':contact }
    return render(request,'adminside/contact_management.html',context)

@login_required
@require_http_methods(["POST"])
def reply_contact(request,contact_id):
    contact = get_object_or_404(ContactForm,id = contact_id)
    try:
        replay_massage = request.POST.get('replay_massage')
        mark_replied = request.POST.get(mark_replied) == 'on'

        contact.replay_message = replay_massage
        if mark_replied:
            contact.status = 'replied'
            contact.replied_date = datetime.now()
        else:
            contact.status = 'pending'

        contact.save()
        messages.success(request,'Reply sent successfully')
        return redirect('contact_management')
    except Exception as e:
        messages.error(request,f'error in sending messages {str(e)}')
        return redirect('contact_management')

@login_required
@require_http_methods(["POST"])
def delete_contact(request,contact_id):
    contact = get_object_or_404(ContactForm,id = contact_id)
    contact_subject = contact.subject
    contact.delete()
    messages.success(request, f'Contact "{contact_subject}" deleted successfully!')
    return redirect('contact_management')












