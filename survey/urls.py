from django.urls import path
from  .views import create_survey, survey_detail, submit_response, export_csv,thank_you, add_question, add_choices, survey_list
from  .views import update_survey,delete_survey, question_list, update_question, survey_responses_table, delete_question, delete_choice, take_survey, thank_you_slug, survey_summary_charts
from django.conf import settings
from django.conf.urls.static import static

app_name = 'survey'  # THIS is critical

urlpatterns = [
    path('create-survey/', create_survey, name='create_survey'),
    path('survey/<int:survey_id>/summary-charts/', survey_summary_charts, name='survey_summary_charts'),
     path('survey/<int:survey_id>/responses/', survey_responses_table, name='survey_responses_table'),
    path('survey-list', survey_list, name='survey_list'),  # e.g. /survey/
    path('<int:survey_id>/update/', update_survey, name='update_survey'),
    path('<int:survey_id>/delete/', delete_survey, name='delete_survey'),
    path('<int:survey_id>/', survey_detail, name='survey_detail'),
    path('<int:survey_id>/submit/', submit_response, name='submit_response'),
    path('thank-you-borra-belt/', thank_you_slug, name='thank_you_slug'),
    path('<str:slug>/', take_survey, name='take_survey'),
    path('<int:survey_id>/export/', export_csv, name='export_csv'),
    path('<int:survey_id>/add_question/', add_question, name='add_question'),
    path('<int:survey_id>/questions/', question_list, name='question_list'),
    path('questions/<int:question_id>/update/', update_question, name='update_question'),
    path('questions/<int:question_id>/delete/', delete_question, name='delete_question'),
    path('question/<int:question_id>/add_choices/', add_choices, name='add_choices'),
    path('choice/<int:choice_id>/delete/', delete_choice, name='delete_choice'),
    path('thank-you/', thank_you, name='thank_you'),
    
]



if settings.DEBUG:  # This should only be True in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)