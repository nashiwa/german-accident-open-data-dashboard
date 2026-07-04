import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/examiner-questions/examiner-questions.component').then((m) => m.ExaminerQuestionsComponent),
  },
  {
    path: 'explorer',
    loadComponent: () =>
      import('./features/accident-explorer/accident-explorer.component').then((m) => m.AccidentExplorerComponent),
  },
  {
    path: 'rankings',
    loadComponent: () =>
      import('./features/rates-rankings/rates-rankings.component').then((m) => m.RatesRankingsComponent),
  },
  {
    path: 'map',
    loadComponent: () => import('./features/map-view/map-view.component').then((m) => m.MapViewComponent),
  },
  {
    path: 'sources',
    loadComponent: () =>
      import('./features/sources-imports/sources-imports.component').then((m) => m.SourcesImportsComponent),
  },
];
