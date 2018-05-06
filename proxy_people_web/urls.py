"""proxy_people_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from main_app.views import *
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/api_test/',api_test,name="api_test"),
    url(r'^api/admin_proxy_account_add_api',admin_proxy_account_add_API,name='admin_proxy_account_add_API'),
    url(r'^api/admin_proxy_account_topup',admin_proxy_account_topup,name='admin_proxy_account_topup'),
    url(r'^api/admin_proxy_account_balance_setup',admin_proxy_account_balance_setup,name='admin_proxy_account_balance_setup'),
    url(r'^api/proxy_account_balance_check',proxy_account_balance_check,name='proxy_account_balance_check'),
    url(r'^api/proxy_account_login',proxy_account_login,name='proxy_account_login'),
    url(r'^api/proxy_account_change_password',proxy_account_change_password,name='proxy_account_change_password'),
    url(r'^api/admin_proxy_account_change_password',admin_proxy_account_change_password,name='admin_proxy_account_change_password'),
    url(r'^api/proxy_account_ad_change',proxy_account_ad_change,name='proxy_account_ad_change'),
    url(r'^api/proxy_info_get',proxy_info_get,name='proxy_info_get'),
    url(r'^api/admin_set_software',admin_set_software,name='admin_set_software'),
    url(r'^api/admin_update_software_version',admin_update_software_version,name='admin_update_software_version'),
    url(r'^api/admin_update_software_cost',admin_update_software_cost,name='admin_update_software_cost'),
    url(r'^api/proxy_get_software_code',proxy_get_software_code,name='proxy_get_software_code'),
    url(r'^api/authorization_make',authorization_make,name='authorization_make'),
    url(r'^api/authorization_check',authorization_check,name='authorization_check'),
    url(r'^api/authorization_change',authorization_change,name='authorization_change'),
]
