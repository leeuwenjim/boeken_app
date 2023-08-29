from typing import Optional
from rest_framework.pagination import BasePagination
from rest_framework.settings import api_settings
from rest_framework.response import Response

"""
usage:

return ApiRestPagination(
        page_size=20, <- better to set api_settings.PAGE_SIZE in most cases
    )
    .paginate(
        query_set=<YOUR_QUERYSET>, 
        request=<REQUEST_OBJECT>, 
        serializer=<SERIALIZER_CLASS TO USE>
    )

"""
#return

class ApiRestPagination(BasePagination):
    def __init__(self, page_size: Optional[int] = None, page_query_param: Optional[str] = None,
                 page_size_query_param: Optional[str] = None) -> None:
        super().__init__()

        self.page_size = page_size
        if page_size is None:
            self.page_size = api_settings.PAGE_SIZE if api_settings.PAGE_SIZE is not None else 50

        self.page_query_param = page_query_param
        if page_query_param is None:
            self.page_query_param = 'page'

        self.page_size_query_param = page_size_query_param
        if self.page_size_query_param is None:
            self.page_size_query_param = 'page_size'

    def __get_navigation_page_list(self):
        if self.amount <= 5:
            return list(range(1, self.amount + 1))
        navigation_indexes = {1, self.page - 1, self.page, self.page + 1, self.amount}
        if self.page <= 3:
            navigation_indexes.add(2)
            navigation_indexes.add(3)
        if self.page >= self.amount - 2:
            navigation_indexes.add(self.amount - 1)
            navigation_indexes.add(self.amount - 2)

        result = [
            index for index in sorted(navigation_indexes) if 0 < index <= self.amount
        ]

        if self.page >= 4:
            result.insert(1, None)
        if self.page <= self.amount - 3:
            result.insert(len(result) - 1, None)

        return result

    def __create_page_url(self, page, add_page_size_param):
        url = self.request.path + f'?{self.page_query_param}={page}'
        if add_page_size_param:
            url += f'&{self.page_size_query_param}={self.page_size}'
        for query_param in self.request.query_params:
            if query_param == self.page_query_param or query_param == self.page_size_query_param:
                continue
            url += f'&{query_param}={self.request.query_params[query_param]}'
        return url

    def __create_result(self, data):
        has_next = self.page < self.amount
        has_previous = self.page > 1

        add_page_size_to_url = self.page_size_query_param in self.request.query_params

        return {
            'count': self.count,
            'page_count': self.amount,
            'page_size': self.page_size,
            'current': self.page,
            'next': self.__create_page_url(self.page - 1, add_page_size_to_url) if has_next else None,
            'previous': self.__create_page_url(self.page + 1, add_page_size_to_url) if has_previous else None,
            'navigation': [
                {
                    'page': page_number,
                    'url': None if page_number is None else self.__create_page_url(page_number, add_page_size_to_url)
                } for page_number in self.__get_navigation_page_list()
            ],
            'results': data,
        }

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.count = len(queryset)

        if self.page_size_query_param is not None and self.page_size_query_param in request.query_params:
            try:
                new_page_size = int(request.query_params.get(self.page_size_query_param, self.page_size))
            except ValueError:
                new_page_size = 0
            if new_page_size >= 1:
                self.page_size = new_page_size

        self.amount = ((self.count // self.page_size) + 1) if self.count % self.page_size else (
        self.count // self.page_size)

        try:
            page = int(request.query_params.get(self.page_query_param, '1'))
        except:
            page = 0
        if page < 1:
            page = 1
        page = min(page, self.amount)
        self.page = page

        if self.count > 1:
            start = (page - 1) * self.page_size
            end = min(start + self.page_size, self.count)

            return queryset[start:end]

        return queryset

    def get_paginated_response(self, data):
        return Response(self.__create_result(data), status=200)

    def paginate(self, request, query_set, serializer):
        data = self.paginate_queryset(query_set, request)
        serialized_data = serializer(data, many=True, context={'request': request})
        return self.get_paginated_response(serialized_data.data)
