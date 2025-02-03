from django.db import models
from applications.globals.models import ExtraInfo
# from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from datetime import date

class Constants:
    # Class for various choices on the enumerations
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    DEPARTMENT = (
        ('CSE', 'CSE'),
        ('ME', 'Mechanical'),
        ('ECE', 'ECE'),
        ('DESIGN', 'DESIGN'),
    )
    CATEGORY = (
        ('SC', 'SC'),
        ('ST', 'ST'),
        ('OBC', 'OBC'),
        ('GENERAL', 'GENERAL'),
        ('PWD', 'PWD'),

    )
    MARITIAL_STATUS = (
        ('MARRIED', 'MARRIED'),
        ('UN-MARRIED', 'UN-MARRIED'),
        ('WIDOW', 'WIDOW'),

    )

    BLOOD_GROUP = (
        ('AB+', 'AB+'),
        ('O+', 'O+'),
        ('AB-', 'AB-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),

    )
    FOREIGN_SERVICE = (
        ('LIEN', 'LIEN'),
        ('DEPUTATION', 'DEPUTATION'),
        ('OTHER', 'OTHER'),
    )



# # Employee model
# class Employee(models.Model):
#     """
#     table for employee details
#     """
    
    
#     extra_info = models.OneToOneField(ExtraInfo, on_delete=models.CASCADE)
#     father_name = models.CharField(max_length=40, default='')
#     mother_name = models.CharField(max_length=40, default='')
#     religion = models.CharField(max_length=40, default='')
#     category = models.CharField(max_length=50, null=False, choices=Constants.CATEGORY)
#     cast = models.CharField(max_length=40, default='')
#     home_state = models.CharField(max_length=40, default='')
#     home_district = models.CharField(max_length=40, default='')
#     date_of_joining = models.DateField(null=True, blank=True)
#     designation = models.CharField(max_length=40, default='')
#     blood_group = models.CharField(
#         max_length=50, choices=Constants.BLOOD_GROUP)

#     def __str__(self):
#         return self.extra_info.user.first_name







# Employee Table
class Employee(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_details', primary_key=True)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    
    religion = models.CharField(max_length=20, null=True, blank=True)
    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    caste = models.CharField(max_length=50)
    home_state = models.CharField(max_length=50)
    home_district = models.CharField(max_length=50)
    full_address = models.TextField()
    date_of_joining = models.DateField()
    date_of_birth = models.DateField()
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    phone_number = models.CharField(max_length=15)
    personal_email = models.EmailField()
    emergency_contact_number = models.CharField(max_length=15)
    emergency_contact_name = models.CharField(max_length=100)

    def _str_(self):
        return f"{self.id.username} - Employee Details"








# # table for employee  confidential details
# class EmpConfidentialDetails(models.Model):
#     """
#     table for employee  confidential details
#     """
#     extra_info = models.OneToOneField(ExtraInfo, on_delete=models.CASCADE)
#     aadhar_no = models.BigIntegerField(default=0,
#                               validators=[MaxValueValidator(999999999999),MinValueValidator(99999999999)])
                              
#     maritial_status = models.CharField(
#         max_length=50, null=False, choices=Constants.MARITIAL_STATUS)
#     bank_account_no = models.IntegerField(default=0)
#     salary = models.IntegerField(default=0)

#     def __str__(self):
#         return self.extra_info.user.first_name



# Employee Confidential Table
class EmpConfidentialDetails(models.Model):
    id = models.AutoField(primary_key=True)
    empid = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='confidential_details')
    aadhar_number = models.CharField(max_length=12, unique=True)
    pan_number = models.CharField(max_length=10, unique=True)
    MARITAL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
    ]
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    personal_file_number = models.CharField(max_length=50, unique=True)
    bank_account_number = models.CharField(max_length=20, unique=True)
    ifsc_code = models.CharField(max_length=20,null=True)
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Confidential Details of {self.empid.empid.username}"









# # table for employee's dependent details
# class EmpDependents(models.Model):
#     """Table for employee's dependent details """
#     extra_info = models.OneToOneField(ExtraInfo, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100, default='')
#     gender = models.CharField(max_length=50, choices=Constants.GENDER_CHOICES)
#     dob = models.DateField(max_length=6, null=True)
#     relationship = models.CharField(max_length=40, default='')

#     def __str__(self):
#         return self.extra_info.user.first_name


