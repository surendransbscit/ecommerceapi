from rest_framework.response import Response

def paginate_queryset(queryset, request, serializer_class):
    # print("Pquary",request, queryset, serializer_class)
    # Get params
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))

    # Count & slice
    total_records = queryset.count()
    total_pages = (total_records + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size

    queryset = queryset[start:end]

    # Serialize
    serializer = serializer_class(queryset, many=True)
    # print("serializer", serializer)
    # print("serializer oda data", serializer.data)

    return Response({
        "total_records": total_records,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "results": serializer.data
    })
