from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

# register urls here
urlpatterns = [
    path("login/", views.loginUser, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    # original url: (e.g) flapp-app.herokuapp.com
    path("", views.home, name="home"),

    path("products/", views.products, name="products"),
    path('create-product/', views.createProduct, name="create-product"),
    # <str:pk> returns page for specific product id
    path('update-product/<str:pk>/', views.updateProduct, name="update-product"),

    path("orders/", views.orders, name="orders"),
    path('create-order/', views.createOrder, name="create-order"),
    path('create-QR-order/', views.createQROrder, name="create-QR-order"),

    path("retrieve-order/<str:pk>/", views.retrieveOrder, name="retrieve-order"),
    path('update-order/<str:pk>/', views.updateOrder, name="update-order"),
    path('delete-order/<str:pk>/', views.deleteOrder, name="delete-order"),

    path("customers/", views.customers, name="customers"),
    path('create-customer/', views.createCustomer, name="create-customer"),
    path("retrieve-customer/<str:pk>/", views.retrieveCustomer, name="retrieve-customer"),
    path('update-customer/<str:pk>/', views.updateCustomer, name="update-customer"),
    path('delete-customer/<str:pk>/', views.deleteCustomer, name="delete-customer"),

    path("invoices/", views.invoices, name="invoices"),
    path("generateInvoices/", views.generateInvoices, name="generateInvoices"),
    path('pdf_view/<pk>/', views.render_pdf_view, name='pdf_view'),

    path("reports/", views.reports, name="reports"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)