# Employee Dependents Table
class EmpDependents(models.Model):
    id = models.AutoField(primary_key=True)
    empid = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='dependents')
    name = models.CharField(max_length=100)
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    relation = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=15)
    contact_email = models.EmailField(null=True, blank=True)
    date_of_birth = models.DateField()

    def __str__(self):
        return f"Dependent {self.name} of {self.empid.empid.username}"











class ForeignService(models.Model):
    """
    This table contains details about deputation, lien 
    and other foreign services of employee
    """
    extra_info = models.ForeignKey(ExtraInfo, on_delete=models.CASCADE)
    start_date = models.DateField(max_length=6, null=True, blank=True)
    end_date = models.DateField(max_length=6, null=True, blank=True)
    job_title = models.CharField(max_length=50, default='')
    organisation = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=300, default='')
    salary_source = models.CharField(max_length=100, default='')
    designation = models.CharField(max_length=100, default='')
    # award_name = models.CharField(max_length=100, default='')
    # award_type = models.CharField(max_length=100, default='')
    # achievement_date = models.CharField(max_length=100, default='')
    service_type = models.CharField(
        max_length=100, choices=Constants.FOREIGN_SERVICE)

    def __str__(self):
        return self.extra_info.user.first_name


class EmpAppraisalForm(models.Model):
    extra_info = models.ForeignKey(ExtraInfo, on_delete=models.CASCADE)
    year = models.DateField(max_length=6, null=True, blank=True)
    appraisal_form = models.FileField(
        upload_to='Hr2/appraisal_form', null=True, default=" ")

    def __str__(self):
        return self.extra_info.user.first_name


class WorkAssignemnt(models.Model):
    extra_info = models.ForeignKey(ExtraInfo, on_delete=models.CASCADE)
    start_date = models.DateField(max_length=6, null=True, blank=True)
    end_date = models.DateField(max_length=6, null=True, blank=True)
    job_title = models.CharField(max_length=50, default='')
    orders_copy = models.FileField(blank=True, null=True)

class LTCform(models.Model):
    id = models.AutoField(primary_key=True)
    employeeId = models.IntegerField()
    name = models.CharField(max_length=100, null=True)
    blockYear = models.TextField() #
    pfNo = models.IntegerField()
    basicPaySalary = models.IntegerField(null=True)
    designation = models.CharField(max_length=50)
    departmentInfo = models.CharField(max_length=50)
    leaveRequired = models.BooleanField(default=False,null=True) #
    leaveStartDate = models.DateField(null=True, blank=True)
    leaveEndDate = models.DateField(null=True, blank=True)
    dateOfDepartureForFamily = models.DateField(null=True, blank=True) #
    natureOfLeave = models.TextField(null=True,blank=True)
    purposeOfLeave = models.TextField(null=True,blank=True)
    hometownOrNot = models.BooleanField(default=False)
    placeOfVisit = models.TextField(max_length=100, null=True, blank=True) 
    addressDuringLeave = models.TextField(null=True)
    modeofTravel = models.TextField(max_length=10, null=True,blank=True) #
    detailsOfFamilyMembersAlreadyDone = models.JSONField(null=True,blank=True)
    detailsOfFamilyMembersAboutToAvail = models.JSONField(max_length=100, null=True,blank=True) 
    detailsOfDependents = models.JSONField(blank=True,null=True) 
    amountOfAdvanceRequired = models.IntegerField(null=True, blank=True)
    certifiedThatFamilyDependents = models.BooleanField(blank=True,null=True) 
    certifiedThatAdvanceTakenOn = models.DateField(null=True, blank=True) 
    adjustedMonth = models.TextField(max_length=50, null=True,blank=True)
    submissionDate = models.DateField(null=True)
    phoneNumberForContact = models.BigIntegerField()
    approved = models.BooleanField(null=True)
    approvedDate = models.DateField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='LTC_created_by')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='LTC_approved_by')



class CPDAAdvanceform(models.Model):
    id = models.AutoField(primary_key=True)
    employeeId = models.IntegerField(null=True)
    name = models.CharField(max_length=40,null=True)
    designation = models.CharField(max_length=40,null=True)
    pfNo = models.IntegerField(null=True)
    purpose = models.TextField(max_length=40, null=True)
    amountRequired = models.IntegerField(null=True)
    advanceDueAdjustment = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
   
    submissionDate = models.DateField(blank=True, null=True)
   
    balanceAvailable = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    advanceAmountPDA = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amountCheckedInPDA = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   
    approved = models.BooleanField(null=True)
    approvedDate = models.DateField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='CPDA_created_by')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True, related_name='CPDA_approved_by')#change 29th oct  2024

