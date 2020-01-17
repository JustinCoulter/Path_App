import json

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Board, Card, Column



from django.views import View
from django.views.generic import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class LearnMore(TemplateView):
    template_name = "learnmore.html"

class NewPath(TemplateView):
    template_name = "newpath.html"


class Home(TemplateView):
    template_name="index.html"

@ensure_csrf_cookie
def index(request):
    return render(request, template_name='kanban/base.html', context={
        'boards': Board.objects.all(),
    })


def new_card(request):
    column_id = int(request.POST.get('column_id'))
    title = request.POST.get('title')
    assert title and column_id
    Card.objects.create(title=title, column_id=column_id)
    return redirect('/')


def view_card(request, card_id, card_slug):
    return render(request, template_name='kanban/view.html', context={
        'boards': Board.objects.all(),
        'current_card': Card.objects.get(id=card_id),
    })


def drop(request):
    payload = json.loads(request.body)
    card_id = int(payload.get('card_id'))
    column_id = int(payload.get('column_id'))
    assert card_id and column_id
    card = Card.objects.get(id=card_id)
    card.column = Column.objects.get(id=column_id)
    card.save()
    return HttpResponse()


class SignUp(View):

    def get(self, request, *args, **kwargs):
        user_form = UserCreationForm()
        profile_form = UserSignUp()


        return render(request, 'signup.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request, *args, **kwargs):
            # load both forms to check validity

        user_form = UserCreationForm(self.request.POST)
        profile_form = UserSignUp(self.request.POST)
        # if both are valid...
        if user_form.is_valid() and profile_form.is_valid():

            # save the user form and log the user in
            # saving triggers the create_user_profile function in the
            # Profile model.
            user = user_form.save(commit=False)
            # user.first_name = profile_form.cleaned_data["first_name"]
            # user.last_name = profile_form.cleaned_data["last_name"]
            user.email = user_form.cleaned_data["username"]
            user.username = user_form.cleaned_data["username"]
            user.save()
            login(request, user)

            # after having created the new row in the Profile model for the new user...
            # re-initiate the profile form with the instance and user_id
            # equal to the current user and save the form
            profile_form = UserSignUp(
                self.request.POST, instance=self.request.user.profile)
            profile = profile_form.save(commit=False)
            profile.user_type = profile_form.cleaned_data["user_type"]
            profile_form.save()

            send_mail(
                'New User has signed up on Booya',
                user.first_name + ' ' + user.last_name + ' signed up with the email ' + user.email,
                os.environ.get('EMAIL'),
                [os.environ.get('ADMIN_EMAIL')],
                fail_silently=False,
            )

            return redirect('/edit_profile')

        else:

            return render(request, 'signup.html', {
                'user_form': user_form,
                'profile_form': profile_form
            })


class Login(FormView):
    template_name = "login.html"
    form_class = AuthenticationForm
    success_url = "/edit_profile/"

    def post(self, request, *args, **kwargs):

        form = self.get_form()
        if form.is_valid():
            user = form.get_user()
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class Logout(FormView):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("/")


