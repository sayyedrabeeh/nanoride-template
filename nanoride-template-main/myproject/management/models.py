from django.contrib.auth.models import AbstractUser,User, Group, Permission
from django.db import models
# from image_cropping import ImageRatioField

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', default='images/profile.jpeg')
    phone = models.CharField(max_length=15, blank=True, null=True) 
    address = models.TextField(blank=True, null=True)  
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_auth_set',  
        blank=True,
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_auth_set',  
        blank=True,
    )


class services(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100,choices=[
        ('Residential', 'Residential Design'),
        ('Commercial', 'Commercial Spaces'),
        ('Hospitality', 'Hospitality Design'),
        ('Space Planning', 'Space Planning'),
        ('Color Consultation', 'Color Consultation'),
        ('Furniture Selection', 'Furniture Selection'),
    ]) 
    starting_price = models.DecimalField(max_digits=10,decimal_places=2)
    project_duration = models.IntegerField(help_text='Duration in weeks')
    description = models.TextField()
    features = models.TextField(help_text='One feature per line')
    status = models.CharField(max_length=100,choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]) 
    image = models.ImageField(upload_to='services/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Services'
    
    def __str__(self):
        return self.name
    def get_category_icon(self):
        
        icons = {
            'Residential': 'fas fa-home',
            'Commercial': 'fas fa-building',
            'Hospitality': 'fas fa-utensils',
            'Space Planning': 'fas fa-drafting-compass',
            'Color Consultation': 'fas fa-palette',
            'Furniture Selection': 'fas fa-couch',
        }
        return icons.get(self.category, 'fas fa-star')
    
    def get_features_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]
    
 

class Project(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50,choices=[
        ('residential', 'Residential Design'),
        ('commercial', 'Commercial Design'),
        ('hospitality', 'Hospitality Design'),
        ('retail', 'Retail Design'),
        ('office', 'Office Design'),
    ])
    overview = models.TextField()
    client_field = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    year = models.IntegerField()
    area = models.CharField(help_text='e.g., 3,500 sq ft',max_length=100)
    duration = models.CharField(max_length=100,help_text='e.g., 6 Months')
    budget = models.CharField(max_length=100,help_text='e.g., $120K')

    property_type = models.CharField(max_length=100,blank=True)
    bedrooms = models.IntegerField(null=True,blank=True)
    bathrooms = models.IntegerField(null=True,blank=True)
    style = models.CharField(max_length=200,blank=True)

    challenge = models.TextField(blank=True)
    solution = models.TextField(blank=True)

    feature1_title = models.CharField(max_length=200,blank=True)
    feature1_desc = models.TextField(blank=True)
    feature2_title = models.CharField(max_length=200,blank=True)
    feature2_desc = models.TextField(blank=True)
    feature3_title = models.CharField(max_length=200,blank=True)
    feature3_desc = models.TextField(blank=True)
    feature4_title = models.CharField(max_length=200,blank=True)
    feature4_desc = models.TextField(blank=True)

    tags = models.TextField(max_length=500,blank=True,help_text="Comma separated tags")
    testimonial = models.TextField(blank=True)

    hero_image = models.ImageField(upload_to='projects/hero/')
    gallery_images = models.ManyToManyField('ProjectImage',blank=True,related_name='projects')

    status = models.CharField(max_length=20,default='draft',choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]) 
    featured = models.BooleanField(default=False)

    created_at =  models.DateTimeField(auto_now_add=True)
    updated_at =  models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_features(self):
        """Return list of features"""
        features = []
        for i in range(1, 5):
            title = getattr(self, f'feature{i}_title')
            desc = getattr(self, f'feature{i}_desc')
            if title:
                features.append({
                    'title': title,
                    'description': desc
                })
        return features
    
    def get_tags(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
class ProjectImage(models.Model):
    image = models.ImageField(upload_to='projects/gallery/')
    upload_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Project Images"
    
    def __str__(self):
        return f"Project Image {self.id}"
    

class ContactForm(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    first_name = models.CharField(max_length=100,default='rabi')
    last_name = models.CharField(max_length=100,default='rabii')
    email = models.EmailField(blank=True,default='rabi@gmail.com')

    phone = models.CharField(max_length=20, blank=True)
    project_type = models.CharField(max_length=200, blank=True)
    budget = models.CharField(max_length=200, blank=True)
    timeline = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=200, blank=True)

    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()

    status = models.CharField(max_length=20, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Contact Forms"
    def is_pending(self):
        return self.status in ['new', 'pending']
    
    def is_replied(self):
        return self.status == 'replied'


 