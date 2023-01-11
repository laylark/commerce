from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment

# Create class for new listing form
class NewListingForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class' : 'form-control'}))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={'class' : 'form-control'}))
    image = forms.CharField(label="Image path", widget=forms.TextInput(attrs={'class' : 'form-control'}))
    price = forms.DecimalField(label="Price", widget=forms.TextInput(attrs={'class' : 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all().order_by('name'))

# Create class for bidding form
class NewBidForm(forms.Form):
    amount = forms.DecimalField(label="", widget=forms.TextInput(attrs={'placeholder' : 'Place a bid...', 'class' : 'form-control mx-2'}))

# Create class for comment form
class NewCommentForm(forms.Form):
    text = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Add a comment...', 'class' : 'form-control mx-2'}))

# Render index page with all listings
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status=0)
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
            initial_bid = Bid(amount=0, listing=listing, user=request.user)
            initial_bid.save()
            return redirect("index")

    # Render new listing form page
    return render(request, "auctions/create.html", {"form": NewListingForm()})
        

# Render listings active in watchlist
def watchlist(request):
    # Validate if user is logged in
    if not request.user.is_authenticated:
        return redirect("index")

    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watched_listings.filter(status=0)
    })


# Render page for selected listing
def listing(request, id):
    listing = Listing.objects.get(pk=id)
    max_bid = listing.bids.order_by('-amount').first() # SELECT * FROM bids WHERE listing = id ORDER BY amount DESC LIMIT 1
    comments = listing.comments.order_by('-created_at') # SELECT * FROM comments WHERE listing = id ORDER BY created_at DESC

    # Validate if entry exists
    if listing == None:
        return render(request, "auctions/404.html", status=404)

    if request.method == "POST":

        # Add listing to watchlist if does not exist and redirect to watchlist page
        if listing.watched_by.filter(id=request.user.id).exists():
            listing.watched_by.remove(request.user)
        else:
            listing.watched_by.add(request.user)
        return redirect("watchlist")

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_form": NewBidForm(),
        "max_bid": max_bid,
        "comment_form": NewCommentForm(),
        "comments": comments,
    })
    

# Post valid bids to database
def bid(request, id):
    listing = Listing.objects.get(pk=id)
    max_bid = listing.bids.order_by('-amount').first()

    # Create a new bid form
    form = NewBidForm(request.POST)

    # Validate form
    if not form.is_valid():
    # If not valid, render listing page along with form data submitted by user
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "bid_form": form,
            "max_bid": max_bid,
        })

    amount = form.cleaned_data["amount"]

    # If bid not greater than max amount, provide error message and render listing page
    if max_bid.amount >= amount:
        messages.error(request, "Error. Bid must be greater than current bid.")
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "bid_form": form,
            "max_bid": max_bid,
        })

    # Save bid to table and redirect to index page if bid > max amount
    bid = Bid(amount=amount, listing=listing, user=request.user)
    bid.save()
    return redirect("listing", id=id)


# Change status to closed in database
def close_auction(request, id):
    listing = Listing.objects.get(pk=id)
    
    # Validate if user is logged in
    if not request.user.is_authenticated:
        return redirect("index")

    # Validate if user created listing
    if request.user != listing.user:
        return redirect("index")

    # Close listing status
    listing.status = 1
    
    # Identify the winner of the auction
    winner = listing.bids.order_by('-amount').first().user # SELECT user FROM bids WHERE listing = id ORDER BY amount DESC LIMIT 1
    listing.winner = winner
    listing.save() # UPDATE listing SET status = 1, winner = winner WHERE pk=id

    return redirect("index")


# Post valid comments to database
def comment(request, id):
    listing = Listing.objects.get(pk=id)

    # Validate if user is logged in
    if not request.user.is_authenticated:
        return redirect("index")

    # Create a new comment form
    form = NewCommentForm(request.POST)

    # Validate form
    if not form.is_valid():
    # If not valid, render listing page along with form data submitted by user
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comment_form": form,
        })

    text = form.cleaned_data["text"]

    # Save comment to database and redirect to current listing page
    comment = Comment(text=text, user=request.user, listing=listing)
    comment.save()
    return redirect("listing", id=id)


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