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
from applications.filetracking.sdk.methods import *





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
        #print(f"Current Designation: {current_designation.designation.name if current_designation else None}")  # Debugging
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
        #print(f"Error in check_hr_access: {str(e)}")  # Debugging
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
        #print("User has HR access. Performing additional actions...")  # Debugging
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
        
        # Get the academic responsibility designation
        try:
            academic_responsibility_designation = Designation.objects.get(name=academic_responsibility_designation)
        except Designation.DoesNotExist:
            return JsonResponse({'error': 'Academic Responsibility designation not found'}, status=404)
        

        # Get the administrative responsibility user
        try:
            administrative_responsibility_user = Employee.objects.get(id=administrative_responsibility_id)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Administrative Responsibility user not found'}, status=404)
        
        # Get the administrative responsibility designation
        try:
            administrative_responsibility_designation = Designation.objects.get(name=administrative_responsibility_designation)
        except Designation.DoesNotExist:
            return JsonResponse({'error': 'Administrative Responsibility designation not found'}, status=404)

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
        attached_pdf_name = None
        if attached_pdf:
            attached_pdf_binary = attached_pdf.read()
            attached_pdf_name=attached_pdf.name

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
            AcademicResponsibility_status='Pending',
            AdministrativeResponsibility_user=administrative_responsibility_user,
            AdministrativeResponsibility_designation=administrative_responsibility_designation,
            AdministrativeResponsibility_status='Pending',
            first_recieved_by=first_recieved_by_user,
            first_recieved_designation=first_recieved_designation,
            status='Pending',
            attached_pdf=attached_pdf_binary,
            attached_pdf_name=attached_pdf_name,

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
    


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_leave_form_by_id(request, form_id):
    """
    API endpoint to get the leave form by ID.
    """
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        #print("0")
        # Get the employee associated with the user
        employee = Employee.objects.filter(id=user)
        if not employee.exists():
            return JsonResponse({'error': 'Employee not found'}, status=404)
        employee = employee.first()
        # get leave balance of employee
        leave_balance = LeaveBalance.objects.filter(empid=employee).first()
        if not leave_balance:
            return JsonResponse({'error': 'Leave balance not found'}, status=404)
        # get leave per year of employee
        leave_per_year = LeavePerYear.objects.filter(empid=employee).first()
        if not leave_per_year:
            return JsonResponse({'error': 'Leave per year not found'}, status=404)
        

        #print("1")
        # Get the leave form by ID
        leave_form = LeaveForm.objects.filter(id=form_id)
        if not leave_form.exists():
            return JsonResponse({'error': 'Leave form not found'}, status=404)
        leave_form = leave_form.first()
        #print("2")
        # Access the AcademicResponsibility_user (Employee object)
        academic_responsibility_employee = leave_form.AcademicResponsibility_user

        # Access the User object from the Employee object
        academic_responsibility_user = academic_responsibility_employee.id
        
        # access name of academic_responsibility_user
        academic_responsibility_name = academic_responsibility_user.first_name + " " + academic_responsibility_user.last_name
        #print(academic_responsibility_name)

        # Access designations of academic_responsibility_user
        academic_responsibility_designation = leave_form.AcademicResponsibility_designation.name


        # Access the AdministrativeResponsibility_user (Employee object)
        administrative_responsibility_employee = leave_form.AdministrativeResponsibility_user

        # Access the User object from the Employee object
        administrative_responsibility_user = administrative_responsibility_employee.id

        # access name of administrative_responsibility_user
        administrative_responsibility_name = administrative_responsibility_user.first_name + " " + administrative_responsibility_user.last_name

        # Access designations of administrative_responsibility_user
        administrative_responsibility_designation = leave_form.AdministrativeResponsibility_designation.name

        # Access the first_recieved_by (Employee object)
        first_recieved_by_employee = leave_form.first_recieved_by

        # Access the User object from the Employee object
        first_recieved_by_user = first_recieved_by_employee.id


        # access name of first_recieved_by_user
        first_recieved_by_name = first_recieved_by_user.first_name + " " + first_recieved_by_user.last_name

        # Access designations of first_recieved_by_user
        first_recieved_by_designation = leave_form.first_recieved_designation.name

        #print("2.5")


        # attcahed file name only
        attached_pdf_name = None
        if leave_form.attached_pdf:
            attached_pdf_name = leave_form.attached_pdf_name
        
    #     #  if status is accepeted send aproved date and and approve by and approved by designationapprovedDate = models.DateField(auto_now_add=True, null=True)
    # approved_by = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, related_name='leave_approved_by')
    # approved_by_designation=models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, related_name='leave_approved_by_designation')

        if leave_form.status == 'Accepted':
            approved_by_employee = leave_form.approved_by
            approved_by_user = approved_by_employee.id
            approved_by_name = approved_by_user.first_name + " " + approved_by_user.last_name
            approved_by_designation = leave_form.approved_by_designation.name
            approved_date = leave_form.approvedDate
        else:
            approved_by_name = None
            approved_by_designation = None
            approved_date = None 

        leave_form_data = {
            'id': leave_form.id,
            'name': leave_form.name,
            'designation': leave_form.designation,
            'pfno': leave_form.personalfileNo,
            'submissionDate': leave_form.submissionDate,
            'department': leave_form.departmentInfo,
            'leaveStartDate': leave_form.leaveStartDate,
            'leaveEndDate': leave_form.leaveEndDate,
            'purpose': leave_form.Purpose_of_leave,
            'casualLeave': leave_form.Noof_CasualLeave,
            'cadualLeaveBalance': leave_per_year.casual_leave_allotted - leave_balance.casual_leave_taken if leave_per_year.casual_leave_allotted and leave_balance.casual_leave_taken else 'N/A',
            'vacationLeave': leave_form.Noof_vacationLeave,
            'vacationLeaveBalance': leave_per_year.vacation_leave_allotted - leave_balance.vacation_leave_taken if leave_per_year.vacation_leave_allotted and leave_balance.vacation_leave_taken else 'N/A',
            'earnedLeave': leave_form.Noof_earnedLeave,
            'earnedLeaveBalance': leave_per_year.earned_leave_allotted - leave_balance.earned_leave_taken if leave_per_year.earned_leave_allotted and leave_balance.earned_leave_taken else 'N/A',
            'commutedLeave': leave_form.Noof_commutedLeave,
            'commutedLeaveBalance': leave_per_year.commuted_leave_allotted - leave_balance.commuted_leave_taken if leave_per_year.commuted_leave_allotted and leave_balance.commuted_leave_taken else 'N/A',
            'specialCasualLeave': leave_form.Noof_specialCasualLeave,
            'specialCasualLeaveBalance': leave_per_year.special_casual_leave_allotted - leave_balance.special_casual_leave_taken if leave_per_year.special_casual_leave_allotted and leave_balance.special_casual_leave_taken else 'N/A',
            'restrictedHoliday': leave_form.Noof_restrictedHoliday,
            'restrictedHolidayBalance': leave_per_year.restricted_holiday_allotted - leave_balance.restricted_holiday_taken if leave_per_year.restricted_holiday_allotted and leave_balance.restricted_holiday_taken else 'N/A',
            'remarks': leave_form.Remarks,
            'stationLeave': leave_form.LeavingStation,
            'stationLeaveStartDate': leave_form.StationLeave_startdate,
            'stationLeaveEndDate': leave_form.StationLeave_enddate,
            'stationLeaveAddress': leave_form.Address_During_StationLeave,
            'academicResponsibility': academic_responsibility_name,
            'academicResponsibilityDesignation': academic_responsibility_designation,
            'academicResponsibilityStatus': leave_form.AcademicResponsibility_status,
            'administrativeResponsibility': administrative_responsibility_name,
            'administrativeResponsibilityDesignation': administrative_responsibility_designation,
            'administrativeResponsibilityStatus': leave_form.AdministrativeResponsibility_status,
            'firstRecievedBy': first_recieved_by_name,
            'firstRecievedByDesignation': first_recieved_by_designation,
            'status': leave_form.status,
            'attachedPdfName': attached_pdf_name,
            'approvedBy': approved_by_name,
            'approvedByDesignation': approved_by_designation,
            'approvedDate': approved_date,
        }
        # #print("3") 
        # #print(leave_form_data)
        return JsonResponse({'leave_form': leave_form_data}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handle_leave_academic_responsibility(request, form_id):
    """
    API endpoint to handle the academic responsibility of a leave form.
    """
    user = request.user
    print("0")
    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        
        # get employee of user
        employee = Employee.objects.filter(id=user)
        if not employee.exists():
            return JsonResponse({'error': 'Employee not found'}, status=404)
        
        
        # get last selected role of user
        extra_info = ExtraInfo.objects.filter(user=user)
        if not extra_info.exists():
            return JsonResponse({'error': 'ExtraInfo not found'}, status=404)
        extra_info = extra_info.first()

        last_selected_role = extra_info.last_selected_role

        # get leave form by id
        leave_form = LeaveForm.objects.filter(id=form_id)

        # check if leave form exists
        if not leave_form.exists():
            return JsonResponse({'error': 'Leave form not found'}, status=404)
        
        leave_form = leave_form.first()

        # check if user has access to handle academic responsibility
        

        if user != leave_form.AcademicResponsibility_user.id:
            return JsonResponse({'error': 'You do not have access to handle academic responsibility for this leave form'}, status=403)
        print("2")
        #get designation of academic responsibility user
        academic_responsibility_designation = leave_form.AcademicResponsibility_designation

        # check if user has access to handle academic responsibility
        if last_selected_role!=academic_responsibility_designation.name:
            return JsonResponse({'error': 'You do not have access to handle academic responsibility for this leave form'}, status=403)
        
        # get action
        data = json.loads(request.body)
        action = data.get('action')
        print(action)
        # check if action is valid
        if action not in ['accept', 'reject']:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        # handle reject
        if action == 'reject':
            leave_form.AcademicResponsibility_status = 'Rejected'
            leave_form.status = 'Rejected'
            leave_form.save()
            return JsonResponse({'message': 'Academic responsibility rejected successfully'}, status=200)
        
        # handle accept
        leave_form.AcademicResponsibility_status = 'Accepted'
        # check if administrative responsibility is pending or rejected
        if leave_form.AdministrativeResponsibility_status == 'Pending' or leave_form.AdministrativeResponsibility_status == 'Rejected':
            leave_form.save()
            return JsonResponse({'message': 'Academic responsibility accepted successfully'}, status=200)
        
        # check if administrative responsibility is accepted
        if leave_form.AdministrativeResponsibility_status == 'Accepted':
            uploader_employee = leave_form.employee
            # get user of uploader employee
            uploader = uploader_employee.id
            uploader_designation=leave_form.designation

            first_recieved_by_employee = leave_form.first_recieved_by
            first_recieved_by_user = first_recieved_by_employee.id
            # get username of first_recieved_by_user
            receiver = first_recieved_by_user.username
            # get designation of first recieved by user
            receiver_designation = leave_form.first_recieved_designation
            src_module = "HR"
            src_object_id = str(leave_form.id)
            file_extra_JSON = {"type": "Leave"}

            file_id = create_file(
                uploader=uploader,
                uploader_designation=uploader_designation,
                receiver=receiver,
                receiver_designation=receiver_designation,
                src_module=src_module,
                src_object_id=src_object_id,
                file_extra_JSON=file_extra_JSON,
                attached_file=None  # Attach any file if necessary
            )
            leave_form.file_id = file_id
            leave_form.save()
            return JsonResponse({'message': 'Academic responsibility accepted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def handle_leave_administrative_responsibility(request, form_id):
    """
    API endpoint to handle the administrative responsibility of a leave form.
    """
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        # get employee of user
        employee = Employee.objects.filter(id=user)
        if not employee.exists():
            return JsonResponse({'error': 'Employee not found'}, status=404)
        
        # get last selected role of user
        extra_info = ExtraInfo.objects.filter(user=user)
        if not extra_info.exists():
            return JsonResponse({'error': 'ExtraInfo not found'}, status=404)
        extra_info = extra_info.first()

        last_selected_role = extra_info.last_selected_role

        # get leave form by id
        leave_form = LeaveForm.objects.filter(id=form_id)

        # check if leave form exists
        if not leave_form.exists():
            return JsonResponse({'error': 'Leave form not found'}, status=404)
        
        leave_form = leave_form.first()

        # check if user has access to handle administrative responsibility
        if user != leave_form.AdministrativeResponsibility_user.id:
            return JsonResponse({'error': 'You do not have access to handle administrative responsibility for this leave form'}, status=403)
        #get designation of administrative responsibility user
        administrative_responsibility_designation = leave_form.AdministrativeResponsibility_designation

        # check if user has access to handle administrative responsibility
        if last_selected_role!=administrative_responsibility_designation.name:
            return JsonResponse({'error': 'You do not have access to handle administrative responsibility for this leave form'}, status=403)
        
        # get action
        data = json.loads(request.body)
        action = data.get('action')
        print(action)

        # check if action is valid
        if action not in ['accept', 'reject']:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        # handle reject
        if action == 'reject':
            leave_form.AdministrativeResponsibility_status = 'Rejected'
            leave_form.status = 'Rejected'
            leave_form.save()
            return JsonResponse({'message': 'Administrative responsibility rejected successfully'}, status=200)
        
        # handle accept
        leave_form.AdministrativeResponsibility_status = 'Accepted'
        # check if academic responsibility is pending or rejected
        if leave_form.AcademicResponsibility_status == 'Pending' or leave_form.AcademicResponsibility_status == 'Rejected':
            leave_form.save()
            return JsonResponse({'message': 'Administrative responsibility accepted successfully'}, status=200)

        
        # check if academic responsibility is accepted
        if leave_form.AcademicResponsibility_status == 'Accepted':
            uploader_employee = leave_form.employee
            # get user of uploader employee
            uploader = uploader_employee.id
            uploader_designation=leave_form.designation
            
            first_recieved_by_employee = leave_form.first_recieved_by
            first_recieved_by_user = first_recieved_by_employee.id
            
            # get username of first_recieved_by_user
            receiver = first_recieved_by_user.username
            # get designation of first recieved by user
            
            receiver_designation = leave_form.first_recieved_designation 
            
            src_module = "HR"
            src_object_id = str(leave_form.id)
            file_extra_JSON = {"type": "Leave"}
            
            file_id = create_file(
                uploader=uploader,
                uploader_designation=uploader_designation,
                receiver=receiver,
                receiver_designation=receiver_designation,
                src_module=src_module,
                src_object_id=src_object_id,
                file_extra_JSON=file_extra_JSON,
                attached_file=None  # Attach any file if necessary
            )
            print(file_id)
            leave_form.file_id = file_id
            
            leave_form.save()
            return JsonResponse({'message': 'Administrative responsibility accepted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)


# def get_leave_inbox get leave forms where acdemic responsibility or administrative responsibility

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_leave_inbox(request):
    """
    API endpoint to get the leave inbox for the authenticated user.
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
        # get last selected role of user
        query_date=request.GET.get('date')
        
        # if date in not set date is 1 year back
        if not query_date:
            # set 1 year back date
            query_date = datetime.now().date() - timedelta(days=365)
        else:
            query_date = datetime.strptime(query_date, '%Y-%m-%d').date()
        extra_info = ExtraInfo.objects.filter(user=user)
        if not extra_info.exists():
            return JsonResponse({'error': 'ExtraInfo not found'}, status=404)
        extra_info = extra_info.first()

        last_selected_role = extra_info.last_selected_role


        # get academic responsibility forms till query date
        academic_responsibility_forms = LeaveForm.objects.filter(AcademicResponsibility_user=employee, submissionDate__gte=query_date)
        # filter by last selected role
        academic_responsibility_forms = [form for form in academic_responsibility_forms if form.AcademicResponsibility_designation.name == last_selected_role]

        # get administrative responsibility forms
        administrative_responsibility_forms = LeaveForm.objects.filter(AdministrativeResponsibility_user=employee, submissionDate__gte=query_date)
        # filter by last selected role
        administrative_responsibility_forms = [form for form in administrative_responsibility_forms if form.AdministrativeResponsibility_designation.name == last_selected_role]

        # Prepare the academic res response data
        academic_res_inbox = []
        # send only id submissionDate, status, leaveStartDate, leaveEndDate,
        for form in academic_responsibility_forms:
            academic_res_inbox.append({
                'id': form.id,
                'name': form.name,
                'designation': form.designation,
                'submissionDate': form.submissionDate,
                'status': form.AcademicResponsibility_status,
                'leaveStartDate': form.leaveStartDate,
                'leaveEndDate': form.leaveEndDate,
            })
        
        # Prepare the administrative res response data
        administrative_res_inbox = []
        # send only id submissionDate, status, leaveStartDate, leaveEndDate,
        for form in administrative_responsibility_forms:
            administrative_res_inbox.append({
                'id': form.id,
                'name': form.name,
                'designation': form.designation,
                'submissionDate': form.submissionDate,
                'status': form.AdministrativeResponsibility_status,
                'leaveStartDate': form.leaveStartDate,
                'leaveEndDate': form.leaveEndDate,
            })

        

        # get leave file 
        user_id = ExtraInfo.objects.get(user=user).user_id
        ext= ExtraInfo.objects.get(user__id=user_id)
        username = ext.user
        designation = ext.last_selected_role
        reciever_designation = None
        if designation:
            reciever_designation = designation
        print("9")
        print(username,designation)
        inbox = view_inbox(username=username, designation=reciever_designation, src_module="HR")
        # type== leave and upload_date> query date
        filtered_inbox = [
            i for i in inbox
            if i['file_extra_JSON']['type'] == "Leave" and
            datetime.strptime(i['upload_date'], "%Y-%m-%dT%H:%M:%S.%f").date() >= query_date ]

        # in fileterd_inbox  get designation name by designatetion id and fetch status of each leave form by src_object_id
        for i in filtered_inbox:
            if i['designation']:
                designation = Designation.objects.get(id=i['designation'])
                i['designation'] = designation.name
            src_object_id = i['src_object_id']
            leave_form = LeaveForm.objects.get(id=src_object_id)
            i['status'] = leave_form.status
        #print("10")
        

        return JsonResponse({
            'leave_inbox': filtered_inbox,
            'academic_res_inbox': academic_res_inbox,
            'administrative_res_inbox': administrative_res_inbox
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

# download attached pdf for leave form

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def download_leave_form_pdf(request, form_id):
    """
    API endpoint to download the attached PDF for a leave form.
    """
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        # Get the leave form by ID
        leave_form = LeaveForm.objects.filter(id=form_id)
        if not leave_form.exists():
            return JsonResponse({'error': 'Leave form not found'}, status=404)
        leave_form = leave_form.first()



        # Check if the leave form has an attached PDF
        if not leave_form.attached_pdf:
            return JsonResponse({'error': 'No attached PDF found for this leave form'}, status=404)

        # convert binary to file
        attached_pdf = leave_form.attached_pdf
        attached_pdf_name = leave_form.attached_pdf_name
        response = HttpResponse(attached_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{attached_pdf_name}"'
        return response
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)