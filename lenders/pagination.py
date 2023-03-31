from rest_framework.views import Response
from rest_framework_json_api.pagination import JsonApiPageNumberPagination


class JsonApiWithSelfLinkPagination(JsonApiPageNumberPagination):

    def get_paginated_response(self, data):
        next = None
        previous = None

        if self.page.has_next():
            next = self.page.next_page_number()
        if self.page.has_previous():
            previous = self.page.previous_page_number()

        return Response(
            {
                "data": data,
                "meta": {
                    "pagination": {
                        "page": self.page.number,
                        "pages": self.page.paginator.num_pages,
                        "count": self.page.paginator.count,
                    }
                },
                "links": {
                    "first": self.build_link(1),
                    "last": self.build_link(self.page.paginator.num_pages),
                    "next": self.build_link(next),
                    "prev": self.build_link(previous),
                    "self": self.request and self.request.build_absolute_uri() or "",
                },
            }
        )
