# -*- coding: utf-8 -*-
"""
Views related to operations on course objects
"""
import json
import random
import string  # pylint: disable=W0402
import re

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django_future.csrf import ensure_csrf_cookie
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponseNotFound, Http404
from util.json_request import JsonResponse
from edxmako.shortcuts import render_to_response

from xmodule.error_module import ErrorDescriptor
from xmodule.modulestore.django import modulestore, loc_mapper
from xmodule.contentstore.content import StaticContent

from xmodule.modulestore.exceptions import (
    ItemNotFoundError, InvalidLocationError)
from xmodule.modulestore import Location
from xmodule.fields import Date

from contentstore.course_info_model import get_course_updates, update_course_updates, delete_course_update
from contentstore.utils import (
    get_lms_link_for_item, add_extra_panel_tab, remove_extra_panel_tab,
    get_modulestore)
from models.settings.course_details import CourseDetails, CourseSettingsEncoder

from models.settings.course_grading import CourseGradingModel
from models.settings.course_metadata import CourseMetadata
from util.json_request import expect_json

from .access import has_course_access
from .tabs import initialize_course_tabs
from .component import (
    OPEN_ENDED_COMPONENT_TYPES, NOTE_COMPONENT_TYPES,
    ADVANCED_COMPONENT_POLICY_KEY)

from django_comment_common.models import assign_default_role
from django_comment_common.utils import seed_permissions_roles

from student.models import CourseEnrollment

from xmodule.html_module import AboutDescriptor
from xmodule.modulestore.locator import BlockUsageLocator, CourseLocator
from course_creators.views import get_course_creator_status, add_user_with_status_unrequested
from contentstore import utils
from student.roles import CourseInstructorRole, CourseStaffRole
from student import auth

from courseware import grades

__all__ = ['students_course_learn_info', 'student_process']


USER_FEATURES = ('id', 'username', 'first_name', 'last_name', 'is_staff', 'email')
PROFILE_FEATURES = ('name', 'language', 'location', 'year_of_birth', 'gender',
                    'level_of_education', 'mailing_address', 'goals')

STUDENT_FEATURES = ['id', 'username', 'name', 'email', 'gender', 'level_of_education']

GENDER_CONTRAST = [
    ['m', '男'],
    ['f', '女'],
    ['o', '其他']
]

EDU_LEVEL_CONTRAST = [
    ['p', '博士'],
    ['m', '硕士'],
    ['b', '学士'],
    ['a', '大专'],
    ['hs','中专/高中'],
    ['jhs', '初中'],
    ['el', '小学'],
    ['none', '没有'],
    ['other', '其它']
]

settings.FEATURES['DISABLE_START_DATES'] = False
settings.XQUEUE_WAITTIME_BETWEEN_REQUESTS = 5

def _get_locator_and_course(package_id, branch, version_guid, block_id, user, depth=0):
    """
    Internal method used to calculate and return the locator and course module
    for the view functions in this file.
    """
    locator = BlockUsageLocator(package_id=package_id, branch=branch, version_guid=version_guid, block_id=block_id)
    if not has_course_access(user, locator):
        raise PermissionDenied()
    course_location = loc_mapper().translate_locator_to_location(locator)
    course_module = modulestore().get_item(course_location, depth=depth)
    return locator, course_module


@login_required
def students_course_learn_info(request, course_id):
    try:
        __, course = _get_locator_and_course(
            course_id, 'draft', None, course_id.split('.')[-1], request.user, depth=None
        )
    except:
        raise Http404('没有找到对应课程！')

    def format_user_data(user):
        try:
            grade = grades.grade(user, request, course)['percent'] * 100
        except:
            grade = 0.0


        student_dict = dict((ft, getattr(user, ft)) for ft in [sf for sf in STUDENT_FEATURES if sf in USER_FEATURES])

        student_profile = user.profile
        if student_profile:
            student_dict.update(dict((tf, getattr(student_profile, tf)) for tf in [pf for pf in STUDENT_FEATURES if pf in PROFILE_FEATURES]))

        if student_dict['gender']:
            st_g = student_dict['gender']
            student_dict['gender'] = filter(lambda x: x[0] == st_g, GENDER_CONTRAST)[0][1]

        if student_dict['level_of_education']:
            st_level = student_dict['level_of_education'] 
            student_dict['level_of_education'] = filter(lambda x: x[0] == st_level, EDU_LEVEL_CONTRAST)[0][1]

        student_dict.update({'complete_degree': "{grade}%".format(grade=grade)})

        return student_dict

    def get_uniq_email(course_users):
        return [ex for ex in course_users.values_list('email', flat=True)]

    course_instructors = CourseInstructorRole(course.location).users_with_role()

    course_staffs = CourseStaffRole(course.location).users_with_role()

    exclude_list = list(set(sum(map(get_uniq_email, [course_instructors, course_staffs]), [])))

    all_data = User.objects.filter(
                    courseenrollment__course_id=course_id.replace('.', '/'),
                    courseenrollment__is_active=1,
               ).order_by('username').select_related('profile')

    students = [format_user_data(st) for st in all_data if st.email not in exclude_list]

    return render_to_response("students_static.html", {'student_data': students, "context_course": course})


@login_required
def student_process(request, course_id, user_id):
    try:
        __, course = _get_locator_and_course(
            course_id, 'draft', None, course_id.split('.')[-1], request.user, depth=None
        )
    except:
        raise Http404('没有找到对应课程！')

    student = User.objects.prefetch_related("groups").get(id=user_id)

    courseware_summary = grades.progress_summary(student, request, course)
    grade_summary = grade.grade(student, request, course)

    if courseware_summary is None:
        raise Http404

    context = {
        'course': course,
        'courseware_summary': courseware_summary,
        'grade_summary': grade_summary,
        'student': student,
    }

    return JsonResponse(context)








