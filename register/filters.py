from django_filters import filters
from django_filters import FilterSet
from .models import Diary


class MyOrderingFilter(filters.OrderingFilter):
    descending_fmt = '%s （降順）'


class ItemFilter(FilterSet):

    pass

    class Meta:

        model = Diary
        fields = ('title','text')