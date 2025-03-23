# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate

from .models import CarMake, CarModel

from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.


# Create a 'get_cars' view to handle db request
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related("car_make")
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    # Try to check if provided credentials can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}

    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)


# Update the `get_dealerships` view to render the index page with
# a list of dealerships or particular state if state is passed
def get_dealerships(request, state="All"):
    logger.info(f"Fetching dealerships for state: {state}")

    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"

    try:
        dealerships = get_request(endpoint)
        if not dealerships:
            logger.warning(f"No dealers found for state: {state}")
            return JsonResponse({"status": 200, "dealers": []})

        logger.info(f"Found {len(dealerships)} dealerships")
        return JsonResponse({"status": 200, "dealers": dealerships})

    except Exception as e:
        logger.error(f"Error fetching dealers: {str(e)}")
        return JsonResponse(
            {"status": 500, "error": "Failed to fetch dealers"}, status=500
        )


# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        try:
            reviews = get_request(endpoint)
            if not reviews:
                return JsonResponse({"status": 200, "reviews": []})

            for review_detail in reviews:
                response = analyze_review_sentiments(review_detail["review"])
                review_detail["sentiment"] = response["sentiment"]

            return JsonResponse({"status": 200, "reviews": reviews})
        except Exception as e:
            logger.error(f"Error fetching reviews for dealer {dealer_id}: {str(e)}")
            return JsonResponse(
                {"status": 500, "error": "Failed to fetch reviews"}, status=500
            )
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        try:
            dealership = get_request(endpoint)
            if not dealership:
                return JsonResponse({"status": 404, "message": "Dealer not found"})
            return JsonResponse({"status": 200, "dealer": dealership})
        except Exception as e:
            logger.error(f"Error fetching dealer details for {dealer_id}: {str(e)}")
            return JsonResponse(
                {"status": 500, "error": "Failed to fetch dealer details"}, status=500
            )
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `add_review` view to submit a review
def add_review(request):
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status": 200})
        except Exception as e:
            logger.error(f"Error posting review: {str(e)}")
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
