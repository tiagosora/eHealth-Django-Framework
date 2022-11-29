from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash

from app.forms import *
from app.models import *

def home(request):
    return render(request, 'index.html', {'data': "data"})

def contact(request):
    return render(request, 'contact.html', {'data': "data"})

def about(request):
    return render(request, 'about.html', {'data': "data"})

def appointment(request):
    if not (request.user.is_authenticated or request.user.username):
        return redirect('login')
    if request.method == 'POST':
        form = NewAppointmentForm(request.POST)
        if form.is_valid():
            department=form.cleaned_data["department"]
            date=form.cleaned_data["date"]
            message=form.cleaned_data["message"]
  
            user_data = User.objects.get(username=request.user.username)
            patient = Patient.objects.get(user=user_data)
            
            appointment = Appointment(patient=patient, department=department, date=date, message=message)
            appointment.save()
            appointment.refresh_from_db()
            return redirect('appointments')
    else:
        form = NewAppointmentForm()
    return render(request, 'appointment.html', {'form': form})


# SignUp
def signup(request):
    if request.method == 'POST': 
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            print("NEW USER INSERTED")
            new_user = form.save()
            email=form.cleaned_data["email"]
            address=form.cleaned_data["address"]
            patient = Patient(user=new_user,email=email,address=address)
            patient.save()
            new_user.refresh_from_db()
            return redirect('login')
    else:
        form = CreateAccountForm()
    return render(request, 'signup.html', {'form': form})


def appointmentsView(request): 
    if request.user.is_authenticated:
        data = {}
        if request.method == 'GET':
            data['appointments'] = list(Appointment.objects.all())
            
            if not request.user.is_superuser:
                patient = Patient.objects.get(user=User.objects.get(username=request.user.username))
                user_appointments = []
                for ap in data['appointments']:
                    if (patient) == ap.patient:
                        user_appointments.append(ap)
                data['appointments'] = user_appointments
        data["form"] = searchForm()
        return render(request, 'appointments.html', data)


def prefillAppointmentForm(appointment):
    # Pre-fill the form with current data
    form = UpdateAppointmentForm()
    form.fields['department'].initial = appointment.department.id
    form.fields['date'].initial = appointment.date
    form.fields['message'].initial = appointment.message
    return form


def updateAppointments(request, id):
    if request.user.is_authenticated:
        data = {}
        appointment = Appointment.objects.get(id=id)
        if request.method == "POST":
            form = UpdateAppointmentForm(request.POST)
            if form.is_valid():
                appointment = Appointment.objects.filter(id=id)[0]
                appointment.department = form.cleaned_data['department']
                appointment.date = form.cleaned_data['date']
                appointment.message = form.cleaned_data['message']
                appointment.save()
                return redirect('appointments')
                
        else:
            form = prefillAppointmentForm(appointment)
            data['form'] = form
            return render(request, 'updateAppointments.html', data)
        
    else:
        return redirect('login')



def removeAppointments(request):
    if request.method == 'POST':
        appointment = Appointment.objects.filter(id=request.POST['id'])
        print("APPOINTMENT DELETED: ", appointment.delete())
    return redirect('appointments')


def departmentsView(request):
    if request.user.is_authenticated and request.user.is_superuser:
        data = {}
        data['departments'] = list(Department.objects.all())
        data["form"] = searchForm()
        data['addform'] = NewDepartmentForm()
        return render(request, 'departments.html', data)
    else: return pageNotFoundView(request)

