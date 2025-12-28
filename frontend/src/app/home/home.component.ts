import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EmailService, EmailRequest, EmailResponse } from '../services/email.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  @Output() logout = new EventEmitter<void>();

  // State
  isDarkMode: boolean = false;

  // Form data
  intention: string = '';
  typeEmail: 'demande' | 'excuse' | 'relance' | 'remerciement' = 'demande';
  niveauFormalite: 'faible' | 'moyen' | 'élevé' = 'moyen';

  // Result data
  emailResult: EmailResponse | null = null;
  isLoading: boolean = false;
  error: string | null = null;
  warningMessage: string | null = null;
  copySuccess: boolean = false;

  constructor(private emailService: EmailService) { }

  ngOnInit() {
    // Initialize dark mode from localStorage or body class
    const savedTheme = localStorage.getItem('theme');
    this.isDarkMode = savedTheme === 'dark';
    // We assume app.component might have set the body class, but safe to sync here
    // or just let the toggle handle it.
  }

  toggleDarkMode() {
    this.isDarkMode = !this.isDarkMode;
    if (this.isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light');
  }

  onLogout() {
    this.logout.emit();
  }

  generateEmail() {
    if (!this.intention || this.intention.trim().length < 5) {
      this.error = 'Veuillez entrer une intention d\'au moins 5 caractères';
      return;
    }

    this.isLoading = true;
    this.error = null;
    this.warningMessage = null;
    this.emailResult = null;
    this.copySuccess = false;

    const request: EmailRequest = {
      intention: this.intention,
      type_email: this.typeEmail,
      niveau_formalite: this.niveauFormalite
    };

    this.emailService.generateEmail(request).subscribe({
      next: (response) => {
        this.emailResult = response;
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Erreur lors de la génération de l\'email. Veuillez réessayer.';
        this.isLoading = false;
        console.error('Error:', err);
      }
    });
  }

  copyToClipboard() {
    if (!this.emailResult) return;

    const fullEmail = `Objet: ${this.emailResult.objet}\n\n${this.emailResult.corps}`;

    // Try using the modern Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(fullEmail).then(() => {
        this.showCopySuccess();
      }).catch(err => {
        console.warn('Clipboard API failed, trying fallback:', err);
        this.copyToClipboardFallback(fullEmail);
      });
    } else {
      // Fallback for browsers/environments without Clipboard API access (e.g., HTTP on mobile)
      this.copyToClipboardFallback(fullEmail);
    }
  }

  private copyToClipboardFallback(text: string) {
    const textArea = document.createElement('textarea');
    textArea.value = text;

    // Ensure the textarea is not visible but part of the DOM
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    textArea.style.top = '0';
    document.body.appendChild(textArea);

    textArea.focus();
    textArea.select();

    try {
      const successful = document.execCommand('copy');
      if (successful) {
        this.showCopySuccess();
      } else {
        console.error('Fallback copy failed.');
        this.error = 'Erreur lors de la copie. Veuillez copier manuellement.';
      }
    } catch (err) {
      console.error('Fallback copy error:', err);
      this.error = 'Erreur lors de la copie. Veuillez copier manuellement.';
    }

    document.body.removeChild(textArea);
  }

  private showCopySuccess() {
    this.copySuccess = true;
    setTimeout(() => {
      this.copySuccess = false;
    }, 2000);
  }

  sendViaEmail() {
    if (!this.emailResult) return;

    const subject = encodeURIComponent(this.emailResult.objet);
    // Ensure consistent newlines: normalize to \n first, then to \r\n
    const bodyContent = this.emailResult.corps.replace(/\r\n/g, '\n').replace(/\n/g, '\r\n');
    const body = encodeURIComponent(bodyContent);

    // Check for mailto length limit (rough estimate, 2000 safe limit)
    const mailtoLink = `mailto:?subject=${subject}&body=${body}`;
    if (mailtoLink.length > 2000) {
      this.warningMessage = "L'email est trop long pour votre client mail par défaut. Veuillez utiliser le bouton Copier.";
      return;
    }

    // Use a hidden anchor tag to open the mail client - more reliable than window.location.href
    const link = document.createElement('a');
    link.href = mailtoLink;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  reset() {
    this.intention = '';
    this.emailResult = null;
    this.error = null;
    this.warningMessage = null;
    this.copySuccess = false;
  }
}
