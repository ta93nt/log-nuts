from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from lognutsapp.models import Subject, PersonalLog, FoodImage

class SubjectInline(admin.StackedInline):
    model = Subject
    can_delete = False
    verbose_name_plural = 'subject'

class UserAdmin(BaseUserAdmin):
    inlines = (SubjectInline,)

class PersonalLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'food_name', 'restaurant', 'size', 'energie', 'protein', 'fat', 'carbohydrate', 'date')

class FoodImageAdmin(admin.ModelAdmin):
    list_display = ('created_date', 'user', 'url', 'pfc_diff')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(PersonalLog, PersonalLogAdmin)
admin.site.register(FoodImage, FoodImageAdmin)