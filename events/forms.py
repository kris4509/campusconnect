from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "title", "description", "external_registration_url", "poster", "category", "venue", "event_date",
            "start_time", "end_time", "ticket_price", "maximum_tickets",
            "registration_deadline",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "registration_deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
