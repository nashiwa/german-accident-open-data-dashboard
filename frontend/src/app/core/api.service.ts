import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface ProvenanceItem {
  source: string;
  source_type: string;
  url_or_path: string;
  licence: string;
  provider: string;
  retrieved_at: string | null;
  import_run_id: number;
  rows_read: number;
  warnings: string[];
}

export interface QuestionEntry {
  answer: Record<string, unknown>;
  endpoint: string;
}

export interface MandatoryQuestionsResponse {
  questions: Record<string, QuestionEntry>;
  provenance: ProvenanceItem[];
}

export interface AccidentAggregateResponse {
  accident_count?: number;
  results?: unknown[];
  filters: Record<string, unknown>;
  provenance: ProvenanceItem[];
}

export interface RateRankingRow {
  ags: string;
  name: string;
  level: string;
  year: number;
  accident_count: number;
  population: number;
  rate_per_100000: number;
}

export interface RateAggregateResponse {
  results: RateRankingRow[];
  filters: Record<string, unknown>;
  provenance: ProvenanceItem[];
}

export interface SourceRecord {
  id: number;
  name: string;
  source_type: string;
  url_or_path: string;
  provider: string;
  licence: string;
  description: string;
}

export interface ImportRunRecord {
  id: number;
  source: SourceRecord;
  started_at: string;
  finished_at: string | null;
  status: string;
  checksum: string;
  rows_read: number;
  rows_inserted: number;
  rows_updated: number;
  warnings: string[];
}

export interface RegionRecord {
  ags: string;
  name: string;
  level: string;
  parent_id: number | null;
  state_code: string;
  state_name: string;
  population: number | null;
  area_km2: string | null;
}

export interface AccidentRecord {
  source_event_id: string;
  year: number;
  month: number;
  hour: number | null;
  weekday: number | null;
  category: string;
  accident_type: string;
  longitude: string;
  latitude: string;
  is_bicycle: boolean;
  is_car: boolean;
  is_pedestrian: boolean;
  is_motorcycle: boolean;
}

export interface AccidentPointRecord {
  id: string;
  longitude: number;
  latitude: number;
  participant: string;
}

export interface AccidentPointResponse {
  results: AccidentPointRecord[];
  filters: Record<string, unknown>;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = 'http://127.0.0.1:8000/api';

  constructor(private readonly http: HttpClient) {}

  getMandatoryQuestions() {
    return this.http.get<MandatoryQuestionsResponse>(`${this.baseUrl}/questions/mandatory/`);
  }

  getAccidentAggregate(filters: { year?: number; state?: string; participant?: string; level?: string }) {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params = params.set(key, String(value));
      }
    });
    return this.http.get<AccidentAggregateResponse>(`${this.baseUrl}/aggregates/accidents/`, { params });
  }

  getAccidents(filters: { year?: number; state?: string; participant?: string }) {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params = params.set(key, String(value));
      }
    });
    return this.http.get<AccidentRecord[]>(`${this.baseUrl}/accidents/`, { params });
  }

  getAccidentPoints(filters: { year?: number; state?: string; participant?: string }) {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params = params.set(key, String(value));
      }
    });
    return this.http.get<AccidentPointResponse>(`${this.baseUrl}/bonus/accident-points/`, { params });
  }

  getRates(filters: { year?: number; level?: string }) {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params = params.set(key, String(value));
      }
    });
    return this.http.get<RateAggregateResponse>(`${this.baseUrl}/aggregates/rates/`, { params });
  }

  getZeroAccidentMunicipalities(filters: { year: number; state: string }) {
    const params = new HttpParams().set('year', String(filters.year)).set('state', filters.state);
    return this.http.get<RegionRecord[]>(`${this.baseUrl}/bonus/zero-accident-municipalities/`, { params });
  }

  getSources() {
    return this.http.get<SourceRecord[]>(`${this.baseUrl}/metadata/sources/`);
  }

  getImportRuns() {
    return this.http.get<ImportRunRecord[]>(`${this.baseUrl}/import-runs/`);
  }
}