def addNewDepartment(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            form = NewDepartmentForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data["name"]
                department = Department(name=name)
                department.save()
                department.refresh_from_db()
        return redirect('departments')
    else: return pageNotFoundView(request)


def removeDepartments(request):
    if request.method == 'POST':
        department = Department.objects.filter(id=request.POST['id'])
        print("DEPARTMENTE DELETED: ", department.delete())
    return redirect('departments')


def appointmentsSearchView(request):
    data = {}
    if request.method == 'POST':
        form = searchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            patient_result = Appointment.objects.filter(patient__user__username__icontains=query)
            department_result = Appointment.objects.filter(department__name__icontains=query)
            message_result = Appointment.objects.filter(message__icontains=query)
            results = list(set(list(list(patient_result) + list(department_result) + list(message_result))))
            if len(results) != 0:
                data['appointments'] = results
            else:
                data['appointments'] = list(Appointment.objects.all())

            if not request.user.is_superuser:
                patient = Patient.objects.get(user=User.objects.get(username=request.user.username))
                user_appointments = []
                for ap in data['appointments']:
                    if (patient) == ap.patient:
                        user_appointments.append(ap)
                data['appointments'] = user_appointments
        form = searchForm()
        data['form'] = form
        return render(request, 'appointments.html', data)
    else:
        form = searchForm()
        data['form'] = form
    return render(request, 'appointments.html', data)

def departmentsSearchView(request):
    data = {}
    if request.method == 'POST':
        form = searchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            department_name = Department.objects.filter(name__icontains=query)
            department_id = Department.objects.filter(id__icontains=query)
            results = list(set(list(department_name) + list(department_id)))
            if len(results) != 0:
                data['departments'] = results
            else:
                data['departments'] = list(Department.objects.all())

        form = searchForm()
        data['form'] = form
        data['addform'] = NewDepartmentForm()
        return render(request, 'departments.html', data)
    else:
        form = searchForm()
        data['form'] = form
    return render(request, 'departments.html', data)

def pageNotFoundView(request):
    out = render(request, 'pagenotfound.html')
    out.status_code = 404
    return out

def prefillProfileForm(profile):
    form = ProfileUpdateForm()
    form.fields['username'].initial = profile.user.username
    form.fields['first_name'].initial = profile.user.first_name
    form.fields['last_name'].initial = profile.user.last_name
    form.fields['email'].initial = profile.email
    form.fields['address'].initial = profile.address
    return form
    
def profileView(request):   
    if request.user.is_authenticated:
        data = {}
        username = User.objects.get(username=request.user.username)
        profile = Patient.objects.filter(user=username)[0]
        if request.method == 'POST':
            form_general = ProfileUpdateForm(request.POST, instance=request.user)
            form_passwd = PasswordUpdateForm(request.user, request.POST)
            if 'old_password' in request.POST:
                if form_passwd.is_valid():
                    user = form_passwd.save()
                    update_session_auth_hash(request, user)
                    user.patient = request.user
                    profile = Patient.objects.get(user_id=user.patient.id)
                    user.save()
                    user.refresh_from_db()
                    data['form_general'] = prefillProfileForm(profile)
                    data['form_passwd'] = form_passwd
                    data['success'] = 'Password alterada com sucesso!'
                    return render(request, 'profile.html', data)
                else:
                    data['invalid'] = 'Erro na alteração da palavra-passe! Por favor, verifique.'
                    data['form_general'] = prefillProfileForm(profile)
                    data['form_passwd'] = form_passwd
            else:
                if form_general.is_valid():
                    new_data = form_general.save()
                    
                    new_data.patient = request.user
                    profile = Patient.objects.get(user_id=new_data.patient.id)
                    
                    new_data.save()
                    new_data.refresh_from_db()
                    data['form_general'] = prefillProfileForm(profile)
                    data['form_passwd'] = form_passwd
                    data['success'] = 'Informações gerais alteradas com sucesso!'
                    return render(request, 'profile.html', data)
                else:
                    data['invalid'] = 'Erro na alteração dos dados! Por favor, verifique.'
                    data['form_general'] = prefillProfileForm(profile)
                    data['form_passwd'] = form_passwd
        else:
            form = prefillProfileForm(profile)
            data['form_general'] = form
            data['form_passwd'] = PasswordChangeForm(request.user)
        return render(request, 'profile.html', data)
    else:
        return redirect('login')