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
from datetime import datetime, timedelta
from .models import LeaveBalance, LeavePerYear, EmpConfidentialDetails , Employee, LeaveForm
from applications.globals.models import ExtraInfo





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
    


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def search_employees(request):
    """
    API endpoint to search for employees based on the given search query.
    Returns:
        - A JSON response containing the list of employees matching the search query.
    """
    user = request.user

    # Check if the user has HR access
    if not check_hr_access(request):
        return JsonResponse({'error': 'HR access required'}, status=403)

    try:
        search_text = request.GET.get("search_text", "").strip()

        if not search_text:
            return JsonResponse({"error": "Search text is required"}, status=400)

        users = User.objects.filter(username__icontains=search_text)
        user_list = []

        for user in users:
        
            # Fetch designations from HoldsDesignation model
            designations = HoldsDesignation.objects.filter(user=user)

            if not designations.exists():
                continue  # Skip users without designations

            for hd in designations:
                
                user_list.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "designation": hd.designation.name,  # Assuming designation has a 'name' field
                })

        return JsonResponse({"employees": user_list}, status=200)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    

# get my form initials name, last_selected_role, and department, pfno

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_form_initials(request):
    """
    API endpoint to get the form initials for the authenticated user.
    Returns:
        - A JSON response containing the form initials for the authenticated user.
    """
    user = request.user

    # Check if the user is authenticated
    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        # fecth employee
        employee = Employee.objects.filter(id=user)
        if not employee.exists():
            return JsonResponse({'error': 'Employee not found'}, status=404)
        employee = employee.first()
        # fetch extra info
        extra_info = ExtraInfo.objects.filter(user=user)
        if not extra_info.exists():
            return JsonResponse({'error': 'ExtraInfo not found'}, status=404)
        extra_info = extra_info.first()

        Empconfidential=EmpConfidentialDetails.objects.filter(empid=employee)
        if not Empconfidential.exists():
            return JsonResponse({'error': 'EmpConfidentialDetails not found'}, status=404)
        Empconfidential=Empconfidential.first()
        dpt=extra_info.department

        
        return JsonResponse({
             
            'name': user.first_name+" "+user.last_name,
            'last_selected_role': extra_info.last_selected_role,
            'pfno': Empconfidential.personal_file_number,
            'department': dpt.name if dpt else None,


        }, status=200)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)