# class LeaveForm(models.Model):
#     id = models.AutoField(primary_key=True)
#     employeeId = models.IntegerField(null=True)
#     name = models.CharField(max_length=40,null=True)
#     designation = models.CharField(max_length=40,null=True)
#     submissionDate = models.DateField(blank=True, null=True)
#     pfNo = models.IntegerField(null=True)
#     departmentInfo = models.CharField(max_length=40,null=True)
#     # natureOfLeave = models.TextField(max_length=40,null=True)
#     natureOfLeave = models.JSONField(null=True)
#     leaveStartDate = models.DateField(blank=True, null=True)
#     leaveEndDate = models.DateField(blank=True, null=True)
   
#     purposeOfLeave = models.TextField(max_length=40,null=True)
#     addressDuringLeave = models.TextField(max_length=40, blank=True, null=True)

#     academicResponsibility = models.TextField(max_length=40, blank=True, null=True)
#     addministrativeResponsibiltyAssigned = models.TextField(max_length=40,null=True)

#     approved = models.BooleanField(null=True)
#     approvedDate = models.DateField(auto_now_add=True, null=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='Leave_created_by')
#     approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='Leave_approved_by')




 # Leave Application Table
class LeaveForm(models.Model):
    STATUS_CHOICES = [
        ('Accepted', 'Accepted'),
        ('Pending', 'Pending'),
        ('Rejected', 'Rejected'),
    ]
    
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_applications')
    name = models.CharField(max_length=40, null=True)
    designation = models.CharField(max_length=40, null=True)
    submissionDate = models.DateField(default=date.today)
    personalfileNo = models.IntegerField(null=True)
    departmentInfo = models.CharField(max_length=40, null=True)
    
    leaveStartDate = models.DateField(blank=True, null=True)
    leaveEndDate = models.DateField(blank=True, null=True)
    
    Noof_CasualLeave = models.IntegerField(default=0)
    Noof_specialCasualLeave = models.IntegerField(default=0)
    Noof_earnedLeave = models.IntegerField(default=0)
    Noof_commutedLeave = models.IntegerField(default=0)
    Noof_restrictedHoliday = models.IntegerField(default=0)
    Noof_vacationLeave = models.IntegerField(default=0)
    
    LeavingStation = models.BooleanField(default=False)
    StationLeave_startdate = models.DateField(blank=True, null=True)
    StationLeave_enddate = models.DateField(blank=True, null=True)
    Address_During_StationLeave = models.TextField(null=True, blank=True)
    Purpose_of_leave = models.TextField(null=True, blank=True)
    
    AcademicResponsibility_user = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='academic_responsibility_user'
    )
    AcademicResponsibility_accepted = models.BooleanField(default=False)
    
    AdministrativeResponsibility_user = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='administrative_responsibility_user'
    )
    AdministrativeResponsibility_accepted = models.BooleanField(default=False)
    
    Remarks = models.TextField(null=True, blank=True)
    
    approvedDate = models.DateField(auto_now_add=True, null=True)
    approved_by = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, related_name='leave_approved_by')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    # New field to store PDF as binary data
    attached_pdf = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return f"Leave Application {self.id} - {self.employee.empid.username}"





# class LeaveBalance(models.Model):
#     id = models.AutoField(primary_key=True)
#     employeeId = models.OneToOneField(ExtraInfo, on_delete=models.CASCADE)
#     casualLeave = models.IntegerField(default=0)
#     specialCasualLeave = models.IntegerField(default=0)
#     earnedLeave = models.IntegerField(default=0)
#     commutedLeave = models.IntegerField(default=0)
#     restrictedHoliday = models.IntegerField(default=0)
#     stationLeave = models.IntegerField(default=0)
#     vacationLeave = models.IntegerField(default=0)





# class LeaveBalance(models.Model):
#     id = models.AutoField(primary_key=True)
#     employeeId = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         limit_choices_to={'moduleaccess__hr': True}  # Only HR users
#     )

#     casualLeave_alloted = models.IntegerField(default=0)
#     casualLeave_taken = models.IntegerField(default=0)

#     specialCasualLeave_alloted = models.IntegerField(default=0)
#     specialCasualLeave_taken = models.IntegerField(default=0)

