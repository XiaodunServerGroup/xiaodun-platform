"""
Views related to operations on course objects
"""
import json
import random
import string  # pylint: disable=W0402
import re
import bson
import time

from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django_future.csrf import ensure_csrf_cookie
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from util.json_request import JsonResponse
from edxmako.shortcuts import render_to_response

from xmodule.error_module import ErrorDescriptor
from xmodule.modulestore.django import modulestore, loc_mapper
from xmodule.contentstore.content import StaticContent

from xmodule.modulestore.exceptions import (
    ItemNotFoundError, InvalidLocationError, InsufficientSpecificationError)
from xmodule.modulestore import Location

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

from django_comment_common.utils import seed_permissions_roles

from student.models import CourseEnrollment

from xmodule.html_module import AboutDescriptor
from xmodule.modulestore.locator import BlockUsageLocator, CourseLocator
from course_creators.views import get_course_creator_status, add_user_with_status_unrequested
from contentstore import utils
from django.views.decorators.csrf import csrf_exempt
from student.roles import CourseInstructorRole, CourseStaffRole, CourseCreatorRole, GlobalStaff
from student import auth

#from microsite_configuration.middleware import MicrositeConfiguration

# from .course import _get_locator_and_course

def _get_locator_and_course(package_id, branch, version_guid, block_id, depth=0):
    locator = BlockUsageLocator(package_id=package_id, branch=branch, version_guid=version_guid, block_id=block_id)
    course_location = loc_mapper().translate_locator_to_location(locator)
    course_module = modulestore().get_item(course_location, depth=depth)
    return locator, course_module


# def fall_version(request):
#     return JsonResponse({"ver": time.time()})
#
# @csrf_exempt
# def fall_course_list(request):
#     # return JsonResponse(get_course_list(request))
#     if "application/json" in request.META.get('HTTP_ACCEPT', 'application/json'):
#         print("--------------------------------------------------------------------------------------------")
#         return JsonResponse(get_course_list(request))
#     else:
#         return HttpResponseBadRequest()
#
#
# def hot_version(request):
#     if "application/json" in request.META.get('HTTP_ACCEPT', 'application/json') and request.method == 'GET':
#         return JsonResponse({"ver": time.time()})
#     else:
#         return HttpResponseBadRequest()
#
#
# def hot_course_list(request):
#     if "application/json" in request.META.get('HTTP_ACCEPT', 'application/json') and request.method == 'POST':
#         return JsonResponse(get_course_list(request))
#     else:
#         return HttpResponseBadRequest()
#
#
# def all_version(request):
#     if "application/json" in request.META.get('HTTP_ACCEPT', 'application/json') and request.method == 'GET':
#         return JsonResponse({"ver": time.time()})
#     else:
#         return HttpResponseBadRequest()
#
#
# def all_course_list(request):
#     if "application/json" in request.META.get('HTTP_ACCEPT', 'application/json') and request.method == 'POST':
#         return JsonResponse(get_course_list(request))
#     else:
#         return HttpResponseBadRequest()
#
#
# def my_version(request):
#     if "application/json" in request.META.get('HTTP_ACCEPT', 'application/json') and request.method == 'GET':
#         return JsonResponse({"ver": time.time()})
#     else:
#         return HttpResponseBadRequest()
#
#
# def my_course_list(request):
#     if "application/json" in request.META.get('HTTP_ACCEPT', 'application/json') and request.method == 'POST':
#         return JsonResponse(get_course_list(request))
#     else:
#         return HttpResponseBadRequest()
#
#
# def latest_version(request):
#     if "application/json" in request.META.get('HTTP_ACCEPT', 'application/json') and request.method == 'GET':
#         return JsonResponse({"ver": time.time()})
#     else:
#         return HttpResponseBadRequest()
#
#
# def latest_course_list(request):
#     if "application/json" in request.META.get('HTTP_ACCEPT', 'application/json') and request.method == 'POST':
#         return JsonResponse(get_course_list(request))
#     else:
#         return HttpResponseBadRequest()

