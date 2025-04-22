from datetime import date, timedelta, datetime, time
from calendar import Calendar, monthrange
from django.shortcuts import render, redirect
from django.http import HttpResponse
from icalendar import Calendar as iCalendar, Event
from django.utils.timezone import now as django_now
from zoneinfo import ZoneInfo
from .models import Assignment
from .forms import AssignmentForm




def dashboard(request):
   tz_name = request.COOKIES.get('user_timezone', 'UTC')
   tz = ZoneInfo(tz_name)
   now = django_now().astimezone(tz)
   today = now.date()


   # Get selected month and year from query params, or default to current
   year = int(request.GET.get('year', today.year))
   month = int(request.GET.get('month', today.month))


   if month > 12:
       month = 1
       year += 1
   elif month < 1:
       month = 12
       year -= 1


   cal = Calendar(firstweekday=0)
   month_days = cal.monthdatescalendar(year, month)


   calendar_weeks = []
   for week in month_days:
       week_data = []
       for day in week:
           if day.month == month:
               assignments = Assignment.objects.filter(due_date=day)
               week_data.append({
                   'day': day,
                   'assignments': assignments,
               })
           else:
               week_data.append(None)
       calendar_weeks.append(week_data)


   start_of_month = date(year, month, 1)
   end_of_month = date(year, month, monthrange(year, month)[1])


   def get_progress(qs):
       total = qs.count()
       done = qs.filter(completed=True).count()
       return (done / total * 100) if total > 0 else 0


   month_assignments = Assignment.objects.filter(due_date__range=(start_of_month, end_of_month))


   start_of_week = today - timedelta(days=today.weekday())
   end_of_week = start_of_week + timedelta(days=6)
   week_assignments = Assignment.objects.filter(due_date__range=(start_of_week, end_of_week))


   start_of_day = datetime.combine(today, time.min)
   end_of_day = datetime.combine(today, time.max)
   day_assignments = Assignment.objects.filter(due_date__range=(start_of_day.date(), end_of_day.date()))


   context = {
       'calendar_weeks': calendar_weeks,
       'month_progress': get_progress(month_assignments),
       'week_progress': get_progress(week_assignments),
       'day_progress': get_progress(day_assignments),
       'today': today,
       'current_month': month,
       'current_year': year,
   }


   return render(request, 'dashboard.html', context)




def add_assignment(request):
   if request.method == 'POST':
       form = AssignmentForm(request.POST)
       if form.is_valid():
           form.save()
           return redirect('dashboard')
   else:
       form = AssignmentForm()


   return render(request, 'add_assignment.html', {'form': form})




def add_assignment_with_date(request, due_date):
   if isinstance(due_date, str):
       due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
   else:
       due_date_obj = due_date


   if request.method == 'POST':
       form = AssignmentForm(request.POST)
       if form.is_valid():
           assignment = form.save(commit=False)
           assignment.due_date = due_date_obj
           assignment.save()
           return redirect('dashboard')
   else:
       form = AssignmentForm(initial={'due_date': due_date_obj})


   return render(request, 'add_assignment.html', {'form': form})




def edit_assignment(request, id):
   assignment = Assignment.objects.get(id=id)
   if request.method == 'POST':
       form = AssignmentForm(request.POST, instance=assignment)
       if form.is_valid():
           form.save()
           return redirect('dashboard')
   else:
       form = AssignmentForm(instance=assignment)


   return render(request, 'edit_assignment.html', {'form': form, 'assignment': assignment})




def export_calendar(request):
   cal = iCalendar()
   cal.add('prodid', '-//Assignment Tracker//')
   cal.add('version', '2.0')


   assignments = Assignment.objects.all()
   for assignment in assignments:
       event = Event()
       event.add('summary', assignment.title)
       event.add('description', assignment.description or "")
       event.add('dtstart', assignment.due_date)
       event.add('dtend', assignment.due_date)
       event.add('dtstamp', datetime.now())
       cal.add_component(event)


   response = HttpResponse(cal.to_ical(), content_type='text/calendar')
   response['Content-Disposition'] = 'attachment; filename=assignments.ics'
   return response
