# -*- coding: UTF-8 -*-
from models import Newsletter, Link, Settings
from flask import Blueprint, redirect
from datetime import date

admin = Blueprint('admin', __name__)