#
# def get_course_list(request):
#     courses = modulestore('direct').get_courses()
#
#     def format_course(course):
#         location = course.location
#         course_id = '.'.join([location.org, location.course, location.name])
#         locator, course_module = _get_locator_and_course(course_id, 'draft', None, location.name)
#         img_url = request.get_host() + utils.course_image_url(course_module)
#         pack_course = {
#             "id": course_id,
#             "imgid": ("-".join([course_id, course.course_image.encode("utf-8").split('.')[0]])),
#             "name": course.display_name,
#             "course_number": course.location.course,
#             "org": course.location.org,
#             "imgurl": img_url.encode("utf-8"),
#             "price": 0,
#             "progress": 20,
#         }
#         return pack_course
#
#     return [format_course(c) for c in courses if not isinstance(c, ErrorDescriptor)]

@csrf_exempt
def mobi_course_handler(request, datatype=None):
    if "application/json" in request.META.get('HTTP_ACCEPT', 'application/json'):
        if request.method == "POST" and request.get_full_path().split("/")[-1] != 'version':
            return mobi_course_data(request, datatype)
        elif request.method == "GET":
            return data_version_detection(request)
        else:
            return JsonResponse(status=404)
    else:
        return JsonResponse(status=404)


def data_version_detection(request):
    action = request.get_full_path().split('/').pop()

    if action == "version":
        return JsonResponse({"ver": time.time()})
    else:
        return JsonResponse({"errcode": 20001, "errmsg": "data error"})


def mobi_course_data(request, datatype):
    if datatype in ["homefalls", "hot", "latest", "all", "my"]:
        if "ver" not in request.POST:
            return JsonResponse({"errcode": 20000, "errmsg": 'param error'})
        else:
            # will fetch course list depend on version, developing
            version = request.POST['ver']

            courses = modulestore('direct').get_courses()

            def course_filter(course):
                """
                filter courses which don't meet the conditions
                """
                common_filter_boolean = (course.location.course != 'templates'
                                         and course.location.org != ''
                                         and course.location.course != ''
                                         and course.location.name != '')

                # if datatype == "my":
                #     return (has_course_access(request.user, course.location)
                #             and common_filter_boolean)
                # else:
                #     return common_filter_boolean

                return common_filter_boolean

            courses = filter(course_filter, courses)

            def format_course_info_for_json(course):
                """
                format data so as to return json
                """
                location = course.location
                course_id = '.'.join([location.org, location.course, location.name])
                locator, course_module = _get_locator_and_course(course_id, 'draft', None, location.name)
                img_url = request.get_host() + utils.course_image_url(course_module)
                pack_course = {
                    "id": course_id,
                    "imgid": ("-".join([course_id, course.course_image.encode("utf-8").split('.')[0]])),
                    "name": course.display_name,
                    "course_number": course.location.course,
                    "org": course.location.org,
                    "imgurl": img_url.encode("utf-8"),
                    "price": 0,
                    "progress": 20,
                }
                return pack_course

            infos_list = []
            for course in courses:
                if not isinstance(course, ErrorDescriptor):
                    try:
                        infos_list.append(format_course_info_for_json(course))
                    except:
                        continue

            return JsonResponse({datatype: infos_list})
    else:
        return JsonResponse({"errcode": 20001, "errmsg": "data error"})


def test_homefalls_list(request):
            print("--------------------------------------------------------")
            courses = modulestore('direct').get_courses()

            def course_filter(course):
                """
                filter courses which don't meet the conditions
                """
                common_filter_boolean = (course.location.course != 'templates'
                                         and course.location.org != ''
                                         and course.location.course != ''
                                         and course.location.name != '')

                # if datatype == "my":
                #     return (has_course_access(request.user, course.location)
                #             and common_filter_boolean)
                # else:
                #     return common_filter_boolean

                return common_filter_boolean

            courses = filter(course_filter, courses)
            print("*******************************************************")

            def format_course_info_for_json(course):
                """
                format data so as to return json
                """
                location = course.location
                course_id = '.'.join([location.org, location.course, location.name])
                print("===================")
                print(course.id)
                print(course_id)
                print("-----------------------------")
                locator, course_module = _get_locator_and_course(course_id, 'draft', None, location.name)
                print(">>>>>>>>>>>>>>>>>>>")
                img_url = request.get_host() + utils.course_image_url(course_module)
                pack_course = {
                    "id": course_id,
                    "imgid": ("-".join([course_id, course.course_image.encode("utf-8").split('.')[0]])),
                    "name": course.display_name,
                    "course_number": course.location.course,
                    "org": course.location.org,
                    "imgurl": img_url.encode("utf-8"),
                    "price": 0,
                    "progress": 20,
                }
                return pack_course

            infos_list = []
            for course in courses:
                if not isinstance(course, ErrorDescriptor):
                    try:
                        infos_list.append(format_course_info_for_json(course))
                    except:
                        continue

            return JsonResponse(infos_list)


