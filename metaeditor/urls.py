from django.conf.urls import patterns, include, url
from django.contrib import admin

from editor import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='home'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^editor/', include('editor.urls')),
    url(r'^account/', include('accounts.urls', namespace='accounts')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
)
