from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.views.generic.edit import CreateView, FormView, ListView, UpdateView
from .forms import EventForm, EventPromoteForm
from .models import Chapter, Event, EventType, OUR_REVOLUTION_CHAPTER_ID
from .auth import Constituent
from hydra.models import EventPromotionRequest
import datetime


class EventsView(ListView):
    model = Event

    def get_queryset(self, request):
        return Event.objects.filter(start_day__gte=datetime.date.today())

    def get_context_data(self, request, *args, **kwargs):
        context = super(EventsView, self).get_context_data(request, *args, **kwargs)
        context['past_events'] = Event.objects.filter(start_day__lt=datetime.date.today())
        return context


class EventCreate(CreateView):
    model = Event
    form_class = EventForm
    template_name = "event_form.html"
    success_url = '/'
    
    def get_initial(self, *args, **kwargs):
        
        initial = {
            'chapter': Chapter.objects.get(pk=OUR_REVOLUTION_CHAPTER_ID),
            'start_day': datetime.date.today() + datetime.timedelta(days=4),
            'start_time': datetime.time(hour=17, minute=0, second=0),
            'capacity': 0,
            'host_receive_rsvp_emails': 1,
            'public_phone': 1,
        }
        
        if self.request.user.is_authenticated():
            initial['creator_cons'] = self.request.user.pk
            initial['creator_name'] = ' '.join([self.request.user.firstname, self.request.user.lastname])
        
        return initial

    def form_valid(self, form):
        #
        return super(EventCreate, self).form_valid(form)
        
        
class EventCreatorMixin(object):
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if self.request.user.has_perm('bsd.can_edit_own_%ss' % self.model._meta.verbose_name.lower(), obj=self.get_object()):
            return super(EventCreatorMixin, self).dispatch(*args, **kwargs)
        return render(self.request, "unauthorized.html", {'object_type': self.model._meta.verbose_name.lower()}, status=401)



class EventEdit(EventCreatorMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'event_form.html'
    success_url = '/events'
    
    

class EventPromote(EventCreatorMixin, CreateView):
    # hack for EventCreator permissions mixin
    model = Event
    
    # actual model is the request, as set on the form.
    form_class = EventPromoteForm
    success_url = "/events"
    template_name = "promote.html"
    
    def form_invalid(self, form):
        import ipdb; ipdb.set_trace()
    
    def get_initial(self, *args, **kwargs):
        event = Event.objects.get(pk=self.kwargs['pk'])

        return {
                    'event': event,
                    'volunteer_count': 100 if event.capacity == 0 else event.capacity * 2,
                    'subject': "Please come to my %s event" % event.event_type.name,
                    'message': """Hello --
                    
I'm hoping to get more attendees at my event, %(name)s. Could you please come?

Thanks!

%(creator_name)s""" % dict(event.__dict__)}