from collections.abc import Mapping, Iterable
from .models import Serie


def validate_book_order_field(data: Mapping, serie: Serie):
    field_name = 'book_order'
    errors = []

    if field_name not in data:
        return ['This field is required', ]

    if not isinstance(data[field_name], Iterable):
        return ['This field must be an iterable with book id\'s in order']


    for index, item in enumerate(data[field_name]):
        if not isinstance(item, int):
            errors.append(f'Non-integer found at index {index} in book_order. Found value: {item}')
            continue

        if not serie.books.filter(pk=item).exists():
            errors.append(f'Book with id {item} is not a part of this serie')
            continue

    return errors
