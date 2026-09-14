import { Injectable, PLATFORM_ID, inject, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { BehaviorSubject, Observable } from 'rxjs';
import { Palette, PALETTES, PaletteInfo } from '../models';

const PALETTE_STORAGE_KEY = 'palette';
const PALETTE_ATTRIBUTE = 'data-palette';
const DEFAULT_PALETTE = Palette.BLUE;

@Injectable({
  providedIn: 'root'
})
export class PaletteService {
  private readonly platformId = inject(PLATFORM_ID);
  private readonly isBrowser = isPlatformBrowser(this.platformId);

  private readonly paletteSubject = new BehaviorSubject<Palette>(DEFAULT_PALETTE);

  // Signal-based API for template reactivity
  private readonly paletteSignal = signal<Palette>(DEFAULT_PALETTE);
  readonly palette = this.paletteSignal.asReadonly();

  // Expose palette options
  readonly palettes: PaletteInfo[] = PALETTES;

  constructor() {
    this.initialize();
  }

  /**
   * Initialize palette service
   */
  private initialize(): void {
    if (!this.isBrowser) return;

    // Load persisted palette
    const storedPalette = this.loadPaletteFromStorage();
    this.paletteSubject.next(storedPalette);
    this.paletteSignal.set(storedPalette);

    // Apply initial palette
    this.applyPaletteToDOM();

    // Subscribe to palette changes
    this.paletteSubject.subscribe((palette) => {
      this.paletteSignal.set(palette);
      this.applyPaletteToDOM();
    });
  }

  /**
   * Set the palette
   */
  setPalette(palette: Palette): void {
    if (!this.isBrowser) return;

    this.persistPaletteToStorage(palette);
    this.paletteSubject.next(palette);
  }

  /**
   * Get the current palette as an observable
   */
  getPalette(): Observable<Palette> {
    return this.paletteSubject.asObservable();
  }

  /**
   * Get the current palette value
   */
  getCurrentPalette(): Palette {
    return this.paletteSubject.getValue();
  }

  /**
   * Get palette info by ID
   */
  getPaletteInfo(palette: Palette): PaletteInfo | undefined {
    return PALETTES.find(p => p.id === palette);
  }

  /**
   * Apply the palette to the DOM
   */
  private applyPaletteToDOM(): void {
    if (!this.isBrowser) return;

    const palette = this.paletteSubject.getValue();
    document.documentElement.setAttribute(PALETTE_ATTRIBUTE, palette);
  }

  /**
   * Load palette from localStorage
   */
  private loadPaletteFromStorage(): Palette {
    if (!this.isBrowser) return DEFAULT_PALETTE;

    const storedPalette = localStorage.getItem(PALETTE_STORAGE_KEY);

    if (storedPalette && Object.values(Palette).includes(storedPalette as Palette)) {
      return storedPalette as Palette;
    }

    return DEFAULT_PALETTE;
  }

  /**
   * Persist palette to localStorage
   */
  private persistPaletteToStorage(palette: Palette): void {
    if (!this.isBrowser) return;

    localStorage.setItem(PALETTE_STORAGE_KEY, palette);
  }
}
