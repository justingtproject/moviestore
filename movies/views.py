from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, MoviePetition, MoviePetitionVote, Review, MovieRating
from django.contrib.auth.decorators import login_required
from .forms import MovieRequestForm, MoviePetitionForm
from .models import MovieRequest
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count
from django.db.models import Avg, Count


@login_required
def movie_requests(request):
    if request.method == "POST":
        # delete
        if "delete" in request.POST:
            req = get_object_or_404(MovieRequest, pk=request.POST["delete"], user=request.user)
            req.delete()
            messages.success(request, "Request deleted.")
            return redirect("movie_requests")

        # create
        form = MovieRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "Request added.")
            return redirect("movie_requests")
    else:
        form = MovieRequestForm()

    my_reqs = MovieRequest.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "movies/movie_requests.html", {"form": form, "requests": my_reqs})


def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def movie_petitions(request):
    # CREATE (you already had this; just set created_by)
    if request.method == "POST" and "create" in request.POST:
        form = MoviePetitionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Petition created.")
            return redirect("movie_petitions")
    else:
        form = MoviePetitionForm()

    # DELETE (optional: allow only creator or staff)
    if request.method == "POST" and "delete" in request.POST:
        petition = get_object_or_404(MoviePetition, pk=request.POST["delete"])
        if petition.created_by_id == request.user.id or request.user.is_staff:
            petition.delete()
            messages.success(request, "Petition deleted.")
        else:
            messages.error(request, "You can only delete your own petitions.")
        return redirect("movie_petitions")

    # LIST all petitions globally with vote counts
    petitions = (
        MoviePetition.objects
        .annotate(vote_total=Count("voters"))
        .order_by("-vote_total", "-created_at")
    )
    return render(request, "movies/petitions.html", {"form": form, "petitions": petitions})

@login_required
def movie_petition_vote(request, petition_id):
    petition = get_object_or_404(MoviePetition, pk=petition_id)
    try:
        MoviePetitionVote.objects.create(petition=petition, user=request.user)
        messages.success(request, "Vote recorded.")
    except IntegrityError:
        messages.info(request, "You already voted for this petition.")
    return redirect("movie_petitions")


def show(request, id):
    movie = get_object_or_404(Movie, pk=id)
    reviews = Review.objects.filter(movie=movie).select_related("user").order_by("-date")

    from .models import MovieRating
    from django.db.models import Avg, Count

    stats = MovieRating.objects.filter(movie=movie).aggregate(avg=Avg("value"), n=Count("id"))
    user_value = None
    if request.user.is_authenticated:
        user_value = MovieRating.objects.filter(movie=movie, user=request.user)\
                                        .values_list("value", flat=True).first()

    template_data = {
        "movie": movie,
        "reviews": reviews,
        "avg_rating": stats["avg"],
        "rating_count": stats["n"],
        "user_rating": user_value,
    }
    return render(request, "movies/show.html", {"template_data": template_data})

@login_required
def rate_movie(request, id):
    movie = get_object_or_404(Movie, pk=id)
    if request.method == "POST":
        try:
            value = int(request.POST.get("rating", ""))
        except ValueError:
            value = 0
        if value < 1 or value > 5:
            messages.error(request, "Choose a rating from 1 to 5.")
        else:
            MovieRating.objects.update_or_create(
                movie=movie, user=request.user, defaults={"value": value}
            )
            messages.success(request, "Thanks for rating!")
    return redirect("movies.show", id=movie.id)

@login_required
def clear_rating(request, id):
    movie = get_object_or_404(Movie, pk=id)
    MovieRating.objects.filter(movie=movie, user=request.user).delete()
    messages.success(request, "Your rating was removed.")
    return redirect("movies.show", id=movie.id)