import math

from rest_framework import pagination
from rest_framework.response import Response


class DokoolaPaginator(pagination.PageNumberPagination):
    page_size = 15

    def get_paginated_response(self, data):
        response = Response(
            {
                "page_size": self.page_size,  # The number of objects per page
                "page_index": self.page.number,  # The current page number
                "pages_count": self.page.paginator.num_pages,  # The total number of pages
                "objects_count": self.page.paginator.count,  # The total number of objects
                "links": {
                    "next": self.get_next_link(),
                    "prev": self.get_previous_link(),
                },
                "payload": data,  # The actual data
            }
        )
        return response
