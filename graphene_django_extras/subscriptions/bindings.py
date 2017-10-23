# -*- coding: utf-8 -*-
from channels_api.bindings import ResourceBindingBase, ResourceBinding

from .mixins import DjangoGraphqlBindingMixin, UnsubscribeMixin

__author__ = 'Ernesto'


class SubscriptionResourceBinding(DjangoGraphqlBindingMixin, ResourceBindingBase):
    # mark as abstract
    model = None


class ExtraResourceBinding(UnsubscribeMixin, ResourceBinding):
    # mark as abstract
    model = None
