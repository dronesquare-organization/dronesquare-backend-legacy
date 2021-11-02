from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Users, Storages, Payment


# Register your models here.
class UsersAdmin(admin.ModelAdmin):
    list_display = ('email',)


class StoragesAdmin(admin.ModelAdmin):
    list_display = ('email',)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('email', 'account', 'bank',)


admin.site.register(Users, UsersAdmin)
admin.site.unregister(Group)
admin.site.register(Storages, StoragesAdmin)
admin.site.register(Payment, PaymentAdmin)
