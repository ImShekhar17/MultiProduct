from django.shortcuts import render

# Create your views here.


def home(request):
   return JsonResponse({
       "status": "ok",
        "message": "Service is up and running"
    })
   

def service_granted(request):
    return JsonResponse({
        "status": "ok",
        "message": "You have access to the service"
    })



