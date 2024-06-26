"""
URL configuration for LaHuertaDeAbril project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lahuertadeabril02app import endpoints
urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/users/', endpoints.users),
    path('v1/sessions/', endpoints.sessions),
    path('v1/account/', endpoints.account),
    path('v1/password/', endpoints.password),
    path('v1/search_product1/', endpoints.search_product1),
    path('v1/search_product2/', endpoints.search_product2),
    path('v1/info_product1/<int:product_id>/', endpoints.info_product1),
    path('v1/info_product2/<int:product_id>/', endpoints.info_product2),
    path('v1/add_favourites_1/<int:product_id>/', endpoints.add_to_favourites1),
    path('v1/add_favourites_2/<int:product_id>/', endpoints.add_to_favourites2),
    path('v1/favourites_1/', endpoints.favourites1),
    path('v1/favourites_2/', endpoints.favourites2),

]
