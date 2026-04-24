from django.contrib import admin
from .models import ParkEntryForm


@admin.register(ParkEntryForm)
class ParkEntryFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'form_type', 'visitor_type', 'date_submitted')
    list_filter = ('form_type', 'visitor_type', 'date_submitted')
    search_fields = ('form_type', 'visitor_type', 'data')
    readonly_fields = ('date_submitted',)
    ordering = ('-date_submitted',)

    fieldsets = (
        ('Form Information', {
            'fields': ('form_type', 'visitor_type', 'date_submitted')
        }),
        ('Form Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Prevent manual creation of forms through admin
        return False