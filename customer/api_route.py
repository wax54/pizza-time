from flask import Blueprint, redirect, jsonify, render_template, session, flash, g, request
from config import USER_KEY, API_SESSION_KEY
from customer.models import Customer

customer_api = Blueprint('customer_api_routes', __name__)
