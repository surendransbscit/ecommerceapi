from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Sum, Q, Count, Avg
from django.shortcuts import get_object_or_404
from knox.models import AuthToken
from django.db import connection
from .models import Category, Tag, Profile, Product, ProductImage
from .serializers import (
    UserSerializer, CategorySerializer, TagSerializer, ProfileSerializer,
    ProductSerializer, ProductImageSerializer
)
from utils.pagination import paginate_queryset


# Login

class LoginAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        # print(User)

        user = User.objects.filter(username=username).first() # Use first() to get a single user or None
        # print("user", user)
        if not user:
            return Response({"error": "Invalid username"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        
        token = AuthToken.objects.create(user)[1]
        # print(UserSerializer)
        # print("user data", UserSerializer(user).data)
        # print("token", token)
        return Response({"user": UserSerializer(user).data, "token": token})



# Custom Permission

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff


# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


    def get(self, request):
        # print(request)
        queryset = self.get_queryset()
        # print(queryset)
        # print(self.serializer_class)
        return paginate_queryset(queryset, request, self.serializer_class)

    def post(self, request):
        # print("request iruthu get", request.data)
        serializer = self.serializer_class(data=request.data)
        # print("serializer", serializer)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # print("serializer data", serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, pk):
        # print(request)
        # print(self.get_queryset())
        category = get_object_or_404(self.get_queryset(), pk=pk)# get_queryset based on pk used get object illa naa 404 error
        # print("category", category)
        serializer = self.serializer_class(category)
        # print("serializer", serializer.data)
        return Response(serializer.data)

    def put(self, request, pk):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        # print("category", category)
        serializer = self.serializer_class(category, data=request.data, partial=True)
        # print("serializer", serializer)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # print("serializer data", serializer.data)
        return Response(serializer.data)

    def delete(self, request, pk):
        # print("request", request)
        category = get_object_or_404(self.get_queryset(), pk=pk)
        # print("category", category)
        category.delete()
        # if category is not None:
            # print("delete")
        return Response({f"message":"delete successfully"},status=status.HTTP_204_NO_CONTENT)



# Tag Views

class TagListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get(self, request):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get(self, request, pk):
        tag = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(tag)
        return Response(serializer.data)

    def put(self, request, pk):
        tag = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(tag, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        tag = get_object_or_404(self.get_queryset(), pk=pk)
        tag.delete()
        return Response({"message":"Delete Sucessfully"},status=status.HTTP_204_NO_CONTENT)



# Product Views

class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request):
        products = self.queryset
        # print("products", products)

        # Filtering by category
        category_name = request.GET.get("category_name")
        if category_name:
            products = products.filter(category__name__icontains=category_name)

        # Filtering
        price_min = request.GET.get("price_min")
        price_max = request.GET.get("price_max")
        released_on = request.GET.get("released_on")
        in_stock = request.GET.get("in_stock")

        if price_min:
            products = products.filter(price__gte=price_min)
        if price_max:
            products = products.filter(price__lte=price_max)
        if released_on:
            products = products.filter(released_on=released_on)
        if in_stock:
            if in_stock.lower() in ["true", "1"]:
                products = products.filter(in_stock=True)
            elif in_stock.lower() in ["false", "0"]:
                products = products.filter(in_stock=False)

        # Search
        search = request.GET.get("search")
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(category__name__icontains=search)
            )

        return paginate_queryset(products, request, self.serializer_class)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, pk):
        # print("request", request)
        product = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        # print("request", request)
        product = get_object_or_404(self.get_queryset(), pk=pk)
        product.delete()
        return Response({"message":"Delete Successfully"},status=status.HTTP_204_NO_CONTENT)


# Product Image Views

class ProductImageListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get(self, request):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get(self, request, pk):
        img = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(img)
        return Response(serializer.data)

    def put(self, request, pk):
        img = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(img, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        # print("request", request)
        img = get_object_or_404(self.get_queryset(), pk=pk)
        # print("img", img)
        img.delete()
        return Response({"message":"Delete Successfully"},status=status.HTTP_204_NO_CONTENT)


# Profile Views

class ProfileListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get(self, request):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request):
        # print("req val",request.user)
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)
        
        serializer = self.serializer_class(profile)
        return Response(serializer.data)

    def put(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        serializer = self.serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



# Admin Dashboard

class AdminDashboardView(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_products = Product.objects.count()
        total_price = Product.objects.aggregate(Sum("price"))["price__sum"] or 0
        total_categories = Category.objects.count()
        total_stock = Product.objects.filter(in_stock=True).count()
        total_users = User.objects.count()

        dats={
            "total_products": total_products,
            "total_price": total_price,
            "total_categories": total_categories,
            "total_stock": total_stock,
            "total_users":total_users
        }
        return Response(dats, status=status.HTTP_200_OK)


# Product Aggregation Stats
class ProductStatsView(APIView):
    def get(self, request):
        stats = Product.objects.aggregate(
            total_products=Count('id'),
            avg_price=Avg('price'),
            total_price=Sum('price'),
            total_in_stock=Count('id', filter=Q(in_stock=True)),
            total_out_of_stock=Count('id', filter=Q(in_stock=False))

        )
        return Response(stats, status=status.HTTP_200_OK)







    






