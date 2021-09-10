from rest_framework import pagination


class UserListPagination(pagination.PageNumberPagination):
    page_size = 12
