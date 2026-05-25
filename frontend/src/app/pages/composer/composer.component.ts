import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';

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

  private readonly apiBase = 'http://localhost:8000/api';

  saving = signal(false);
  error = signal<string | null>(null);

  form = this.fb.nonNullable.group({
    content: ['', [Validators.required, Validators.maxLength(280)]],
    image_url: [''],
  });

  save(): void {
    if (this.form.invalid) return;
    this.saving.set(true);
    this.error.set(null);

    const body: Record<string, any> = { content: this.form.controls.content.value };
    const img = this.form.controls.image_url.value?.trim();
    if (img) body['image_url'] = img;

    this.http.post(`${this.apiBase}/posts/`, body).subscribe({
      next: () => this.router.navigate(['/']),
      error: (err: HttpErrorResponse) => {
        this.error.set(err.error?.content?.[0] || 'Error al crear post');
        this.saving.set(false);
      },
    });
  }
}
