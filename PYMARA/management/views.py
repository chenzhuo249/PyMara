from django.shortcuts import render
from Public.tools import *


# Create your views here.
def index(request):
    return good({'quanbu':7,'gongkai':3})
