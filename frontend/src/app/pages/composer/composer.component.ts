import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-composer',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './composer.component.html',
  styleUrl: './composer.component.scss',
})
export class ComposerComponent {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private router = inject(Router);

  private readonly apiBase = environment.apiUrl;

  saving = signal(false);
  error = signal<string | null>(null);

  form = this.fb.nonNullable.group({
    content: ['', [Validators.required, Validators.maxLength(280)]],
  });

  save(): void {
    if (this.form.invalid) return;
    this.saving.set(true);
    this.error.set(null);
    this.http.post(`${this.apiBase}/posts/`, this.form.getRawValue()).subscribe({
      next: () => this.router.navigate(['/']),
      error: (err: HttpErrorResponse) => {
        this.error.set(err.error?.content?.[0] || 'Error al crear post');
        this.saving.set(false);
      },
    });
  }
}
