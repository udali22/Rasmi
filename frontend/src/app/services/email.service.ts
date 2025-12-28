import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface EmailRequest {
    intention: string;
    type_email: 'demande' | 'excuse' | 'relance' | 'remerciement';
    niveau_formalite: 'faible' | 'moyen' | 'élevé';
}

export interface EmailResponse {
    objet: string;
    corps: string;
}

@Injectable({
    providedIn: 'root'
})
export class EmailService {
    // Use the current hostname to determine backend URL (allows testing on mobile)
    private apiUrl = `http://${window.location.hostname}:8000`;

    constructor(private http: HttpClient) { }

    generateEmail(request: EmailRequest): Observable<EmailResponse> {
        return this.http.post<EmailResponse>(`${this.apiUrl}/generate-email`, request);
    }
}