@csrf_exempt
def mobi_search(request, keyword=None):
    if "application/json" not in request.META.get('HTTP_ACCEPT', 'application/json'):
        return HttpResponseNotFound()

    if request.method != 'POST':
        return HttpResponseNotFound()

    # we want realize the function that can identify machine uniquely, but now we just fetch data depending on 'ver'
    # in params

    def format_and_filter_key_for_json(course, keyword=None):
        """
        format data and filter with keywordso as to return json
        """
        if not keyword or (keyword not in course.org and keyword not in course.id and keyword not in course.display_name_with_default):
            return None
        try:
            location = course.location
            course_id = '.'.join([location.org, location.course, location.name])
            locator, course_module = _get_locator_and_course(course_id, 'draft', None, location.name)
            img_url = request.get_host() + utils.course_image_url(course_module)
            return {
                "id": course_id,
                "imgid": ("-".join([course_id, course.course_image.encode("utf-8").split('.')[0]])),
                "name": course.display_name,
                "course_number": course.location.course,
                "org": course.location.org,
                "imgurl": img_url.encode("utf-8"),
                "price": 0,
                "progress": 20,
            }
        except:
            return None

    courses = modulestore('direct').get_courses()

    info_list = []

    for course in courses:
        if not course.location:
            continue

        if not isinstance(course, ErrorDescriptor):
            filmat_course = format_and_filter_key_for_json(course, keyword)
            if not filmat_course:
                continue
            info_list.append(filmat_course)

    return JsonResponse({'search': info_list})


@csrf_exempt
def mobi_course_info_handler(request, course_id, action=None):
    # return mobi_course_action(request, course_id, action)
    # return mobi_course_info(request, course_id)
    if "application/json" not in request.META.get('HTTP_ACCEPT', 'application/json'):
        return HttpResponseNotFound()
    elif request.method == "GET":
        if action:
            return mobi_course_action(request, course_id, action)
        else:
            return mobi_course_info(request, course_id)
    else:
        return HttpResponseNotFound()


def mobi_course_action(request, course_id, action):
    if action not in ["structure", "updates", "handouts"]:
        return JsonResponse(status=404)

    try:
        if action != "structure":
            course_locator = BlockUsageLocator(package_id=course_id, branch='draft', version_guid=None, block_id=action)
            course_location = loc_mapper().translate_locator_to_location(course_locator)

            def get_course_info_by_action(location, action):
                """
                return data depend on action
                """
                if action == "updates":
                    return get_course_updates(location, None)
                elif action == "handouts":
                    module = get_modulestore(location).get_item(location)
                    return {"data": getattr(module, 'data', '')}
                else:
                    return {"error": 20000, "errmsg": "some error occur!"}

            if not course_location:
                return JsonResponse([])
            else:
                return JsonResponse(get_course_info_by_action(course_location, action))
        else:
            return JsonResponse(_course_json(request, course_id))
    except:
        return HttpResponseBadRequest("Fail to get data")


def mobi_course_sourse(request):
    """
    return request course source
    """
    return JsonResponse({})


