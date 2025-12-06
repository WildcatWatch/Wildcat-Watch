from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from myapp.models import Duty, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Saves reminders to the database for duties starting in the next 30 minutes.'

    def handle(self, *args, **options):
        now = timezone.localtime()
        reminder_start_time = now + timedelta(minutes=1)
        reminder_end_time = now + timedelta(minutes=30)

        duties_to_remind = Duty.objects.filter(
            time_start__gte=reminder_start_time,
            time_start__lte=reminder_end_time,
            status='pending'
        ).select_related('staff')

        if not duties_to_remind:
            self.stdout.write(self.style.SUCCESS('No duties found requiring reminders.'))
            return

        sent_count = 0
        for duty in duties_to_remind:
            
            if Notification.objects.filter(related_duty=duty, created_at__date=now.date()).exists():
                 continue

            start_time_display = timezone.localtime(duty.time_start).strftime("%H:%M %p")
            
            message = (
                f"REMINDER: Your duty '{duty.title}' at {duty.location} "
                f"is scheduled to start soon at {start_time_display}."
            )

            Notification.objects.create(
                user=duty.staff,
                related_duty=duty, 
                message=message
            )
            
            self.stdout.write(self.style.WARNING(f'Reminder saved for {duty.staff.fullname}.'))
            sent_count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully saved {sent_count} shift start reminders.'))