@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def submit_leave_form(request):
    """
    API endpoint to submit a leave form for the authenticated user.
    """
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        form_data = request.POST
        files = request.FILES

        # Extract form data
        name = form_data.get('name')
        designation = form_data.get('designation')
        pfno = form_data.get('pfno')
        submissionDate = form_data.get('date')
        department = form_data.get('department')
        leave_start_date = form_data.get('leaveStartDate')
        leave_end_date = form_data.get('leaveEndDate')
        purpose = form_data.get('purpose')
        casual_leave = form_data.get('casualLeave', 0)
        vacation_leave = form_data.get('vacationLeave', 0)
        earned_leave = form_data.get('earnedLeave', 0)
        commuted_leave = form_data.get('commutedLeave', 0)
        special_casual_leave = form_data.get('specialCasualLeave', 0)
        restricted_holiday = form_data.get('restrictedHoliday', 0)
        remarks = form_data.get('remarks')
        station_leave = form_data.get('stationLeave', 'false').lower() == 'true'
        station_leave_start_date = form_data.get('stationLeaveStartDate')
        station_leave_end_date = form_data.get('stationLeaveEndDate')
        station_leave_address = form_data.get('stationLeaveAddress')
        academic_responsibility_id = form_data.get('academicResponsibility')
        academic_responsibility_designation = form_data.get('academicResponsibility_designation')
        administrative_responsibility_id = form_data.get('administrativeResponsibility')
        administrative_responsibility_designation = form_data.get('administrativeResponsibility_designation')
        first_recieved_by_id = form_data.get('forwardTo')
        first_recieved_designation = form_data.get('forwardTo_designation')
        attached_pdf = files.get('attached_pdf')

        # Validate required fields
        if not all([name, designation, pfno, department, leave_start_date, leave_end_date, purpose, remarks]):
            return JsonResponse({'error': 'All required fields must be provided'}, status=400)

        # Validate leave dates
        try:
            leave_start_date = datetime.strptime(leave_start_date, "%Y-%m-%d").date()
            leave_end_date = datetime.strptime(leave_end_date, '%Y-%m-%d').date()
            if leave_end_date < leave_start_date:
                return JsonResponse({'error': 'Leave end date cannot be before start date'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Invalid leave date format. Use YYYY-MM-DD'}, status=400)

        # Validate station leave fields if station leave is checked
        if station_leave:
            if not all([station_leave_start_date, station_leave_end_date, station_leave_address]):
                return JsonResponse({'error': 'Station leave details are required when station leave is checked'}, status=400)
            try:
                station_leave_start_date = datetime.strptime(station_leave_start_date, '%Y-%m-%d').date()
                station_leave_end_date = datetime.strptime(station_leave_end_date, '%Y-%m-%d').date()
                if station_leave_end_date < station_leave_start_date:
                    return JsonResponse({'error': 'Station leave end date cannot be before start date'}, status=400)
            except ValueError:
                return JsonResponse({'error': 'Invalid station leave date format. Use YYYY-MM-DD'}, status=400)
        else:
            # Set station leave fields to None if station leave is not checked
            station_leave_start_date = None
            station_leave_end_date = None
            station_leave_address = None

        # Get the employee associated with the user
        try:
            employee = Employee.objects.get(id=user.id)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found'}, status=404)

        # Get the academic responsibility user
        try:
            academic_responsibility_user = Employee.objects.get(id=academic_responsibility_id)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Academic Responsibility user not found'}, status=404)

        # Get the administrative responsibility user
        try:
            administrative_responsibility_user = Employee.objects.get(id=administrative_responsibility_id)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Administrative Responsibility user not found'}, status=404)

        # Get the first received by user
        try:
            first_recieved_by_user = Employee.objects.get(id=first_recieved_by_id)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'First Received By user not found'}, status=404)

        # Get the first received designation
        try:
            first_recieved_designation = Designation.objects.get(name=first_recieved_designation)
        except Designation.DoesNotExist:
            return JsonResponse({'error': 'First Received By designation not found'}, status=404)

        # Handle attached PDF file
        attached_pdf_binary = None
        if attached_pdf:
            attached_pdf_binary = attached_pdf.read()

        # Create and save the leave form
        leave_form = LeaveForm(
            employee=employee,
            name=name,
            designation=designation,
            personalfileNo=pfno,
            submissionDate=submissionDate,
            departmentInfo=department,
            leaveStartDate=leave_start_date,
            leaveEndDate=leave_end_date,
            Purpose_of_leave=purpose,
            Noof_CasualLeave=casual_leave,
            Noof_vacationLeave=vacation_leave,
            Noof_earnedLeave=earned_leave,
            Noof_commutedLeave=commuted_leave,
            Noof_specialCasualLeave=special_casual_leave,
            Noof_restrictedHoliday=restricted_holiday,
            Remarks=remarks,
            LeavingStation=station_leave,
            StationLeave_startdate=station_leave_start_date,
            StationLeave_enddate=station_leave_end_date,
            Address_During_StationLeave=station_leave_address,
            AcademicResponsibility_user=academic_responsibility_user,
            AcademicResponsibility_designation=academic_responsibility_designation,
            AdministrativeResponsibility_user=administrative_responsibility_user,
            AdministrativeResponsibility_designation=administrative_responsibility_designation,
            first_recieved_by=first_recieved_by_user,
            first_recieved_designation=first_recieved_designation,
            status='Pending',
            attached_pdf=attached_pdf_binary,
        )
        leave_form.save()
        return JsonResponse({'message': 'Leave form submitted successfully'}, status=200)

    except ValidationError as e:
        return JsonResponse({'error': f'Validation error: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_leave_requests(request):
    """
    API endpoint to get the leave requests for the authenticated user.
    """
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        # Get the employee associated with the user
        employee = Employee.objects.filter(id=user)
        

        if not employee.exists():
            return JsonResponse({'error': 'Employee not found'}, status=404)
        employee = employee.first()
        query_date=request.GET.get('date')
        if not query_date:
            # set 1 year back date
            query_date = datetime.now().date() - timedelta(days=365)
        else:
            query_date = datetime.strptime(query_date, '%Y-%m-%d').date()
        # Get the leave forms for the employee
        leave_forms = LeaveForm.objects.filter(employee=employee, submissionDate__gte=query_date)

        # Prepare the response data
        leave_requests = []
        # send only id submissionDate, status, leaveStartDate, leaveEndDate,
        for form in leave_forms:
            leave_requests.append({
                'id': form.id,
                'name': form.name,
                'submissionDate': form.submissionDate,
                'status': form.status,
                'leaveStartDate': form.leaveStartDate,
                'leaveEndDate': form.leaveEndDate,
            })
        
        return JsonResponse({'leave_requests': leave_requests}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    