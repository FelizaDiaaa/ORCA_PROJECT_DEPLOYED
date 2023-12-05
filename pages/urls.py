from django.urls import path, include
from .import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
app_name = 'pages'

urlpatterns = [
    path('', RedirectView.as_view(url='main', permanent=False)),
    path('main', views.MainPage.as_view(), name='MainPage'),
    path('donate', views.DonatePage.as_view(), name='DonatePage'),

    path('volunteerorg', views.VolunteerOrgPage.as_view(), name='VolunteerOrgPage'),
    path('volunteer', views.VolunteerPage.as_view(), name='VolunteerPage'),
    path('register', views.RegisterPage.as_view(), name='RegisterPage'),
    path('login', views.LoginPage.as_view(), name='LoginPage'),

    path('userdashboard', views.UserDashboard.as_view(), name='UserDashboard'),

    path('userprofile', views.UserProfilePage.as_view(), name='UserProfilePage'),
    path('userhome', views.UserHomePage.as_view(), name='UserHomePage'),
    path('userappointments', views.UserAppointmentsPage.as_view(), name='UserAppointmentsPage'),
    path('userpets', views.UserPetsPage.as_view(), name='UserPetsPage'),
    path('userhighlights', views.UserHighlightsPage.as_view(), name='UserHighlightsPage'),

    path('orgdashboard', views.OrgDashboard.as_view(), name='OrgDashboard'),
    path('orghome', views.OrgHomePage.as_view(), name='OrgHomePage'),
    path('orgprofile', views.OrgProfilePage.as_view(), name='OrgProfilePage'),
    path('orgclients', views.OrgClientsPage.as_view(), name='OrgClientsPage'),
    path('orgvolunteers', views.OrgVolunteersPage.as_view(), name='OrgVolunteersPage'),
    path('orgappointmentrecs', views.OrgAppointmentRecsPage.as_view(), name='OrgAppointmentRecsPage'),

    path('systemadmindashboard', views.SystemAdminDashboard.as_view(), name='SystemAdminDashboard'),
    path('systemadminhome', views.SystemAdminHome.as_view(), name='SystemAdminHome'),
    path('systemadminorgs', views.SystemAdminOrgs.as_view(), name='SystemAdminOrgs'),
    path('systemadminlogin', views.SystemAdminLogin.as_view(), name='SystemAdminLoginPage'),

    path('logout_view/', views.logout_view, name='logout_view'),
    path('logout_view', views.logout_view, name='logout_view'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

