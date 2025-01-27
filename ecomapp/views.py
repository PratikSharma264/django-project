#from typing import Any
from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView,CreateView,FormView,DetailView,ListView
from django.urls import reverse_lazy,reverse
from .models import *
from django.contrib import messages
from .forms import CheckoutForm,CustomerRegistrationForm,CustomerLoginForm,AdminLoginForm,ContactForm,ProductForm,PasswordForgotForm,PasswordResetForm
from django.contrib.auth import authenticate, login, logout
import logging
import requests
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse
from .utils import password_reset_token
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
class EcomMixin(object):
    def dispatch(self,request,*args,**kwargs):
        cart_id=request.session.get("cart_id")
        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer=request.user.customer
                cart_obj.save()
        return super().dispatch(request,*args,**kwargs)
    

# class HomeView(EcomMixin,TemplateView):
#     template_name= "home.html"

    # def get_context_data(self,**kwargs):
    #     context=super().get_context_data(**kwargs)
    #     #context['product_list']=Product.objects.all()
    #     context['myname']="Pratik Sharma"
    #     all_products = Product.objects.all().order_by("-id")
    #     paginatior = Paginator(all_products,4)
    #     page_number = self.request.GET.get("page")
    #     product_list = Paginator.get_page(page_number)
    #     #context['allcategories']=Category.objects.all().order_by("-id")
    #     context["product_list"]= product_list
    #     return context

class HomeView(EcomMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myname'] = "Pratik Sharma"
        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 8)  
        page_number = self.request.GET.get("page")
        product_list = paginator.get_page(page_number)
        context["product_list"] = product_list
        context['allcategories'] = Category.objects.all().order_by("-id")
        return context
    
class AllProductsView(EcomMixin,TemplateView):
    template_name="allproducts.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['allcategories']=Category.objects.all()
        return context
    
class ProductDetailView(EcomMixin,TemplateView):
    template_name="productdetail.html"

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        url_slug=self.kwargs['slug']
        product=Product.objects.get(slug=url_slug)
        product.view_count+=1
        product.save()
        context['product']=product
        return context
    

