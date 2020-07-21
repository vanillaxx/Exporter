from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from common.Parsers import excel_parser


def index(request):
    return render(request, 'main/main.html')

