from django.conf.urls import url
from Places import views


urlpatterns = [
    url(r'^places/$', views.PlacesListView.as_view()),
    url(r'^places/(?P<pk>\d+)/$', views.PlaceDetailView.as_view()),
    url(r'^accepts/$', views.AcceptsListView.as_view()),
    url(r'^accepts/(?P<pk>\d+)/$', views.AcceptDetailView.as_view()),
    url(r'^ratings/$', views.RatingsListView.as_view()),
    url(r'^ratings/(?P<pk>\d+)/$', views.RatingDetailView.as_view()),
    url(r'^place_images/$', views.PlaceImagesListView.as_view()),
    url(r'^place_images/(?P<pk>\d+)/$', views.PlaceImageDetailView.as_view()),
]
