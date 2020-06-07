from django.test import Client as BaseClient
from django.urls import reverse


class Client(BaseClient):
    url = reverse("graphql")

    def query(self, query):
        response = self.get(path=self.url, data={"query": query})
        return response

    def mutate(self, payload):
        response = self.post(path=self.url, data=payload, content_type='application/json')
        return response
