from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.accidents.models import Accident
from apps.api.serializers import AccidentSerializer, ImportRunSerializer, RegionSerializer, SourceSerializer
from apps.api.services.provenance import latest_successful_import_provenance
from apps.api.services.queries import (
    accident_count,
    accident_counts_by_region,
    accident_rates_by_population,
    earliest_accident_year,
    earliest_year_for_state,
    zero_accident_municipalities,
)
from apps.catalog.models import ImportRun, Source
from apps.regions.models import Region


def _parse_int(value, name):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _error(message, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({"detail": message}, status=http_status)


@extend_schema(
    operation_id="list_regions",
    parameters=[
        OpenApiParameter("level", OpenApiTypes.STR, description="Filter by state, district, or municipality."),
        OpenApiParameter("state", OpenApiTypes.STR, description="Filter by state code such as SN or BE."),
    ],
    responses=RegionSerializer(many=True),
)
@api_view(["GET"])
def regions(request):
    queryset = Region.objects.all().order_by("ags")
    level = request.query_params.get("level")
    state = request.query_params.get("state")
    if level:
        queryset = queryset.filter(level=level)
    if state:
        queryset = queryset.filter(state_code=state)
    return Response(RegionSerializer(queryset, many=True).data)


@extend_schema(operation_id="retrieve_region", responses=RegionSerializer)
@api_view(["GET"])
def region_detail(request, ags):
    try:
        region = Region.objects.get(ags=ags)
    except Region.DoesNotExist:
        return _error("Region not found", status.HTTP_404_NOT_FOUND)
    return Response(RegionSerializer(region).data)


@extend_schema(
    operation_id="list_accidents",
    parameters=[
        OpenApiParameter("year", OpenApiTypes.INT),
        OpenApiParameter("state", OpenApiTypes.STR),
        OpenApiParameter("category", OpenApiTypes.STR),
        OpenApiParameter("participant", OpenApiTypes.STR),
    ],
    responses=AccidentSerializer(many=True),
)
@api_view(["GET"])
def accidents(request):
    queryset = Accident.objects.select_related("state_region", "district_region", "municipality_region").order_by("id")
    try:
        year = _parse_int(request.query_params.get("year"), "year")
    except ValueError as exc:
        return _error(str(exc))
    state = request.query_params.get("state")
    participant = request.query_params.get("participant")
    category = request.query_params.get("category")
    if year is not None:
        queryset = queryset.filter(year=year)
    if state:
        queryset = queryset.filter(state_region__state_code=state)
    if category:
        queryset = queryset.filter(category=category)
    if participant:
        participant_fields = {
            "pedestrian": "is_pedestrian",
            "bicycle": "is_bicycle",
            "car": "is_car",
            "motorcycle": "is_motorcycle",
            "goods_vehicle": "is_goods_vehicle",
            "other": "is_other",
        }
        participant_field = participant_fields.get(participant)
        if participant_field is None:
            return _error(f"Unsupported participant filter: {participant}")
        queryset = queryset.filter(**{participant_field: True})
    return Response(AccidentSerializer(queryset[:100], many=True).data)


@extend_schema(
    operation_id="aggregate_accidents",
    parameters=[
        OpenApiParameter("year", OpenApiTypes.INT),
        OpenApiParameter("state", OpenApiTypes.STR),
        OpenApiParameter("level", OpenApiTypes.STR),
        OpenApiParameter("category", OpenApiTypes.STR),
        OpenApiParameter("participant", OpenApiTypes.STR),
    ],
    responses=OpenApiTypes.OBJECT,
)
@api_view(["GET"])
def aggregate_accidents(request):
    try:
        year = _parse_int(request.query_params.get("year"), "year")
        level = request.query_params.get("level")
        state = request.query_params.get("state")
        category = request.query_params.get("category")
        participant = request.query_params.get("participant")
        if level:
            if level not in Region.Level.values:
                return _error(f"Unsupported region level: {level}")
            if year is None:
                return _error("year is required when grouping by level")
            grouped = list(accident_counts_by_region(level=level, year=year, category=category, participant=participant))
            return Response({
                "results": grouped,
                "filters": {"level": level, "year": year, "category": category, "participant": participant},
                "provenance": latest_successful_import_provenance(),
            })
        count = accident_count(year=year, state_code=state, category=category, participant=participant)
    except ValueError as exc:
        return _error(str(exc))
    return Response({
        "accident_count": count,
        "filters": {"year": year, "state": state, "category": category, "participant": participant},
        "provenance": latest_successful_import_provenance(),
    })


@extend_schema(
    operation_id="aggregate_accident_rates",
    parameters=[
        OpenApiParameter("year", OpenApiTypes.INT, required=True),
        OpenApiParameter("level", OpenApiTypes.STR),
    ],
    responses=OpenApiTypes.OBJECT,
)
@api_view(["GET"])
def aggregate_rates(request):
    try:
        year = _parse_int(request.query_params.get("year"), "year")
    except ValueError as exc:
        return _error(str(exc))
    level = request.query_params.get("level", Region.Level.DISTRICT)
    if level not in Region.Level.values:
        return _error(f"Unsupported region level: {level}")
    if year is None:
        return _error("year is required")
    return Response({
        "results": accident_rates_by_population(level=level, year=year),
        "filters": {"level": level, "year": year, "denominator": "population"},
        "provenance": latest_successful_import_provenance(),
    })


@extend_schema(
    operation_id="bonus_zero_accident_municipalities",
    parameters=[
        OpenApiParameter("year", OpenApiTypes.INT, required=True),
        OpenApiParameter("state", OpenApiTypes.STR, required=True, description="State code such as SN, BE, or SH."),
    ],
    responses=RegionSerializer(many=True),
)
@api_view(["GET"])
def bonus_zero_accident_municipalities(request):
    try:
        year = _parse_int(request.query_params.get("year"), "year")
    except ValueError as exc:
        return _error(str(exc))
    state = request.query_params.get("state")
    if year is None:
        return _error("year is required")
    if not state:
        return _error("state is required")
    regions = zero_accident_municipalities(year=year, state_code=state)
    return Response(RegionSerializer(regions, many=True).data)


@extend_schema(
    operation_id="bonus_accident_points_preview",
    parameters=[
        OpenApiParameter("year", OpenApiTypes.INT),
        OpenApiParameter("state", OpenApiTypes.STR),
        OpenApiParameter("participant", OpenApiTypes.STR),
    ],
    responses=OpenApiTypes.OBJECT,
)
@api_view(["GET"])
def bonus_accident_points(request):
    try:
        year = _parse_int(request.query_params.get("year"), "year")
    except ValueError as exc:
        return _error(str(exc))
    state = request.query_params.get("state")
    participant = request.query_params.get("participant")
    queryset = Accident.objects.order_by("id")
    if year is not None:
        queryset = queryset.filter(year=year)
    if state:
        queryset = queryset.filter(state_region__state_code=state)
    if participant:
        participant_fields = {
            "pedestrian": "is_pedestrian",
            "bicycle": "is_bicycle",
            "car": "is_car",
            "motorcycle": "is_motorcycle",
        }
        participant_field = participant_fields.get(participant)
        if participant_field is None:
            return _error(f"Unsupported participant filter: {participant}")
        queryset = queryset.filter(**{participant_field: True})
    return Response({
        "results": [
            {
                "id": accident.source_event_id,
                "longitude": float(accident.longitude),
                "latitude": float(accident.latitude),
                "participant": (
                    "pedestrian" if accident.is_pedestrian else
                    "bicycle" if accident.is_bicycle else
                    "motorcycle" if accident.is_motorcycle else
                    "car" if accident.is_car else
                    "other"
                ),
            }
            for accident in queryset[:100]
        ],
        "filters": {"year": year, "state": state, "participant": participant},
    })


@extend_schema(operation_id="list_sources", responses=SourceSerializer(many=True))
@api_view(["GET"])
def sources(request):
    return Response(SourceSerializer(Source.objects.all().order_by("name"), many=True).data)


@extend_schema(operation_id="list_import_runs", responses=ImportRunSerializer(many=True))
@api_view(["GET"])
def import_runs(request):
    return Response(ImportRunSerializer(ImportRun.objects.select_related("source").order_by("-started_at")[:20], many=True).data)


def _question_response(question, answer, filters):
    return Response({
        "question": question,
        "answer": answer,
        "filters": filters,
        "provenance": latest_successful_import_provenance(),
    })


@extend_schema(operation_id="question_earliest_accident_year", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def question_earliest_accident_year(request):
    return _question_response(
        "What is the earliest accident year in the complete dataset?",
        {"earliest_year": earliest_accident_year()},
        {},
    )


@extend_schema(operation_id="question_saxony_accidents_2023", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def question_saxony_accidents_2023(request):
    return _question_response(
        "How many accidents involving personal injury occurred in Saxony in 2023?",
        {"region": "Sachsen", "state": "SN", "year": 2023, "accident_count": accident_count(year=2023, state_code="SN")},
        {"state": "SN", "year": 2023},
    )


@extend_schema(operation_id="question_nrw_earliest_year", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def question_nrw_earliest_year(request):
    return _question_response(
        "From which year onwards is data available for North Rhine-Westphalia?",
        {"region": "North Rhine-Westphalia", "state": "NW", "earliest_year": earliest_year_for_state("NW")},
        {"state": "NW"},
    )


@extend_schema(operation_id="question_mecklenburg_vorpommern_earliest_year", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def question_mecklenburg_vorpommern_earliest_year(request):
    return _question_response(
        "From which year onwards is data available for Mecklenburg-Western Pomerania?",
        {"region": "Mecklenburg-Western Pomerania", "state": "MV", "earliest_year": earliest_year_for_state("MV")},
        {"state": "MV"},
    )


@extend_schema(operation_id="question_berlin_pedestrian_accidents_2023", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def question_berlin_pedestrian_accidents_2023(request):
    return _question_response(
        "How many accidents involving pedestrians occurred in Berlin in 2023?",
        {
            "region": "Berlin",
            "state": "BE",
            "year": 2023,
            "participant": "pedestrian",
            "accident_count": accident_count(year=2023, state_code="BE", participant="pedestrian"),
        },
        {"state": "BE", "year": 2023, "participant": "pedestrian"},
    )


@extend_schema(operation_id="question_top_districts_by_accident_rate", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def question_top_districts_by_accident_rate(request):
    return _question_response(
        "Which districts have the highest accident rate per 100,000 inhabitants?",
        {"year": 2023, "results": accident_rates_by_population(level=Region.Level.DISTRICT, year=2023)},
        {"level": "district", "year": 2023, "denominator": "population"},
    )


@extend_schema(operation_id="mandatory_questions", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def mandatory_questions(request):
    return Response({
        "questions": {
            "earliest_accident_year": {
                "answer": {"earliest_year": earliest_accident_year()},
                "endpoint": "/api/questions/earliest-accident-year/",
            },
            "saxony_accidents_2023": {
                "answer": {"region": "Sachsen", "state": "SN", "year": 2023, "accident_count": accident_count(year=2023, state_code="SN")},
                "endpoint": "/api/questions/saxony-accidents-2023/",
            },
            "nrw_earliest_year": {
                "answer": {"region": "North Rhine-Westphalia", "state": "NW", "earliest_year": earliest_year_for_state("NW")},
                "endpoint": "/api/questions/nrw-earliest-year/",
            },
            "mecklenburg_vorpommern_earliest_year": {
                "answer": {"region": "Mecklenburg-Western Pomerania", "state": "MV", "earliest_year": earliest_year_for_state("MV")},
                "endpoint": "/api/questions/mecklenburg-vorpommern-earliest-year/",
            },
            "berlin_pedestrian_accidents_2023": {
                "answer": {
                    "region": "Berlin",
                    "state": "BE",
                    "year": 2023,
                    "participant": "pedestrian",
                    "accident_count": accident_count(year=2023, state_code="BE", participant="pedestrian"),
                },
                "endpoint": "/api/questions/berlin-pedestrian-accidents-2023/",
            },
            "top_districts_by_accident_rate": {
                "answer": {"year": 2023, "results": accident_rates_by_population(level=Region.Level.DISTRICT, year=2023)},
                "endpoint": "/api/questions/top-districts-by-accident-rate/",
            },
        },
        "provenance": latest_successful_import_provenance(),
    })
