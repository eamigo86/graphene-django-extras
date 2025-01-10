import django
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

if django.VERSION >= (2, 0):
    from django.urls import path

    urlpatterns = [
        path("admin/", admin.site.urls),
        path(
            "graphql", csrf_exempt(GraphQLView.as_view(graphiql=True)), name="graphql"
        ),
    ]
else:
    from django.conf.urls import url

    urlpatterns = [
        url("admin/", admin.site.urls),
        url("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True)), name="graphql"),
    ]
