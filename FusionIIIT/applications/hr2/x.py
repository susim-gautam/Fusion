def submit_cpda_adv_form(request):
    """POST request to submit a CPDA Advance Form. This endpoint is accessible only to authenticated users."""
    print("submit_cpda_adv_form")
    user = request.user
    try:
        user_id = ExtraInfo.objects.get(user=user).user_id
    except ExtraInfo.DoesNotExist:
        return JsonResponse({'error': 'User ID is required.'}, status=400)

    employee = get_object_or_404(ExtraInfo, user__id=user_id)

    if employee.user_type in ['faculty', 'staff', 'student']:
        try:
            form_data = json.loads(request.body.decode('utf-8'))
            form_data['employeeId'] = user_id

            # Ensure all decimal fields are correctly formatted
            decimal_fields = ['advanceDueAdjustment', 'balanceAvailable', 'advanceAmountPDA', 'amountCheckedInPDA']
            for field in decimal_fields:
                if field in form_data and form_data[field] not in [None, '']:
                    try:
                        form_data[field] = Decimal(form_data[field])
                    except InvalidOperation:
                        return JsonResponse({'error': f'Invalid decimal value for {field}'}, status=400)

            # Get the designation of the uploader
            holds_designation = HoldsDesignation.objects.filter(user=employee.user)
            if not holds_designation.exists():
                return JsonResponse({'error': "Uploader does not hold any designation"}, status=404)

            holds_designation_list = list(holds_designation)
            form_data['designation'] = str(holds_designation_list[0].designation)
            uploader_designation_obj = Designation.objects.filter(name=form_data['designation']).first()

            # Create CPDAAdvanceform instance
            cpda_adv_form = CPDAAdvanceform.objects.create(
                name=form_data.get('name'),
                designation=form_data.get('designation'),
                pfNo=form_data.get('pfNo'),
                purpose=form_data.get('purpose'),
                amountRequired=form_data.get('amountRequired'),
                advanceDueAdjustment=form_data.get('advanceDueAdjustment'),
                submissionDate=form_data.get('submissionDate'),
                balanceAvailable=form_data.get('balanceAvailable'),
                advanceAmountPDA=form_data.get('advanceAmountPDA'),
                amountCheckedInPDA=form_data.get('amountCheckedInPDA'),
                created_by=user
            )

            receiver_username = request.GET.get('username_reciever')
            employee_receiver = get_object_or_404(User, username=receiver_username)
            holds_designation = HoldsDesignation.objects.filter(user=employee_receiver).first()
            receiver_designation = str(holds_designation.designation) if holds_designation else None

            if not receiver_designation:
                return JsonResponse({'error': "Receiver designation does not exist"}, status=404)

            if not uploader_designation_obj:
                return JsonResponse({'error': "Uploader designation does not exist"}, status=404)

            src_module = "HR"
            src_object_id = str(cpda_adv_form.id)
            file_extra_JSON = {"type": "CPDAAdvance"}
            file_id = create_file(
                uploader=employee.user,
                uploader_designation=uploader_designation_obj,
                receiver=receiver_username,
                receiver_designation=receiver_designation,
                src_module=src_module,
                src_object_id=src_object_id,
                file_extra_JSON=file_extra_JSON,
                attached_file=None
            )
            messages.success(request, "CPDA form filled successfully")
            return HttpResponse("Success")
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
 # cpda advance Inbox

leave_form = LeaveForm.objects.create(
                    employeeId = id,
                    name = request.POST.get('name'),
                    designation =  request.POST.get('designation'),
                    submissionDate = request.POST.get('submissionDate'),
                    pfNo = request.POST.get('pfNo'),
                    departmentInfo = request.POST.get('departmentInfo'),
                    leaveStartDate = request.POST.get('leaveStartDate'),
                    leaveEndDate = request.POST.get('leaveEndDate'),
                    natureOfLeave = request.POST.get('natureOfLeave'),
                    purposeOfLeave = request.POST.get('purposeOfLeave'),
                    addressDuringLeave = request.POST.get('addressDuringLeave'),
                    academicResponsibility = request.POST.get('academicResponsibility'),
                    addministrativeResponsibiltyAssigned = request.POST.get('addministrativeResponsibiltyAssigned'),
                    created_by=creator,
                )