from django.test import Client as BaseClient
from asgiref.sync import async_to_sync
from django.urls import reverse


class Client(BaseClient):
    url = reverse("graphql")

    def query(self, query):
        response = async_to_sync(self.get(path=self.url, data={"query": query}))
        return response
