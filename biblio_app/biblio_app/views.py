from functools import wraps
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request


def allow_zero(func):
    func.allow_zero = True
    @wraps(func)
    def inner_wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return inner_wrapper


def protect(func):
    @wraps(func)
    def inner_wrapper(request: Request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return Response(status=401) # 401_UNAUTHENTICATED
    return inner_wrapper


# This class is a real simple extension of the rest_framework.views.APIView class
# The only this that is different is that 3 attributes must be set:
# model: Class of which the view is a model
# id_name: Name through which the id of the object is given in the url
# keyword: By what keyword should the view-functions receive the object
#
# The big advantage is that DetailApiView classes no longer need to check in every function if the given object
# (through id) does exist or not. This function will return an empty 404 response if the object is not found.
# By doing the object lookup in this class will reduce overhead as in: not every view function a check must be done anymore
class DetailApiView(APIView):

    def dispatch(self, request, *args, **kwargs):
        """
        `.dispatch()` is pretty much the same as Django's regular dispatch,
        but with extra hooks for startup, finalize, and exception handling.
        """

        if not(hasattr(self, 'model') and hasattr(self, 'keyword') and hasattr(self, 'id_name')):
            raise RuntimeError(
                'While using DetailApiView you must set the `model`, `keyword` and `id_name` attribute'
            )

        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(),
                                  self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            if self.id_name not in kwargs:
                raise Exception(f'{self.id_name} not found in the request')

            try:
                object_set = False
                if hasattr(handler, 'allow_zero'):
                    if handler.allow_zero:
                        if kwargs[self.id_name] == 0:
                            object = None
                            object_set = True
                if not object_set:
                    object = self.model.objects.get(id=kwargs[self.id_name])
                del kwargs[self.id_name]
                kwargs[self.keyword] = object
                response = handler(request, *args, **kwargs)
            except self.model.DoesNotExist:
                response = Response(status=404)


        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response