import {
  DestroyRef,
  Injectable,
  PLATFORM_ID,
  computed,
  effect,
  inject,
  signal,
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { EffectiveTheme, ThemeMode } from '../models';

const THEME_STORAGE_KEY = 'theme-mode';
const THEME_ATTRIBUTE = 'data-theme';

/**
 * Owns the `data-theme` attribute on <html>.
 *
 * Three modes - light, dark, system - persisted to localStorage. `system` is
 * resolved against `prefers-color-scheme` and re-resolved when the OS flips.
 *
 * NOTE: this service does NOT prevent the first-paint flash. That requires the
 * inline boot script in index.html (see assets/theme-boot.html), which sets the
 * attribute before any stylesheet loads. This service takes over afterwards.
 */
@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly isBrowser = isPlatformBrowser(inject(PLATFORM_ID));
  private readonly destroyRef = inject(DestroyRef);

  private readonly themeModeSignal = signal<ThemeMode>(ThemeMode.SYSTEM);
  private readonly systemPrefersDark = signal(false);

  /** The user's selected mode - light, dark or system. */
  readonly themeMode = this.themeModeSignal.asReadonly();

  /** The mode resolved to an actual theme. `system` becomes the OS preference. */
  readonly effectiveTheme = computed<EffectiveTheme>(() => {
    const mode = this.themeModeSignal();
    if (mode === ThemeMode.SYSTEM) {
      return this.systemPrefersDark() ? 'dark' : 'light';
    }
    return mode as EffectiveTheme;
  });

  readonly isDark = computed(() => this.effectiveTheme() === 'dark');

  constructor() {
    if (!this.isBrowser) return;

    this.themeModeSignal.set(this.loadFromStorage());

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    this.systemPrefersDark.set(mediaQuery.matches);

    const onChange = (e: MediaQueryListEvent) => this.systemPrefersDark.set(e.matches);
    mediaQuery.addEventListener('change', onChange);
    this.destroyRef.onDestroy(() => mediaQuery.removeEventListener('change', onChange));

    // Single reactive sink: any change to mode or OS preference writes the DOM.
    // First paint is already correct thanks to the inline boot script.
    effect(() => this.applyToDom(this.effectiveTheme()));
  }

  setTheme(mode: ThemeMode): void {
    if (!this.isBrowser) return;
    localStorage.setItem(THEME_STORAGE_KEY, mode);
    this.themeModeSignal.set(mode);
  }

  /** Cycles light -> dark -> system -> light. */
  toggleTheme(): void {
    const modes = [ThemeMode.LIGHT, ThemeMode.DARK, ThemeMode.SYSTEM];
    const next = (modes.indexOf(this.themeModeSignal()) + 1) % modes.length;
    this.setTheme(modes[next]);
  }

  private applyToDom(theme: EffectiveTheme): void {
    if (!this.isBrowser) return;
    document.documentElement.setAttribute(THEME_ATTRIBUTE, theme);
    this.updateColorSchemeMeta(theme);
  }

  /**
   * Keeps <meta name="color-scheme"> in step so browser-native UI - scrollbars,
   * form controls, the address bar - matches the app theme.
   */
  private updateColorSchemeMeta(theme: EffectiveTheme): void {
    let meta = document.querySelector('meta[name="color-scheme"]');
    if (!meta) {
      meta = document.createElement('meta');
      meta.setAttribute('name', 'color-scheme');
      document.head.appendChild(meta);
    }
    meta.setAttribute('content', theme);
  }

  private loadFromStorage(): ThemeMode {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    return stored && Object.values(ThemeMode).includes(stored as ThemeMode)
      ? (stored as ThemeMode)
      : ThemeMode.SYSTEM;
  }
}
