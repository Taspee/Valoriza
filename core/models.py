from django.db import models

# Create your models here.
class Industry(models.Model):
    """Tabla maestra de industrias (sin duplicados)"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Industries"


class Sub_industry(models.Model):
    """Tabla maestra de sub-industrias"""
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name='sub_industries')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.industry.name} - {self.name}"
    
    class Meta:
        unique_together = ['industry', 'name']
        verbose_name_plural = "Sub Industries"


class Enterprise(models.Model):
    """Empresas con referencias a industria y sub-industria"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, default='Chile')
    website = models.URLField(blank=True, null=True)
    
    # Referencias a industrias
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True, related_name='enterprises')
    sub_industry = models.ForeignKey(Sub_industry, on_delete=models.SET_NULL, null=True, blank=True, related_name='enterprises')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        
    def __str__(self):
        return self.name


class Contact(models.Model):
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    contacted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.enterprise.name}"

