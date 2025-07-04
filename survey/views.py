from django.shortcuts import render, redirect, get_object_or_404
from .models import Survey, Question, Choice, Response, Answer
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.http import JsonResponse
import csv
from collections import OrderedDict
from django.urls import reverse
from django.http import HttpResponseRedirect
from tts.helpers import check_internet_connectivity
from djangoML.utils import ensure_active_subscription


@login_required
def create_survey(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        url = request.POST.get('url')
        logo = request.FILES.get('logo')
        if title:
            survey = Survey.objects.create(
                user=request.user,
                title=title,
                url=url,
                description=description,
                logo=logo
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Survey created successfully', 'survey_id': survey.id})
            else:
                return redirect('survey:survey_detail', survey.id)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Title is required.'}, status=400)
            else:
                messages.error(request, 'Title is required.')
    return render(request, 'survey/create_survey.html')


@login_required
def survey_list(request):
    surveys = request.user.survey_set.all().order_by('-created_at')
    return render(request, 'survey/survey_list.html', {'surveys': surveys})


@login_required
def update_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        url = request.POST.get('url')
        logo = request.FILES.get('logo')

        if not title:
            messages.error(request, "Title cannot be empty.")
        else:
            survey.title = title
            survey.description = description
            survey.url = url
            if logo:
                survey.logo = logo
            survey.save()
            messages.success(request, "Survey updated successfully.")
            return redirect('survey:survey_list')

    return render(request, 'survey/update_survey.html', {'survey': survey})


@login_required
def delete_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    if request.method == 'POST':
        survey.delete()
        messages.success(request, "Survey deleted successfully.")
        return redirect('survey:survey_list')
    return render(request, 'survey/delete_survey.html', {'survey': survey})

# @login_required
# def create_survey(request):
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         description = request.POST.get('description')
#         logo = request.FILES.get('logo')
#         if title:
#             survey = Survey.objects.create(
#                 user=request.user,
#                 title=title,
#                 description=description,
#                 logo=logo
#             )
#             return redirect('survey/survey_detail', survey.id)
#         else:
#             messages.error(request, 'Title is required.')
#     return render(request, 'survey/create_survey.html')

@login_required
def add_question(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        is_required = request.POST.get('is_required') == 'on'
        if question_text and question_type:
            question = Question.objects.create(
                survey=survey,
                question_text=question_text,
                question_type=question_type,
                is_required=is_required
            )
            if question_type in ['radio', 'checkbox']:
                # Redirect to add choices
                return redirect('survey:add_choices', question.id)
            else:
                return redirect('survey_detail', survey.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    return render(request, 'survey/add_question.html', {'survey': survey})


@login_required
def question_list(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    questions = survey.question_set.all()
    return render(request, 'survey/question_list.html', {'survey': survey, 'questions': questions})


@login_required
def update_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, survey__user=request.user)
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        is_required = request.POST.get('is_required') == 'on'

        if not question_text or not question_type:
            messages.error(request, 'Please fill all fields.')
        else:
            question.question_text = question_text
            question.question_type = question_type
            question.is_required = is_required
            question.save()
            messages.success(request, 'Question updated successfully.')
            if question_type in ['radio', 'checkbox']:
                # Redirect to add choices
                return redirect('survey:add_choices', question.id)
            else:
                return redirect('survey_detail', question.survey.id)
            # return redirect('survey:question_list', survey_id=question.survey.id)

    return render(request, 'survey/update_question.html', {'question': question})


@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, survey__user=request.user)
    if request.method == 'POST':
        survey_id = question.survey.id
        question.delete()
        messages.success(request, 'Question deleted successfully.')
        return redirect('survey:question_list', survey_id=survey_id)
    return render(request, 'survey/delete_question.html', {'question': question})

@login_required
def add_choices(request, question_id):
    question = get_object_or_404(Question, id=question_id, survey__user=request.user)
    if request.method == 'POST':
        choice_text = request.POST.get('choice_text')
        if choice_text:
            Choice.objects.create(question=question, choice_text=choice_text)
        # Stay on the same page to add more choices
    choices = question.choice_set.all()
    return render(request, 'survey/add_choices.html', {'question': question, 'choices': choices})


@login_required
def delete_choice(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id)

    # Optional: Ensure only owner of the survey can delete
    if choice.question.survey.user != request.user:
        messages.error(request, "You do not have permission to delete this choice.")
        return redirect('survey:survey_detail', survey_id=choice.question.survey.id)

    if request.method == 'POST':
        survey_id = choice.question.survey.id
        choice.delete()
        messages.success(request, "Choice deleted successfully.")
        return redirect('survey:add_choices', question_id=choice.question.id)

    # If GET request, show confirmation page or redirect back
    return redirect('survey:add_choices', question_id=choice.question.id)



@login_required
def update_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    if request.method == 'POST':
        survey.title = request.POST.get('title')
        survey.description = request.POST.get('description')
        survey.url = request.POST.get('url')
        logo = request.FILES.get('logo')
        if logo:
            survey.logo = logo
        survey.save()
        print("logo", survey.logo)
        # return redirect('survey/survey_detail', survey.id)
        return redirect('survey:survey_list')
    return render(request, 'survey/update_survey.html', {'survey': survey})

@login_required
def delete_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    if request.method == 'POST':
        survey.delete()
        return redirect('survey:survey_list')
    return render(request, 'survey/delete_survey.html', {'survey': survey})

def survey_detail(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    questions = survey.question_set.all()
    return render(request, 'survey/survey_detail.html', {'survey': survey, 'questions': questions})

def submit_response(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    surveys = Survey.objects.filter(user=request.user).order_by('-created_at')
    questions = list(survey.question_set.all().order_by('id'))
    question_index = int(request.GET.get('q', 0))

    if question_index >= len(questions):
        return redirect('survey:thank_you')

    question = questions[question_index]

    if request.method == 'POST':
        response_id = request.session.get('response_id')
        if not response_id:
            response = Response.objects.create(
                survey=survey,
                user=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            request.session['response_id'] = response.id
        else:
            response = get_object_or_404(Response, id=response_id)

        answer_value = request.POST.get(str(question.id))
        if question.question_type == 'text':
            Answer.objects.create(response=response, question=question, text_answer=answer_value)
        elif question.question_type == 'radio':
            Answer.objects.create(response=response, question=question, selected_choice_id=answer_value)
        elif question.question_type == 'checkbox':
            for choice_id in request.POST.getlist(str(question.id)):
                Answer.objects.create(response=response, question=question, selected_choice_id=choice_id)

        # return redirect(f'?q={question_index + 1}')
        next_index = question_index + 1
        next_url = reverse('survey:submit_response', args=[survey_id]) + f'?q={next_index}'
        return HttpResponseRedirect(next_url)

    return render(request, 'survey/single_question.html', {
        'survey': survey,
        'surveys': surveys,
        'question': question,
        'index': question_index,
        'total': len(questions),
    })



# def take_survey(request, slug):
#     survey = get_object_or_404(Survey, slug=slug)
#     survey_id = survey.id
#     surveys = Survey.objects.filter(slug=slug).order_by('-created_at')
#     questions = list(survey.question_set.all().order_by('id'))
#     question_index = int(request.GET.get('q', 0))
#     email = request.POST.get('title')

#     if question_index >= len(questions):
#         return redirect('survey:thank_you_slug')

#     question = questions[question_index]
#     # Response.objects.all().delete()
#     if request.method == 'POST':
#         response_id = request.session.get('response_id')
#         if not response_id:
#             response = Response.objects.create(
#                 survey=survey,
#                 email=email,
#                 ip_address=request.META.get('REMOTE_ADDR')
#             )
#             request.session['response_id'] = response.id
#         else:
#             response = get_object_or_404(Response, id=response_id)

#         answer_value = request.POST.get(str(question.id))
#         if question.question_type == 'text':
#             Answer.objects.create(response=response, question=question, text_answer=answer_value)
#         elif question.question_type == 'radio':
#             Answer.objects.create(response=response, question=question, selected_choice_id=answer_value)
#         elif question.question_type == 'checkbox':
#             for choice_id in request.POST.getlist(str(question.id)):
#                 Answer.objects.create(response=response, question=question, selected_choice_id=choice_id)

#         # Redirect to the next question
#         next_index = question_index + 1
#         next_url = reverse('survey:take_survey', args=[survey.slug]) + f'?q={next_index}'
#         return HttpResponseRedirect(next_url)

#     return render(request, 'survey/take_survey.html', {
#         'survey': survey,
#         'surveys': surveys,
#         'question': question,
#         'index': question_index,
#         'total': len(questions),
#     })



def take_survey(request, slug):
    survey = get_object_or_404(Survey, slug=slug)
    surveys = Survey.objects.filter(slug=slug).order_by('-created_at')
    questions = list(survey.question_set.all().order_by('id'))
    question_index = int(request.GET.get('q', 0))
    start_survey = True


    if not check_internet_connectivity():
        return render(request, 'survey/start_survey.html', {
            'message': 'Please check your network and try again.',
             'survey': survey,
             'start_survey': start_survey,
        })

    # if not request.user.is_authenticated:
    #     return render(request, 'survey/start_survey.html', {
    #         'message': 'Please <a href="/login" style="text-decoration: none; color: #0E8AB3;">login</a> and come back.',
    #          'survey': survey,
    #          'start_survey': start_survey,
    #     })
    
    
    # if ensure_active_subscription(request.user):
    #     start_survey = True
    # else:
    #         return render(request, 'survey/start_survey.html', {
    #             'message': 'Please contact site admin to subscribe and continue using survey.',
    #             'survey': survey,
    #             'start_survey': start_survey,
    #         })

    # Show thank you if done
    if question_index >= len(questions):
        return redirect('survey:thank_you_slug')

    # First visit – ask for email and phone
    if question_index == 0 and request.method != 'POST':
        return render(request, 'survey/start_survey.html', {
            'survey': survey,
            'start_survey': start_survey,
        })

    # Get the current question
    question = questions[question_index]

    if request.method == 'POST':
        # First POST: collect email & phone
        if question_index == 0:
            email = request.POST.get('email')
            # phone = request.POST.get('phone')
            response = Response.objects.create(
                survey=survey,
                email=email,
                # phone=phone,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            request.session['response_id'] = response.id
            return HttpResponseRedirect(reverse('survey:take_survey', args=[survey.slug]) + '?q=1')

        # Ongoing questions
        response_id = request.session.get('response_id')
        if not response_id:
            return redirect('survey:take_survey', slug=slug)  # fallback to start

        response = get_object_or_404(Response, id=response_id)
        answer_value = request.POST.get(str(question.id))

        if question.question_type == 'text':
            Answer.objects.create(response=response, question=question, text_answer=answer_value)
        elif question.question_type == 'radio':
            Answer.objects.create(response=response, question=question, selected_choice_id=answer_value)
        elif question.question_type == 'checkbox':
            for choice_id in request.POST.getlist(str(question.id)):
                Answer.objects.create(response=response, question=question, selected_choice_id=choice_id)

        # Go to next question
        next_index = question_index + 1
        next_url = reverse('survey:take_survey', args=[survey.slug]) + f'?q={next_index}'
        return HttpResponseRedirect(next_url)

    return render(request, 'survey/take_survey.html', {
        'survey': survey,
        'surveys': surveys,
        'question': question,
        'index': question_index,
        'total': len(questions),
    })


def thank_you_slug(request):
    response_id = request.session.get('response_id')
    response = get_object_or_404(Response, id=response_id)
    return render(request, 'survey/thank_you.html')


# @login_required
# def export_csv(request, survey_id):
#     survey = get_object_or_404(Survey, id=survey_id, user=request.user)
#     responses = Response.objects.filter(survey=survey)
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename=\"survey_{survey.id}_responses.csv\"'
#     writer = csv.writer(response)
#     writer.writerow(['User', 'IP Address', 'Submission Date'])
#     for r in responses:
#         writer.writerow([str(r.user), r.ip_address, r.submitted_at])
#     return response


from collections import OrderedDict
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import csv

@login_required
def export_csv(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    questions = list(survey.question_set.all())
    responses = Response.objects.filter(survey=survey).prefetch_related('answer_set__question', 'answer_set__selected_choice').order_by('-submitted_at')

    latest_responses = OrderedDict()
    for resp in responses:
        key = resp.email or (resp.user.email if resp.user else resp.ip_address)
        if key and key not in latest_responses:
            latest_responses[key] = resp

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="survey_{survey.id}_latest_responses.csv"'
    writer = csv.writer(response)

    header = ['Email/User/IP', 'IP Address', 'Submitted At'] + [q.question_text for q in questions]
    writer.writerow(header)

    for resp in latest_responses.values():
        identifier = resp.email or (resp.user.email if resp.user else resp.ip_address)
        row = [
            identifier,
            resp.ip_address,
            resp.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        ]

        answers_map = {}
        for answer in resp.answer_set.all():
            qid = answer.question.id
            if answer.text_answer:
                answers_map[qid] = answer.text_answer
            elif answer.selected_choice:
                if qid in answers_map:
                    answers_map[qid] += f", {answer.selected_choice.choice_text}"
                else:
                    answers_map[qid] = answer.selected_choice.choice_text

        for q in questions:
            row.append(answers_map.get(q.id, ''))

        writer.writerow(row)

    return response


from collections import OrderedDict
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def survey_responses_table(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    questions = list(survey.question_set.all())

    # Base queryset
    responses_qs = Response.objects.filter(survey=survey).prefetch_related(
        'answer_set__question', 'answer_set__selected_choice'
    ).order_by('-submitted_at')

    # Filter by search query if given
    search_query = request.GET.get('q', '').strip()
    if search_query:
        responses_qs = responses_qs.filter(
            Q(email__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )

    # Get latest responses per user/email/ip
    latest_responses = OrderedDict()
    for resp in responses_qs:
        key = resp.email or (resp.user.email if resp.user else resp.ip_address)
        if key and key not in latest_responses:
            latest_responses[key] = resp

    # Build answers map for each response
    responses_data = []
    for resp in latest_responses.values():
        answers_map = {}
        for answer in resp.answer_set.all():
            qid = answer.question.id
            if answer.text_answer:
                answers_map[qid] = answer.text_answer
            elif answer.selected_choice:
                if qid in answers_map:
                    answers_map[qid] += f", {answer.selected_choice.choice_text}"
                else:
                    answers_map[qid] = answer.selected_choice.choice_text
        responses_data.append({
            'response': resp,
            'answers_map': answers_map,
        })

    context = {
        'survey': survey,
        'questions': questions,
        'responses_data': responses_data,
        'search_query': search_query,
    }
    return render(request, 'survey/responses_table.html', context)

def thank_you(request):
    request.session.pop('response_id', None)
    return render(request, 'survey/thank_you.html')



from collections import Counter

import json

@login_required
def survey_summary_charts(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    questions = survey.question_set.all()
    responses = Response.objects.filter(survey=survey).prefetch_related('answer_set__selected_choice')

    yes_no_counts = Counter()

    for response in responses:
        for answer in response.answer_set.all():
            choice_text = answer.selected_choice.choice_text.strip().lower() if answer.selected_choice else ''
            if choice_text in ['yes', 'no']:
                yes_no_counts[choice_text] += 1

    context = {
        'survey': survey,
        'yes_count': yes_no_counts['yes'],
        'no_count': yes_no_counts['no'],
    }
    return render(request, 'survey/survey_charts.html', context)
