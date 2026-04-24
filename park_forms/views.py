from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import json
import csv
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from .models import ParkEntryForm


def index(request):
    """Main form page"""
    return render(request, 'index.html')


@method_decorator(csrf_exempt, name='dispatch')
class SubmitFormView(View):
    """Handle form submissions"""

    def post(self, request):
        form_type = request.POST.get('form_type', '')
        visitor_type = request.POST.get('visitor_type', '')

        # Build structured payload
        payload = {}

        # Handle clients
        clients = []
        names = request.POST.getlist('client_name[]')
        contacts = request.POST.getlist('client_contact[]')
        nationalities = request.POST.getlist('client_nationality[]')

        for i in range(max(len(names), len(contacts), len(nationalities))):
            client = {}
            if i < len(names) and names[i].strip():
                client['name'] = names[i].strip()
            if i < len(contacts) and contacts[i].strip():
                client['contact'] = contacts[i].strip()
            if i < len(nationalities) and nationalities[i].strip():
                client['nationality'] = nationalities[i].strip()
            if client:
                clients.append(client)

        if clients:
            payload['clients'] = clients

        # Handle vehicles
        vehicles = []
        vehicle_types = request.POST.getlist('car_type[]')
        vehicle_regs = request.POST.getlist('car_reg[]')
        driver_names = request.POST.getlist('driver_name[]')
        driver_phones = request.POST.getlist('driver_phone[]')

        for i in range(max(len(vehicle_types), len(vehicle_regs), len(driver_names), len(driver_phones))):
            vehicle = {}
            if i < len(vehicle_types) and vehicle_types[i].strip():
                vehicle['type'] = vehicle_types[i].strip()
            if i < len(vehicle_regs) and vehicle_regs[i].strip():
                vehicle['reg'] = vehicle_regs[i].strip()
            if i < len(driver_names) and driver_names[i].strip():
                vehicle['driver_name'] = driver_names[i].strip()
            if i < len(driver_phones) and driver_phones[i].strip():
                vehicle['driver_phone'] = driver_phones[i].strip()
            if vehicle:
                vehicles.append(vehicle)

        if vehicles:
            payload['vehicles'] = vehicles

        # Handle activities
        activities = request.POST.getlist('activities')
        if activities:
            payload['activities'] = activities

        # Handle other fields
        for key in request.POST:
            if key in ('client_name[]', 'client_contact[]', 'client_nationality[]',
                      'car_type[]', 'car_reg[]', 'driver_name[]', 'driver_phone[]',
                      'activities', 'form_type', 'visitor_type'):
                continue
            if request.POST.get(key):
                payload.setdefault('fields', {})
                payload['fields'][key] = request.POST.get(key)

        # Save to database
        form_entry = ParkEntryForm.objects.create(
            form_type=form_type,
            visitor_type=visitor_type,
            data=payload
        )

        # Generate PDF
        pdf_buffer = self.generate_pdf(form_entry.id, form_type, visitor_type, payload)

        # Return PDF for download
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="park_entry_{form_entry.id}.pdf"'
        return response

    def generate_pdf(self, form_id, form_type, visitor_type, data_dict):
        """Generate PDF for form submission"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Header
        elements.append(Paragraph("<b>UGANDA WILDLIFE AUTHORITY</b>", styles['Heading1']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>Form ID:</b> {form_id}", styles['Normal']))
        elements.append(Paragraph(f"<b>Form Type:</b> {form_type}", styles['Normal']))
        elements.append(Paragraph(f"<b>Visitor Type:</b> {visitor_type}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Data table
        table_data = [["Field", "Value"]]

        def add_row(k, v):
            if isinstance(v, list):
                vstr = ", ".join([str(x) for x in v])
            elif isinstance(v, dict):
                vstr = json.dumps(v, indent=2)
            else:
                vstr = str(v)
            table_data.append([k, vstr])

        # Add clients, vehicles, activities first
        for key in ["clients", "vehicles", "activities"]:
            if key in data_dict:
                add_row(key.title(), data_dict[key])

        # Add other fields
        for k, v in data_dict.items():
            if k not in ("clients", "vehicles", "activities"):
                add_row(k, v)

        table = Table(table_data, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        return buffer


def admin_dashboard(request):
    """Admin dashboard with form records"""
    # Get filter parameters
    form_type = request.GET.get('form_type', '')
    visitor_type = request.GET.get('visitor_type', '')
    search_query = request.GET.get('q', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    # Base queryset
    forms = ParkEntryForm.objects.all()

    # Apply filters
    if form_type:
        forms = forms.filter(form_type=form_type)
    if visitor_type:
        forms = forms.filter(visitor_type=visitor_type)
    if from_date:
        forms = forms.filter(date_submitted__date__gte=from_date)
    if to_date:
        forms = forms.filter(date_submitted__date__lte=to_date)

    # Apply search
    if search_query:
        # Search in JSON data
        forms = forms.filter(data__icontains=search_query)

    # Pagination
    paginator = Paginator(forms, 25)  # 25 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'forms': page_obj,
        'form_type': form_type,
        'visitor_type': visitor_type,
        'search_query': search_query,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, 'admin.html', context)


def view_form(request, form_id):
    """View individual form details"""
    form_entry = get_object_or_404(ParkEntryForm, id=form_id)
    return render(request, 'view_form.html', {'form_entry': form_entry})


def export_csv(request):
    """Export all forms to CSV"""
    forms = ParkEntryForm.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="park_entries.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Form Type', 'Visitor Type', 'Date Submitted', 'Data'])

    for form in forms:
        writer.writerow([
            form.id,
            form.form_type,
            form.visitor_type,
            form.date_submitted,
            json.dumps(form.data)
        ])

    return response


def stats_api(request):
    """API endpoint for statistics"""
    # By visitor type
    visitor_stats = ParkEntryForm.objects.values('visitor_type').annotate(
        count=Count('id')
    ).order_by('-count')

    by_type = {item['visitor_type']: item['count'] for item in visitor_stats}

    # By period
    now = timezone.now()
    periods = {
        'today': ParkEntryForm.objects.filter(date_submitted__date=now.date()).count(),
        'week': ParkEntryForm.objects.filter(date_submitted__gte=now - timedelta(days=7)).count(),
        'month': ParkEntryForm.objects.filter(date_submitted__gte=now - timedelta(days=30)).count(),
        'quarter': ParkEntryForm.objects.filter(date_submitted__gte=now - timedelta(days=90)).count(),
        'year': ParkEntryForm.objects.filter(date_submitted__gte=now - timedelta(days=365)).count(),
    }

    return JsonResponse({
        'by_type': by_type,
        'by_period': periods
    })