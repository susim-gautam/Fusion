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
    


    