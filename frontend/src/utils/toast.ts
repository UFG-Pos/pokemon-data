// Simple toast system
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

class ToastManager {
  private toasts: ToastMessage[] = [];
  private listeners: ((toasts: ToastMessage[]) => void)[] = [];

  subscribe(listener: (toasts: ToastMessage[]) => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notify() {
    this.listeners.forEach(listener => listener([...this.toasts]));
  }

  private addToast(type: ToastType, message: string, duration = 5000) {
    const id = Math.random().toString(36).substr(2, 9);
    const toast: ToastMessage = { id, type, message, duration };
    
    this.toasts.push(toast);
    this.notify();

    if (duration > 0) {
      setTimeout(() => {
        this.removeToast(id);
      }, duration);
    }

    return id;
  }

  removeToast(id: string) {
    this.toasts = this.toasts.filter(toast => toast.id !== id);
    this.notify();
  }

  success(message: string, duration?: number) {
    return this.addToast('success', message, duration);
  }

  error(message: string, duration?: number) {
    return this.addToast('error', message, duration);
  }

  warning(message: string, duration?: number) {
    return this.addToast('warning', message, duration);
  }

  info(message: string, duration?: number) {
    return this.addToast('info', message, duration);
  }

  clear() {
    this.toasts = [];
    this.notify();
  }
}

export const toast = new ToastManager();
