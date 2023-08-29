from rest_framework.request import Request
from collections.abc import Sequence, Mapping, Iterable
from typing import Optional, Callable
from django.db.models import Q, Field, ManyToManyField, IntegerField, CharField, ForeignKey, Model
from django.core.exceptions import FieldDoesNotExist
import random
from .models import Book


def __save_int(value: str):
    try:
        return int(value)
    except ValueError:
        return None

class MockCharField(Field):
    def __init__(self, name):
        self.name = name

def __generate_charfield_filter(field: Field, param: str, value: str) -> Q:
    field_filter = field.name + '__icontains'
    return Q(**{field_filter: value})


def __generate_choises_filter(field: Field, param: str, value: str) -> Q:
    options = {option[0] for option in field.choices}
    search_options = value.split(',')
    result = Q()
    filters = [Q(**{field.name: search_option}) for search_option in search_options if search_option in options]
    for search_filter in filters:
        result = result | search_filter
    return Q(result)


def __generate_foreign_key_filter(field: Field, param: str, value: str) -> Q:
    return Q(**{field.name + '_id__in': list(filter(lambda x: x is not None, [__save_int(splitted_part) for splitted_part in value.split(',')]))})


def __generate_integerfield_filter(field: Field, param: str, value: str) -> Q:
    try:
        casted_value = int(value)
    except ValueError:
        return Q()

    if param == field.name:
        return Q(**{field.name: casted_value})
    allowed_compares = ['gt', 'gte', 'lt', 'lte']
    compare = param.rsplit('_', 1)[1]

    if compare in allowed_compares:
        return Q(**{field.name + '__' + compare: casted_value})

    return Q()


def __generate_m2m_filter(field: Field, param: str, value: str) -> Q:
    return Q(**{field.name + '__in': list(filter(lambda x: x is not None, [__save_int(splitted_part) for splitted_part in value.split(',')]))})


def __field_to_function(field: Field) -> Optional[Callable[[Field, str], Q]]:
    if isinstance(field, CharField):
        if field.choices is None:
            return __generate_charfield_filter
        return __generate_choises_filter
    if isinstance(field, IntegerField):
        return __generate_integerfield_filter
    if isinstance(field, ForeignKey):
        return __generate_foreign_key_filter
    if isinstance(field, ManyToManyField):
        return __generate_m2m_filter

    return None


def generate_filters(model: Model, params: Mapping, field_names: Iterable, non_field_names: Iterable = None, use_or: bool = False) -> Q:
    result = Q()

    if non_field_names is None:
        non_field_names = list()

    for param in params:
        if param in field_names or param in non_field_names:
            field_name = param
        elif param.rsplit('_', 1)[0] in field_names:
            field_name = param.rsplit('_', 1)[0]
        else:
            continue

        try:
            field = model._meta.get_field(field_name)
        except FieldDoesNotExist:
            if field_name in non_field_names:
                if use_or:
                    result = result | __generate_charfield_filter(MockCharField(field_name), param, params[param])
                else:
                    result = result & __generate_charfield_filter(MockCharField(field_name), param, params[param])
            continue
        if use_or:
            result = result | __field_to_function(field)(field, param, params[param])
        else:
            result = result & __field_to_function(field)(field, param, params[param])

    return result


def get_ordering(request: Request, query_key: str, columns: Sequence) -> str:
    if len(columns) == 0:
        return ''

    if not query_key in request.query_params:
        return columns[0]

    given_ordering: str = request.query_params[query_key]
    column_name = given_ordering
    if given_ordering.startswith('-'):
        column_name = given_ordering[1:]

    if column_name in columns:
        return given_ordering
    return columns[0]


def generate_random_book_selection(amount: int, max_amount: int = 10) -> Sequence:
    amount =  min(amount, max_amount)

    order_options = ['title', 'publish_year', 'isbn']
    order = random.choice(order_options)

    amount_of_books = Book.objects.all().count()
    if amount_of_books < 1:
        return []

    selection_size = max_amount * 10
    start_selection = random.randint(0, max(0, amount_of_books - selection_size))
    end_selection = min(amount_of_books, start_selection + selection_size)

    selection = list(Book.objects.all().order_by(order)[start_selection:end_selection])
    return random.sample(selection, min(amount, len(selection)))