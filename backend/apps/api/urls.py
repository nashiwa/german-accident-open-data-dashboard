from django.urls import path

from . import views


urlpatterns = [
    path("regions/", views.regions, name="api-regions"),
    path("regions/<str:ags>/", views.region_detail, name="api-region-detail"),
    path("accidents/", views.accidents, name="api-accidents"),
    path("aggregates/accidents/", views.aggregate_accidents, name="api-aggregate-accidents"),
    path("aggregates/rates/", views.aggregate_rates, name="api-aggregate-rates"),
    path("bonus/accident-points/", views.bonus_accident_points, name="api-bonus-accident-points"),
    path("bonus/zero-accident-municipalities/", views.bonus_zero_accident_municipalities, name="api-bonus-zero-accident-municipalities"),
    path("metadata/sources/", views.sources, name="api-sources"),
    path("import-runs/", views.import_runs, name="api-import-runs"),
    path("questions/mandatory/", views.mandatory_questions, name="api-mandatory-questions"),
    path("questions/earliest-accident-year/", views.question_earliest_accident_year, name="api-question-earliest-accident-year"),
    path("questions/saxony-accidents-2023/", views.question_saxony_accidents_2023, name="api-question-saxony-accidents-2023"),
    path("questions/nrw-earliest-year/", views.question_nrw_earliest_year, name="api-question-nrw-earliest-year"),
    path(
        "questions/mecklenburg-vorpommern-earliest-year/",
        views.question_mecklenburg_vorpommern_earliest_year,
        name="api-question-mecklenburg-vorpommern-earliest-year",
    ),
    path(
        "questions/berlin-pedestrian-accidents-2023/",
        views.question_berlin_pedestrian_accidents_2023,
        name="api-question-berlin-pedestrian-accidents-2023",
    ),
    path("questions/top-districts-by-accident-rate/", views.question_top_districts_by_accident_rate, name="api-question-top-districts-by-accident-rate"),
]
