from django.urls import path
from .views  import *
app_name= "ecomapp"
urlpatterns = [
    path("",HomeView.as_view(), name= "home"), 
    path("about/",AboutView.as_view(), name= "about"),  # type: ignore
    path("contact-us/",ContactView.as_view(), name= "contact"), # type: ignore
    path("all-products/",AllProductsView.as_view(),name="allproducts"), # type: ignore
    path("products/<slug:slug>/",ProductDetailView.as_view(),name="productdetail"), # type: ignore
    path("add-to-cart-<int:pro_id>/",AddToCartView.as_view(),name="addtocart"),
    path("my-cart/",MyCartView.as_view(),name='mycart'),
    path("manage-cart/<int:cp_id>/",ManageCartView.as_view(),name="managecart"),
    path("empty-cart/",EmptyCartView.as_view(),name="emptycart"),
    path("checkout/",CheckoutView.as_view(),name="checkout"),
    path("register/",CustomerRegistrationView.as_view(),name="customerregistration"),
    path("logout/",CustomerLogoutView.as_view(),name="customerlogout"),
    path("login/",CustomerLoginView.as_view(),name="customerlogin"),
    path("profile/",CustomerProfileView.as_view(),name="customerprofile"),
    path("profile/order-<int:pk>/",CustomerOrderDetailView.as_view(),name="customerorderdetail"),
    path("search/", SearchView.as_view(),name="search"),
    #payment
    # path('khalti-request/', KhaltiRequestView.as_view(), name='khaltirequest'),
    path('khalti-checkout/<int:order_id>/', khalti_checkout, name='khalti_checkout'),
    path('khalti-verify/', verify_payment, name='verify_payment'),
    #Admin Section
    path("admin-login/",AdminLoginView.as_view(),name="adminlogin"),
    path("admin-home/",AdminHomeView.as_view(),name="adminhome"),
    path("admin-order/<int:pk>/",AdminOrderDetailView.as_view(),name="adminorderdetail"),
    path("admin-all-orders/",AdminOrderListView.as_view(),name="adminorderlist"),
    path("admin-order-<int:pk>-change/",AdminOrderStatusChange.as_view(),name="adminorderstatuschange"),
    path("admin-contact/",AdminContactView.as_view(),name="admincontact"),
] 