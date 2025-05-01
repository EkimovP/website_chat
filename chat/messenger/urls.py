from django.urls import path

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('feedback/', views.FeedbackFormView.as_view(), name='feedback'),
    path('add_channel/', views.AddChannelFormView.as_view(), name='add_channel'),
    path('update_channel/<slug:update_slug>/', views.UpdateChannelFormView.as_view(), name='update_channel'),
    path('delete_channel/<slug:delete_slug>/', views.DeleteChannelView.as_view(), name='delete_channel'),
    path('user-search/', views.user_search, name='user_search'),
    path('channels/', views.ShowChannelsView.as_view(), name='channels'),
    path('chat/<slug:chat_slug>/', views.ShowChatView.as_view(), name='chat'),
]