def test_mobi_course_action(request, course_id, action):
    if action not in ["structure", "updates", "handouts"]:
        return JsonResponse(status=404)

    if action != "structure":
        course_locator = BlockUsageLocator(package_id=course_id, branch='draft', version_guid=None, block_id=action)
        course_location = loc_mapper().translate_locator_to_location(course_locator)

        def get_course_info_by_action(location, action):
            """
            return data depend on action
            """
            if action == "updates":
                return get_course_updates(location, None)
            elif action == "handouts":
                module = get_modulestore(location).get_item(location)
                return {"data": getattr(module, 'data', '')}
            else:
                return {"error": 20000, "errmsg": "some error occur!"}

        return JsonResponse(get_course_info_by_action(course_location, action))
    else:
        return JsonResponse(_course_json(request, course_id))


@csrf_exempt
def mobi_notice(request):
    if "application/json" not in request.META.get('HTTP_ACCEPT', 'application/json'):
        return HttpResponseBadRequest("Only support json requests")

    if "course_id" not in request.POST:
        return JsonResponse({"errcode": 20000, "errmsg": "params error"})
    try:
        course_locator = BlockUsageLocator(package_id=request.POST["course_id"], branch='draft', version_guid=None, block_id='updates')
        location = loc_mapper().translate_locator_to_location(course_locator)
        return JsonResponse(get_course_updates(location, None))
    except:
        return HttpResponseBadRequest("Fail to get data")


@csrf_exempt
def mobi_handouts(request):
    if "application/json" not in request.META.get('HTTP_ACCEPT', 'application/json'):
        return HttpResponseBadRequest("Only support json requests")

    if "course_id" not in request.POST:
        return JsonResponse({"errcode": 20000, "errmsg": "params error"})

    try:
        course_locator = BlockUsageLocator(package_id=request.POST["course_id"], branch='draft', version_guid=None, block_id="handouts")
        location = loc_mapper().translate_locator_to_location(course_locator)
        module = get_modulestore(location).get_item(location)

        return JsonResponse({
            "id": unicode(course_locator),
            "data": getattr(module, 'data', '')
        })
    except:
        return HttpResponseBadRequest("Fail to get handouts data")


def mobi_course_info(request, course_id=None):
    if request.method != "GET":
        return HttpResponseBadRequest("Only support GET request for this restful api")
    else:
        try:
            locator, course_module = _get_locator_and_course(package_id=course_id, branch='draft', version_guid=None, block_id=course_id.split(".")[-1])
        except InsufficientSpecificationError:
            return JsonResponse({"error": 20000, "errormsg": "unable get the course with id" + course_id})

        location = loc_mapper().translate_locator_to_location(locator)
        course = modulestore('direct').get_item(location)

        return JsonResponse({
            "name": course.display_name,
            "logo": request.get_host() + utils.course_image_url(course_module),
            "org": course.location.org,
            "code": location.course,
            "startdate": location.name,
            "peried": 0,
            "price": 0,
            "about": "--",
            "category": course.category
        })


def mobi_course_structure(request, course_id=None):
    return JsonResponse(_course_json(request, course_id))
    # response_format = request.REQUEST.get('format', 'html')
    # if response_format == 'json' or 'application/json' in request.META.get('HTTP_ACCEPT', 'application/json'):
    #     if request.method == "GET":
    #         return JsonResponse(_course_json(request, course_id))
    #     else:
    #         return HttpResponseBadRequest(status=404)
    # else:
    #     return HttpResponseBadRequest(status=404)


def _course_json(request, course_id):
    """
    Return a Json overview of a course
    """
    __, course = _get_locator_and_course(course_id, 'draft', None, course_id.split('.')[-1], depth=None)

    return _xmodule_json(course, course.location.course_id)


def _xmodule_json(xmodule, course_id):
    """
    Return a Json overview if an Xmodule
    """
    locator = loc_mapper().translate_location(
        course_id, xmodule.location, published=False, add_entry_if_missing=True
    )
    is_container = xmodule.has_children

    result = {
        'display_name': xmodule.display_name,
        'id': unicode(locator),
        'category': xmodule.category,
        'is_draft': getattr(xmodule, 'is_draft', False),
        'is_container': is_container,
    }
    if is_container:
        result['children'] = [_xmodule_json(child, course_id) for child in xmodule.get_children()]
    return result