class AddToCartView(EcomMixin,TemplateView):
    template_name="addtocart.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs) 
        #get product id from requested url
        product_id=self.kwargs['pro_id']
    
        #get product
        product_obj=Product.objects.get(id=product_id)

        #check if cart exists
        cart_id=self.request.session.get("cart_id",None)
        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            this_product_in_cart=cart_obj.cartproduct_set.filter(product=product_obj)

            #item already exists in cart
            if this_product_in_cart.exists():
                cartproduct=this_product_in_cart.last()
                cartproduct.quantity +=1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            #new item added in cart
            else:
                cartproduct=CartProduct.objects.create(cart=cart_obj, product=product_obj, rate= product_obj.selling_price, quantity=1,
                subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
        else:
            cart_obj=Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct=CartProduct.objects.create(cart=cart_obj, product=product_obj, rate= product_obj.selling_price, quantity=1,
                subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

        #check if product already ecists in cart.
        return context
        


class MyCartView(EcomMixin,TemplateView):
    template_name='mycart.html'
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        cart_id=self.request.session.get("cart_id",None)
        if cart_id:
            cart=Cart.objects.get(id=cart_id)
        else:
            cart=None
        context['cart']=cart
        return context
        


class ManageCartView(EcomMixin,View):
    def get(self,request,*args, **kwargs):
        cp_id=self.kwargs['cp_id']
        action = request.GET.get('action')
        cp_obj=CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart
       
        if action=='inc':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action=='dcr':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity ==0:
                    cp_obj.delete()
        elif action=='rmv':
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect('ecomapp:mycart')



class EmptyCartView(EcomMixin,View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get('cart_id', None)
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                cart.cartproduct_set.all().delete()
                cart.total = 0
                cart.save()
                messages.success(request, "Your cart has been successfully emptied.")
            except Cart.DoesNotExist:
                messages.error(request, "The cart could not be found.")
        else:
            messages.warning(request, "You don't have an active cart.")
        
        return redirect('ecomapp:mycart') 




class CheckoutView(CreateView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('ecomapp:home')  

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if request.user.is_authenticated:
            try:
                customer = request.user.customer
            except Customer.DoesNotExist:
                messages.error(request, "You need to complete your profile before proceeding to checkout.")
                return redirect("/profile/")
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            try:
                cart_obj = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart_obj = None
                messages.warning(self.request, "Cart does not exist.")
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context
    
    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if Order.objects.filter(cart=cart_obj).exists():
                # Handle the case where the cart is already associated with an order
                messages.error(self.request, "This cart is already associated with an order.")
                return redirect('ecomapp:mycart')
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = 'Order Recieved'
            del self.request.session['cart_id']
            pm = form.cleaned_data.get("payment_method")  # Payment Method
            order = form.save()
            if pm == "Khalti":
                return redirect(reverse("ecomapp:khalti_checkout", kwargs={"order_id": order.id}))
            elif pm == "Esewa":
                return redirect(reverse("ecomapp:esewa_payment_page", kwargs={"order_id": order.id}))
        else:
            return redirect('ecomapp:home')
        return super().form_valid(form)



def khalti_checkout(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {
        'order': order,
        'khalti_public_key': settings.KHALTI_PUBLIC_KEY
    }
    return render(request, 'khaltirequest.html', context)





def verify_payment(request):   #khalti verify payment
    if request.method == "POST":
        data = request.json()
        payload = {
            "token": data.get("token"),
            "amount": data.get("amount")
        }
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
        }

        response = requests.post(settings.KHALTI_VERIFY_URL, payload, headers=headers)
        if response.status_code == 200:
            return JsonResponse({"success": True, "message": "Payment Verified"})
        else:
            return JsonResponse({"success": False, "message": "Verification Failed"})

    return JsonResponse({"error": "Invalid Request"}, status=400)


    

logger = logging.getLogger(__name__)

class CustomerRegistrationView(CreateView):
    template_name = "customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("ecomapp:home")

    def form_valid(self, form):
        try:
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            user = User.objects.create_user(username, email, password)
            form.instance.user = user
            login(self.request, user)
            messages.success(self.request, "Your account has been created and you are now logged in!")

        except Exception as e:
            logger.error(f"Error during registration: {e}")

            messages.error(self.request, "An error occurred during registration. Please try again.")
            return redirect("ecomapp:customerregistration")

        return super().form_valid(form)
    
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url
        

    
class CustomerLogoutView(View):
    def get(self,request):
        logout(request)
        return redirect("ecomapp:home")
    

# class CustomerLoginView(FormView):
#     template_name = "customerlogin.html"
#     form_class = CustomerLoginForm
#     success_url = reverse_lazy("ecomapp:home")
    
#     def form_valid(self,form):
#         uname = form.cleaned_data.get("username")
#         pword = form.cleaned_data["password"]
#         usr = authenticate(username=uname,password=pword)
#         #if usr is not None and usr.customer:
#         if usr is not None and Customer.objects.filter(user=usr).exists():
#             login(self.request, usr)
#         else:
#             return render(self.request,self.template_name, {"form": self.form_class,"error": "Invalid credentials"})
#         return super().form_valid(form)
    
#     def get_success_url(self):
#         if "next" in self.request.GET:
#             next_url = self.request.GET.get("next")
#             return next_url
#         else:
#             return self.success_url


#  class CustomerLoginView(FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomapp:home")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)

        if usr is not None:
            # Check if the user is a customer and log them in
            if Customer.objects.filter(user=usr).exists():
                login(self.request, usr)
                return super().form_valid(form)
            # Check if the user is a superuser and log them in
            elif usr.is_superuser:
                login(self.request, usr)
                return redirect('ecomapp:adminhome')  # Redirect to admin home page
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class CustomerLoginView(FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomapp:home")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)

        if usr is not None:
            # Check if the user is a customer and log them in
            if Customer.objects.filter(user=usr).exists():
                login(self.request, usr)
                return super().form_valid(form)
            # Check if the user is a superuser and log them in
            elif usr.is_superuser:
                login(self.request, usr)
                return redirect('ecomapp:adminhome')  # Redirect to admin home page
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            # Check if the 'next' URL is pointing to the admin login page and prevent that
            if "adminlogin" in next_url:
                return reverse_lazy("ecomapp:adminhome")  # Redirect to admin home page
            return next_url
        else:
            return self.success_url



class AboutView(EcomMixin, TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Provide creator details
        context['creator'] = {
        'name': 'Pratik Sharma',  
        'role': 'Developer & Visionary',
        'image_url': settings.MEDIA_URL + 'creator/19cdfda9-1dce-4171-a19b-1301c9d3d0fe.jpg', 
        'bio': 'Pratik is a passionate software developer dedicated to crafting user-friendly and impactful applications. With a deep understanding of technology and a commitment to excellence, he has built this platform to redefine the e-commerce experience.',
        'mission': 'To revolutionize online shopping by providing seamless, reliable, and customer-focused solutions.',
        'vision': 'Creating a future where online shopping is intuitive, inclusive, and accessible for everyone.',
        'values': [
            'Innovation',
            'Customer-Centric Approach',
            'Integrity',
            'Sustainability',
            'Diversity and Inclusion'
        ],
   
        'fun_fact': 'The platform’s name was inspired by Pratik’s late-night brainstorming sessions fueled by coffee!',
        'contact_cta': 'Want to get in touch? Reach out via our Contact page or follow me on social media.'
}

        return context


class ContactView(EcomMixin,TemplateView):
    template_name= "contactus.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data
            form.save()
            messages.success(request, "Thank you for contacting us. We will get back to you shortly.")
            return redirect('ecomapp:contact')
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)
        
class CustomerProfileView(TemplateView):
    template_name="customerprofile.html"
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer=self.request.user.customer
        context['customer']=customer
        orders=Order.objects.filter(cart__customer=customer).order_by("-id")
        context['orders']=orders
        return context
    
class CustomerOrderDetailView(DetailView):
    template_name="customerorderdetail.html"
    model=Order
    context_object_name="ord_obj"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id=self.kwargs['pk']
            order=Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("ecomapp:customerprofile")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        order_id=self.kwargs['pk']
        order=Order.objects.get(id=order_id)
        orderitems=CartProduct.objects.filter(cart=order.cart)
        context['orderitems']=orderitems
        return context
    
class SearchView(TemplateView):
    template_name="search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw=self.request.GET.get('keyword')
        results = Product.objects.filter(Q(title__icontains=kw) | Q(description__icontains=kw) | Q(return_policy__icontains=kw))
        context["results"] = results
        return context


class PasswordForgotView(FormView):
    template_name = "forgotpassword.html"
    form_class = PasswordForgotForm
    success_url = "/forgot-password/?m=s"

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        url = self.request.META['HTTP_HOST']   # get current host ip/domain
        customer = Customer.objects.get(user__email=email)   
        user = customer.user
        # send mail to the user with email
        text_content = 'Please Click the link below to reset your password. '
        html_content = url + "/password-reset/" + email + "/" + password_reset_token.make_token(user) + "/" 
        send_mail(
            'Password Reset Link | Django Ecommerce',
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return super().form_valid(form)

    
    
class PasswordResetView(FormView):
    template_name = "passwordreset.html"
    form_class = PasswordResetForm
    success_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")
        if user is not None and password_reset_token.check_token(user, token):
            pass
        else:
            return redirect(reverse("ecomapp:passwordforgot") + "?m=e")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data['new_password']
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return super().form_valid(form)
       


#admin pages
# class AdminLoginView(FormView):
#     template_name="adminpages/adminlogin.html"
#     form_class=AdminLoginForm
#     success_url=reverse_lazy("ecomapp:adminhome")

#     def form_valid(self, form):
#         uname=form.cleaned_data.get("username")
#         pword=form.cleaned_data.get("password")
#         usr=authenticate(username=uname,password=pword)
#         if usr is not None and usr.admin:
#             login(self.request,usr)
#         else:
#             return render(self.request,self.template_name,{"form":self.form_class,"error":"Invalid credentials"})
#         return super().form_valid(form)

    

class AdminLoginView(FormView):
    template_name = "adminpages/adminlogin.html"
    form_class = AdminLoginForm
    success_url = reverse_lazy("ecomapp:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data.get("password")
        usr = authenticate(username=uname, password=pword)
        if usr is not None and usr.is_staff:
            login(self.request, usr)
            self.request.session["admin_logged_in"] = True
            return redirect(self.success_url)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
        return super().form_valid(form)



# class  AdminRequiredMixin(object):
#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
#             pass
#         else:
#             return redirect("/admin-login/")
#         return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.session.get("admin_logged_in"):
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect("/admin-login/")

# class AdminHomeView(AdminRequiredMixin,TemplateView):
#     template_name="adminpages/adminhome.html"
    
#     def get_context_data(self, **kwargs):
#         context=super().get_context_data(**kwargs)
#         context['pendingorders']=Order.objects.filter(order_status="Order Recieved").order_by("-id")
#         return context



class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminhome.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pendingorders'] = Order.objects.filter(order_status="Order Recieved").order_by("-id")
        return context


class AdminOrderDetailView(AdminRequiredMixin,DetailView):
    template_name="adminpages/adminorderdetail.html"
    model=Order
    context_object_name="ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"]=ORDER_STATUS
        return context



class AdminOrderListView(AdminRequiredMixin,ListView):
    template_name="adminpages/adminorderlist.html"
    queryset=Order.objects.all().order_by("-id")
    context_object_name="allorders"
    

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['allorders']=Order.objects.all().order_by("-id")
        return context


class AdminOrderStatusChange(AdminRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status=request.POST.get("status")
        order_obj.order_status=new_status
        order_obj.save()
        return redirect(reverse_lazy("ecomapp:adminorderdetail", kwargs={"pk":self.kwargs["pk"]}))

class AdminContactView(AdminRequiredMixin,ListView):
    template_name="adminpages/admincontact.html"
    queryset=Contact.objects.all().order_by("-id")
    context_object_name="contacts"
    ordering=["-created_at"]
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['contacts']=Contact.objects.all().order_by("-id")
        return context


class AdminProductListView(AdminRequiredMixin,ListView):
    template_name="adminpages/adminproductlist.html"
    queryset=Product.objects.all().order_by("-id")
    context_object_name="allproducts"
    ordering=["-id"]
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['products']=Product.objects.all().order_by("-id")
        return context
    
class AdminProductCreateView(AdminRequiredMixin,CreateView):
    template_name="adminpages/adminproductcreate.html"
    model=Product
    form_class=ProductForm
    #fields="__all__"
    success_url=reverse_lazy("ecomapp:adminproductlist")
    
    def form_valid(self, form):
        ptitle=form.cleaned_data.get("title")
        messages.success(self.request,ptitle+" has been added successfully")
        return super().form_valid(form)
    

