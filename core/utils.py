import coreapi
import coreschema
from rest_framework import filters


class SwaggerOrderingFilter(filters.OrderingFilter):
    def get_schema_fields(self, view):
        self.ordering_description = "Fields for sorting: " + ", ".join(view.ordering_fields)
        return super().get_schema_fields(view)


class SwaggerSearchFilter(filters.SearchFilter):
    def get_schema_fields(self, view):
        sf_result = str(super().get_search_fields(view, None))
        sf_result = sf_result.replace("'", "").replace("(", "").replace(")", "").replace("__", "/")

        result = super().get_schema_fields(view)
        newField = coreapi.Field(
            name=result[0].name,
            required=result[0].required,
            location=result[0].location,
            schema=coreschema.String(title="Search", description="Word Search within these fields: " + sf_result),
        )
        return [newField]
