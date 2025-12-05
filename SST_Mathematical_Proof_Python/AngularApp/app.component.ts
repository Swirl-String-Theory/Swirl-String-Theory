
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // Although we use simple event bindings, good to have
import { presets } from './utils/presets';
import { GlobalSettings } from './types';
import { SimulationCardComponent } from './components/simulation-card.component';
import { IconComponent } from './components/icon.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, SimulationCardComponent, IconComponent],
  template: `
    <div class="min-h-screen bg-black text-gray-100 font-sans selection:bg-cyan-500 selection:text-black">
      
      <!-- Sticky Header Controls -->
      <header class="sticky top-0 z-50 bg-gray-900/80 backdrop-blur-md border-b border-gray-800 shadow-2xl">
        <div class="max-w-7xl mx-auto px-4 py-4">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            
            <!-- Title -->
            <div class="flex items-center gap-3">
              <div class="p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/20">
                <app-icon name="activity" class="text-cyan-400" [size]="24"></app-icon>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-white tracking-tight">Physics <span class="text-cyan-400">Simulator</span></h1>
              </div>
            </div>

            <!-- Controls Grid -->
            <div class="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4 items-end">
              
              <!-- Time/Speed Control -->
              <div class="space-y-1.5">
                 <label class="text-xs font-medium text-gray-400 flex justify-between">
                    <span>Sim Speed</span>
                    <span class="text-cyan-400">{{ isPlaying ? globalSettings.timeScale.toFixed(1) + 'x' : 'PAUSED' }}</span>
                 </label>
                 <div class="flex items-center gap-2 h-7">
                     <button 
                        (click)="togglePlay()"
                        class="p-1.5 rounded transition-colors"
                        [class]="isPlaying ? 'bg-gray-800 hover:bg-gray-700 text-red-400' : 'bg-cyan-500 hover:bg-cyan-400 text-black'"
                     >
                        <app-icon [name]="isPlaying ? 'pause' : 'play'" [size]="14"></app-icon>
                     </button>
                     <input 
                        type="range" min="0.1" max="3" step="0.1"
                        [value]="isPlaying ? globalSettings.timeScale : 1"
                        (input)="onTimeScaleChange($event)"
                        class="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                     />
                 </div>
              </div>

               <!-- Gravity Control -->
              <div class="space-y-1.5">
                 <label class="text-xs font-medium text-gray-400 flex justify-between">
                    <span>Gravity</span>
                    <span class="text-cyan-400">{{ globalSettings.gravityMultiplier.toFixed(1) }}x</span>
                 </label>
                 <div class="flex items-center h-7">
                    <input 
                        type="range" min="0" max="3" step="0.1"
                        [value]="globalSettings.gravityMultiplier"
                        (input)="updateSetting('gravityMultiplier', $event)"
                        class="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                    />
                 </div>
              </div>

              <!-- Rotation Control -->
              <div class="space-y-1.5">
                 <label class="text-xs font-medium text-gray-400 flex justify-between">
                    <span>Rotation</span>
                    <span class="text-cyan-400">{{ globalSettings.rotationMultiplier.toFixed(1) }}x</span>
                 </label>
                 <div class="flex items-center h-7">
                    <input 
                        type="range" min="0" max="5" step="0.1"
                        [value]="globalSettings.rotationMultiplier"
                        (input)="updateSetting('rotationMultiplier', $event)"
                        class="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                    />
                 </div>
              </div>

               <!-- Restitution Control -->
               <div class="space-y-1.5">
                 <label class="text-xs font-medium text-gray-400 flex justify-between">
                    <span>Bounciness</span>
                    <span class="text-cyan-400">{{ globalSettings.bouncinessMultiplier.toFixed(1) }}x</span>
                 </label>
                 <div class="flex items-center h-7">
                    <input 
                        type="range" min="0.1" max="1" step="0.1"
                        [value]="globalSettings.bouncinessMultiplier"
                        (input)="updateSetting('bouncinessMultiplier', $event)"
                        class="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                    />
                 </div>
              </div>

            </div>
          </div>
        </div>
      </header>

      <!-- Grid Content -->
      <main class="max-w-7xl mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 justify-items-center">
          <app-simulation-card 
            *ngFor="let preset of presets"
            [config]="preset"
            [globalSettings]="globalSettings"
          ></app-simulation-card>
        </div>
      </main>

    </div>
  `
})
export class AppComponent {
  presets = presets;
  
  globalSettings: GlobalSettings = {
    timeScale: 1.0,
    gravityMultiplier: 1.0,
    rotationMultiplier: 1.0,
    bouncinessMultiplier: 1.0,
  };

  isPlaying = true;

  togglePlay() {
    if (this.isPlaying) {
      this.globalSettings = { ...this.globalSettings, timeScale: 0 };
    } else {
      this.globalSettings = { ...this.globalSettings, timeScale: 1 };
    }
    this.isPlaying = !this.isPlaying;
  }

  onTimeScaleChange(event: Event) {
    const value = parseFloat((event.target as HTMLInputElement).value);
    if (!this.isPlaying) this.togglePlay();
    this.globalSettings = { ...this.globalSettings, timeScale: value };
  }

  updateSetting(key: keyof GlobalSettings, event: Event) {
    const value = parseFloat((event.target as HTMLInputElement).value);
    this.globalSettings = { ...this.globalSettings, [key]: value };
  }
}
