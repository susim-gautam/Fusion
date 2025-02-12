import json
from django.shortcuts import render, get_object_or_404
from .models import *
from applications.globals.models import ExtraInfo
from applications.globals.models import *
from django.db.models import Q
from django.http import Http404
# from .forms import EditDetailsForm, EditConfidentialDetailsForm, EditServiceBookForm, NewUserForm, AddExtraInfo
from django.contrib import messages
from applications.eis.models import *
from django.http import HttpResponse, JsonResponse
from applications.establishment.models import *
from applications.establishment.views import *
from applications.eis.models import *
from applications.globals.models import ExtraInfo, HoldsDesignation, DepartmentInfo, Designation, ModuleAccess
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from decimal import Decimal, InvalidOperation





def check_hr_access(request):
    """
    Check if the authenticated user has HR module access.
    Returns:
        - True if the user has HR access.
        - False if the user does not have HR access or an error occurs.
    """
    user = request.user

    # Check if the user is authenticated
    if not user.is_authenticated:
        return False

    # Get the user's current designation
    try:
        # Fetch the user's current designation from HoldsDesignation
        

        


        
        

        extra_info = get_object_or_404(ExtraInfo, user=user)
        last_selected_role=extra_info.last_selected_role
        request.session['currentDesignationSelected'] = last_selected_role
        current_designation = HoldsDesignation.objects.filter(working=user).first()
        print(f"Current Designation: {current_designation.designation.name if current_designation else None}")  # Debugging
        if not current_designation:
            return False

        # Fetch the ModuleAccess for the user's designation
        module_access = ModuleAccess.objects.filter(designation=current_designation.designation.name).first()
        if not module_access:
            return False

        # Check if HR module access is granted
        return module_access.hr

    except Exception as e:
        # Handle any unexpected errors
        print(f"Error in check_hr_access: {str(e)}")  # Debugging
        return False
    


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def test(request):
    """
    Test view to check HR access and perform additional actions.
    """
    user = request.user

    # Check if the user is authenticated
    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    # Check if the user has HR access
    if check_hr_access(request):
        # Perform additional actions if HR access is granted
        print("User has HR access. Performing additional actions...")  # Debugging
        # Add your additional logic here
        return JsonResponse({'message': 'You have HR access. Additional actions performed.'}, status=200)
    else:
        # Return a response if HR access is not granted
        return JsonResponse({'error': 'HR access required'}, status=403)
    


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import LeaveBalance, LeavePerYear
from applications.globals.models import ExtraInfo

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_leave_balance(request):
    """
    API endpoint to retrieve the leave balance for the authenticated user.
    Returns:
        - A JSON response containing the leave balance for each leave type.
    """
    user = request.user

    # Check if the user is authenticated
    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)



    # check if the user has HR access
    if not check_hr_access(request):
        return JsonResponse({'error': 'HR access required'}, status=403)
    
    try:
        # Fetch the ExtraInfo object for the user
        extra_info = ExtraInfo.objects.get(user=user)

        # Fetch the leave balance for the user
        leave_balance = LeaveBalance.objects.filter(empid__id=user.id).first()
        leave_per_year = LeavePerYear.objects.filter(empid__id=user.id).first()

        if not leave_balance or not leave_per_year:
            return JsonResponse({'error': 'Leave balance data not found'}, status=404)

        # Prepare the response data
        leave_data = {
            'casual_leave': {
                'allotted': leave_per_year.casual_leave_allotted,
                'taken': leave_balance.casual_leave_taken,
                'balance': leave_per_year.casual_leave_allotted - leave_balance.casual_leave_taken,
            },
            'special_casual_leave': {
                'allotted': leave_per_year.special_casual_leave_allotted,
                'taken': leave_balance.special_casual_leave_taken,
                'balance': leave_per_year.special_casual_leave_allotted - leave_balance.special_casual_leave_taken,
            },
            'earned_leave': {
                'allotted': leave_per_year.earned_leave_allotted,
                'taken': leave_balance.earned_leave_taken,
                'balance': leave_per_year.earned_leave_allotted - leave_balance.earned_leave_taken,
            },
            'commuted_leave': {
                'allotted': leave_per_year.commuted_leave_allotted,
                'taken': leave_balance.commuted_leave_taken,
                'balance': leave_per_year.commuted_leave_allotted - leave_balance.commuted_leave_taken,
            },
            'restricted_holiday': {
                'allotted': leave_per_year.restricted_holiday_allotted,
                'taken': leave_balance.restricted_holiday_taken,
                'balance': leave_per_year.restricted_holiday_allotted - leave_balance.restricted_holiday_taken,
            },
            'vacation_leave': {
                'allotted': leave_per_year.vacation_leave_allotted,
                'taken': leave_balance.vacation_leave_taken,
                'balance': leave_per_year.vacation_leave_allotted - leave_balance.vacation_leave_taken,
            },
        }

        # Return the leave balance data
        return JsonResponse({'leave_balance': leave_data}, status=200)

    except ExtraInfo.DoesNotExist:
        return JsonResponse({'error': 'User details not found'}, status=404)
    except Exception as e:
        # Handle any unexpected errors
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)    