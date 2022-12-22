from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from .models import User, Category, Listing, Bid, Comment, Watchlist

# Create class for new listing form
class NewListingForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class' : 'form-control'}))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={'class' : 'form-control'}))
    image = forms.CharField(label="Image path", widget=forms.TextInput(attrs={'class' : 'form-control'}))
    price = forms.DecimalField(label="Price", widget=forms.TextInput(attrs={'class' : 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all().order_by('name'))

# Render index page with all listings
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })

# Create a new listing 
def create_listing(request):
    if request.method == "POST":
            # Create a new listing form
            form = NewListingForm(request.POST)

            # Validate form
            if not form.is_valid():
                # If not valid, render new listing page along with form data submitted by user
                return render(request, "auctions/create.html", {"form": form})

            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
            price = form.cleaned_data["price"]
            category = form.cleaned_data["category"]

            # Save listing to listing table and redirect to index page
            listing = Listing(title=title, description=description, img_path=image, price=price, category=category, user=request.user)
            listing.save()
            return redirect("index")

    # Render new listing form page
    return render(request, "auctions/create.html", {"form": NewListingForm()})
        

# Render listings active in watchlist
def watchlist(request):

    # Validate if user is logged in
    if not request.user.is_authenticated:
        return redirect("index")

    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watched_listings.all()
    })

# Render page for selected listing
def listing(request, id):
    listing = Listing.objects.get(pk=id)
    
    # Validate if entry exists
    if listing == None:
        return render(request, "auctions/404.html", status=404)

    return render(request, "auctions/listing.html", {
        "listing": listing
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")