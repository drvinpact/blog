from django.shortcuts import redirect

class AuthorCheckMixin(object):
    failure_path = '/'

    def check_author(self, user):
        if user.is_authenticated:
            return (self.object.author==user)
        return False

    def check_author_failed(self, request, *args, **kwargs):
        return redirect(self.failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_author(request.user):
            return self.check_author_failed(request, *args, **kwargs)
        return super(AuthorCheckMixin, self).dispatch(request, *args, **kwargs)
    
