from django.urls import path
from .views import (
    LoginAPIView,
    CategoryListCreateView, CategoryDetailView,
    TagListCreateView, TagDetailView,
    ProductListCreateView, ProductDetailView,
    ProductImageListCreateView, ProductImageDetailView,
    ProfileListView, ProfileDetailView,
    AdminDashboardView,ProductStatsView,
)

urlpatterns = [
    # Auth
    path("login/", LoginAPIView.as_view()),

    # Categories
    path("categories/", CategoryListCreateView.as_view()),
    path("categories/<int:pk>/", CategoryDetailView.as_view()),

    # Tags
    path("tags/", TagListCreateView.as_view()),
    path("tags/<int:pk>/", TagDetailView.as_view()),

    # Products
    path("products/", ProductListCreateView.as_view()),
    path("products/<int:pk>/", ProductDetailView.as_view()),

    # Product Images
    path("productimages/", ProductImageListCreateView.as_view()),
    path("productimages/<int:pk>/", ProductImageDetailView.as_view()),

    # Profiles
    path("profiles/", ProfileListView.as_view()),
    path("profile/", ProfileDetailView.as_view()),

    # Admin Dashboard
    path("dashboard/", AdminDashboardView.as_view()),

    # Product Stats
    path("product_stats/", ProductStatsView.as_view()),


]
