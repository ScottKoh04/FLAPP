from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.loginUser, name="login"),
    path("logout/", views.logoutUser, name="logout"),

    path("", views.home, name="home"),
    path("products/", views.products, name="products"),
    path('create-product/', views.createProduct, name="create-product"),
    path('update-product/<str:pk>/', views.updateProduct, name="update-product"),

    path("orders/", views.orders, name="orders"),
    #CRUD for orders
    path('create-order/', views.createOrder, name="create-order"),
    path("retrieve-order/<str:pk>/", views.retrieveOrder, name="retrieve-order"),
    path('update-order/<str:pk>/', views.updateOrder, name="update-order"),
    path('delete-order/<str:pk>/', views.deleteOrder, name="delete-order"),

    path("customers/", views.customers, name="customers"),
    path('create-customer/', views.createCustomer, name="create-customer"),
    path('update-customer/<str:pk>/', views.updateCustomer, name="update-customer"),
    path('delete-customer/<str:pk>/', views.deleteCustomer, name="delete-customer"),

    path("users/", views.users, name="users"),
    path("invoices/", views.invoices, name="invoices"),
    path("generateInvoices/", views.generateInvoices, name="generateInvoices"),
    #path("singleInvoice/", views.singleInvoice, name="singleInvoice"),

    #path("singleInvoice/<str:pk>/", views.singleInvoice, name="singleInvoice"),

    path('pdf_view/<pk>/', views.render_pdf_view, name='pdf_view')]