#     earnedLeave_alloted = models.IntegerField(default=0)
#     earnedLeave_taken = models.IntegerField(default=0)

#     commutedLeave_alloted = models.IntegerField(default=0)
#     commutedLeave_taken = models.IntegerField(default=0)

#     restrictedHoliday_alloted = models.IntegerField(default=0)
#     restrictedHoliday_taken = models.IntegerField(default=0)

#     vacationLeave_alloted = models.IntegerField(default=0)
#     vacationLeave_taken = models.IntegerField(default=0)





# Leave Balance Table
class LeaveBalance(models.Model):
    empid = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='leave_balance', primary_key=True)
    casual_leave_taken = models.IntegerField(default=0)
    special_casual_leave_taken = models.IntegerField(default=0)
    earned_leave_taken = models.IntegerField(default=0)
    commuted_leave_taken = models.IntegerField(default=0)
    restricted_holiday_taken = models.IntegerField(default=0)
    vacation_leave_taken = models.IntegerField(default=0)

    def __str__(self):
        return f"Leave Balance for {self.empid.empid.username}"


class LeavePerYear(models.Model):
    empid = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='yearly_leave', primary_key=True)
    casual_leave_allotted = models.IntegerField(default=0)
    special_casual_leave_allotted = models.IntegerField(default=0)
    earned_leave_allotted = models.IntegerField(default=0)
    commuted_leave_allotted = models.IntegerField(default=0)
    restricted_holiday_allotted = models.IntegerField(default=0)
    vacation_leave_allotted = models.IntegerField(default=0)

    def __str__(self):
        return f"Yearly Leave Allotment for {self.empid.empid.username}"







class Appraisalform(models.Model):
    id = models.AutoField(primary_key=True)
    employeeId = models.IntegerField(null=True)
    name = models.CharField(max_length=22)
    designation = models.CharField(max_length=50)
    disciplineInfo = models.CharField(max_length=22, null=True)
    specificFieldOfKnowledge = models.TextField(max_length=40, null=True)
    currentResearchInterests = models.TextField(max_length=40, null=True)
    coursesTaught = models.JSONField(max_length=100, null=True)
    newCoursesIntroduced = models.JSONField(max_length=100, null=True)
    newCoursesDeveloped = models.JSONField(max_length=100, null=True)
    otherInstructionalTasks = models.TextField(max_length=100, null=True)
    thesisSupervision = models.JSONField(max_length=100, null=True)
    sponsoredReseachProjects = models.JSONField(max_length=100, null=True)
    otherResearchElement = models.TextField(max_length=40, null=True)
    publication = models.TextField(max_length=40, null=True)
    referredConference = models.TextField(max_length=40, null=True)
    conferenceOrganised = models.TextField(max_length=40, null=True)
    membership = models.TextField(max_length=40, null=True)
    honours = models.TextField(max_length=40, null=True)
    editorOfPublications = models.TextField(max_length=40, null=True)
    expertLectureDelivered = models.TextField(max_length=40, null=True)
    membershipOfBOS = models.TextField(max_length=40, null=True)
    otherExtensionTasks = models.TextField(max_length=40, null=True)
    administrativeAssignment = models.TextField(max_length=40, null=True)
    serviceToInstitute = models.TextField(max_length=40, null=True)
    otherContribution = models.TextField(max_length=40, null=True)
    performanceComments = models.TextField(max_length=100, null=True)
    submissionDate = models.DateField(max_length=6, null=True)

    approved = models.BooleanField(null=True)
    approvedDate = models.DateField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='Appraisal_created_by')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='Appraisal_approved_by')


class CPDAReimbursementform(models.Model):
     id = models.AutoField(primary_key=True)
     employeeId = models.IntegerField(null=True)
     name = models.CharField(max_length=50)
     designation = models.CharField(max_length=50)
     pfNo = models.IntegerField()
     advanceTaken = models.IntegerField()
     purpose = models.TextField()
     adjustmentSubmitted = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
     balanceAvailable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
     advanceDueAdjustment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
     advanceAmountPDA = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
     amountCheckedInPDA = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #  submissionDate = models.DateField(auto_now_add=True)
     submissionDate = models.DateField(blank=True, null=True)
     approved = models.BooleanField(null=True)
     approvedDate = models.DateField(auto_now_add=True, null=True)
     created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='CPDAR_created_by')
     approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='CPDAR_approved_by')
   




