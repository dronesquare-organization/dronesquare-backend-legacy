from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=False):
        user = super().save_user(request, user, form, commit)
        data = form.cleaned_data
        user.name = data.get('name')
        user.sectors = data.get('sectors')
        user.organization = data.get('organization')
        user.phoneNumber = data.get('phoneNumber')
        user.save()
        return user
