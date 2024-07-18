
# admin.py
from django.contrib import admin
from .models import Student, College, Team
from .models import Task, CollegeLeaderboard, IndividualLeaderboard

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'college')
    filter_horizontal = ('students',)

admin.site.register(Student)
admin.site.register(College)
admin.site.register(Team, TeamAdmin)


admin.site.register(Task)
admin.site.register(CollegeLeaderboard)
admin.site.register(IndividualLeaderboard)
