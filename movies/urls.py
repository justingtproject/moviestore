from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review, name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
    path("movies/requests/", views.movie_requests, name="movie_requests"),
    path("petitions/", views.movie_petitions, name="movie_petitions"),
    path("petitions/<int:petition_id>/vote/", views.movie_petition_vote, name="movie_petition_vote"),
    path("<int:id>/rate/", views.rate_movie, name="movies.rate"),
    path("<int:id>/rating/clear/", views.clear_rating, name="movies.clear_rating"),
]