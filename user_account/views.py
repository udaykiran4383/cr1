from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db import models
import json
import os

from .models import Task, Student, CollegeLeaderboard, IndividualLeaderboard, College


def points(request): 
    return render(request, 'myapp/points.html')


def success_view(request):
    colleges = College.objects.all()
    teams = []

    for college in colleges:
        students = Student.objects.filter(college=college)
        if students.exists():
            teams.append({
                'college': college.name,
                'state': college.state,
                'district': college.district,
                'students': students
            })

    return render(request, 'success.html', {'teams': teams})


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        state = request.POST.get('state')
        district = request.POST.get('district')
        college_name = request.POST.get('college')

        if college_name == 'other':
            new_college_name = request.POST.get('new_college')
            college, created = get_or_create_college(new_college_name, state, district)
            if created:
                add_college_to_json(state, district, new_college_name)
        else:
            try:
                college = College.objects.get(name=college_name, district=district, state=state)
            except College.DoesNotExist:
                return render(request, 'myapp/points.html', {'error': 'College not found. Please enter a new college.'})

        phone = request.POST.get('phone')
        years = request.POST.get('years')
        gender = request.POST.get('gender')
        stream = request.POST.get('stream')
        year_of_study = request.POST.get('year_of_study')

        Student.objects.create(
            name=name,
            state=state,
            district=district,
            college=college,
            phone=phone,
            years=years,
            gender=gender,
            stream=stream,
            year_of_study=year_of_study
        )
        return redirect('tasks_view')

    return render(request, 'myapp/points.html')


def get_or_create_college(name, state, district):
    college, created = College.objects.get_or_create(name=name, district=district, state=state)
    return college, created


def add_college_to_json(state, district, new_college_name):
    file_path = os.path.join(settings.BASE_DIR, 'user_account', 'static', 'states_districts.json')

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {'states': []}

    state_found = False
    for state_obj in data['states']:
        if state_obj['state'] == state:
            state_found = True
            district_found = False
            for district_obj in state_obj['districts']:
                if district_obj['name'] == district:
                    district_found = True
                    if 'colleges' not in district_obj:
                        district_obj['colleges'] = []
                    if new_college_name not in district_obj['colleges']:
                        district_obj['colleges'].append(new_college_name)
                    break
            if not district_found:
                state_obj['districts'].append({
                    'name': district,
                    'colleges': [new_college_name]
                })
            break

    if not state_found:
        data['states'].append({
            'state': state,
            'districts': [{
                'name': district,
                'colleges': [new_college_name]
            }]
        })

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def add_college(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            state = data['state']
            district = data['district']
            new_college = data['new_college']

            file_path = os.path.join(settings.BASE_DIR, 'user_account', 'static', 'states_districts.json')
            try:
                with open(file_path, 'r') as file:
                    json_data = json.load(file)
            except FileNotFoundError:
                json_data = {'states': []}

            state_obj = next((s for s in json_data['states'] if s['state'] == state), None)
            if state_obj:
                district_obj = next((d for d in state_obj['districts'] if d['name'] == district), None)
                if district_obj:
                    if 'colleges' not in district_obj:
                        district_obj['colleges'] = []
                    if new_college not in district_obj['colleges']:
                        district_obj['colleges'].append(new_college)
                else:
                    state_obj['districts'].append({
                        'name': district,
                        'colleges': [new_college]
                    })
            else:
                json_data['states'].append({
                    'state': state,
                    'districts': [{
                        'name': district,
                        'colleges': [new_college]
                    }]
                })

            with open(file_path, 'w') as file:
                json.dump(json_data, file, indent=4)

            return JsonResponse({'status': 'success', 'message': f"College '{new_college}' added successfully to {state}, {district}"}, status=200)

        except Exception as e:
            print(f"Error occurred: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def tasks_view(request):
    tasks = Task.objects.all()
    if request.method == 'POST':
        points = 0
        for task in tasks:
            selected_option = request.POST.get(f'task_{task.id}')
            if selected_option == task.correct_option:
                points += 100
            else:
                points += 20

        student = request.user.student
        student.points += points
        student.save()

        # Update individual leaderboard
        individual_leaderboard, created = IndividualLeaderboard.objects.get_or_create(student=student)
        individual_leaderboard.points = student.points
        individual_leaderboard.save()

        # Update college leaderboard
        college_leaderboard, created = CollegeLeaderboard.objects.get_or_create(college=student.college)
        college_leaderboard.total_points = Student.objects.filter(college=student.college).aggregate(models.Sum('points'))['points__sum']
        college_leaderboard.save()

        return redirect('leaderboard_view')

    return render(request, 'myapp/tasks.html', {'tasks': tasks})


def leaderboard_view(request):
    college_leaderboard = CollegeLeaderboard.objects.all().order_by('-total_points')
    individual_leaderboard = IndividualLeaderboard.objects.all().order_by('-points')
    return render(request, 'leaderboard.html', {
        'college_leaderboard': college_leaderboard,
        'individual_leaderboard': individual_leaderboard
    })
