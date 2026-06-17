import { Component, EventEmitter, Output, signal } from '@angular/core';

const EMOJIS = [
  '😀','😁','😂','🤣','😃','😄','😅','😆','😉','😊','😋','😎','😍','🥰','😘','😜','🤪','😝','🤑','🤗',
  '🤭','🤔','🤐','😐','😑','😶','😏','😒','🙄','😬','😮','😯','😲','😳','🥺','😢','😭','😤','😡','🤬',
  '😈','👿','💀','☠️','💩','🤡','👹','👺','👻','👽','👾','🤖','😺','😸','😹','😻','😼','😽','🙀','😿',
  '😾','👋','🤚','✋','🖐','👌','✌️','🤞','🤟','🤘','🤙','👈','👉','👆','🖕','👇','👍','👎','✊','👊',
  '🤛','🤜','👏','🙌','👐','🤲','🤝','🙏','✍️','💅','🤳','💪','❤️','🧡','💛','💚','💙','💜','🖤','🤍',
  '🤎','💔','❣️','💕','💞','💓','💗','💖','💘','💝','💟','💌','🔥','💫','⭐','🌟','✨','💥','💯','💢',
  '💬','👁️‍🗨️','🗯','💭','💤','🎉','🎊','🎈','🎁','🎀','🪄','✨','🎯','🎲','♟️','🎸','🎺','🎻','🎹','🥁',
  '🎧','🎤','🎵','🎶','🎬','🎨','🎭','🏆','🥇','🥈','🥉','⚽','🏀','🏈','⚾','🎾','🏐','🏉','🎱','🏓',
  '🏸','🏒','🏏','🥊','🥋','⛸️','🛹','🛼','🚗','🚕','🚙','🚌','🚎','🏎️','🚓','🚑','🚒','🚐','🛴','🚲',
  '🛵','🏍️','✈️','🚀','🛸','🚁','🛶','⛵','🚤','🛳️','🚉','🚄','🚅','🚇','🚃','🚆','🚈','🚝','🚟','🚠',
  '🚡','🌍','🌎','🌏','🌐','🗺️','🏔️','⛰️','🌋','🗻','🏕️','🏖️','🏜️','🏝️','🏞️','🌄','🌅','🌇','🌆','🌃',
  '🌌','🌉','🌁','🌈','☀️','🌤️','⛅','🌥️','☁️','🌦️','🌧️','⛈️','🌩️','🌨️','❄️','☃️','⛄','🔥','💧','🌊',
  '🍏','🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🫐','🍈','🍒','🍑','🥭','🍍','🥝','🍅','🍆','🥑','🥦',
  '🥬','🥒','🌶️','🫑','🌽','🥕','🫒','🧄','🧅','🥔','🍠','🥐','🍞','🥖','🥨','🧀','🥚','🍳','🥞','🧇',
  '🥓','🥩','🍗','🍖','🦴','🌭','🍔','🍟','🍕','🫓','🥪','🥙','🧆','🌮','🌯','🥗','🥘','🫕','🥫','🍝',
  '🍜','🍲','🍛','🍣','🍱','🥟','🦪','🍤','🍙','🍚','🍘','🍥','🥠','🥮','🍢','🍡','🍧','🍨','🍦','🥧',
  '🧁','🍰','🎂','🍮','🍭','🍬','🍫','🍿','🍩','🍪','🌰','🥜','🍯','🥛','🍼','☕','🫖','🍵','🧃','🥤',
  '🧋','🍶','🍺','🍻','🥂','🍷','🥃','🍸','🍹','🧉','🍾','🧊','🥄','🍴','🥣','🥡','🥢','🧂',
];

@Component({
  selector: 'app-emoji-picker',
  standalone: true,
  template: `
    <div class="emoji-picker">
      <button type="button" class="emoji-toggle" (click)="toggle()" title="Emoji">😊</button>
      @if (visible()) {
        <div class="emoji-grid">
          @for (emoji of emojis; track emoji) {
            <button type="button" class="emoji-item" (click)="select(emoji)">{{ emoji }}</button>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .emoji-picker { position: relative; display: inline-block; }
    .emoji-toggle {
      background: transparent; border: 1px solid var(--neon-dim); border-radius: 6px;
      cursor: pointer; font-size: 1.2rem; padding: 0.3rem 0.5rem; line-height: 1;
      transition: all 0.15s;
    }
    .emoji-toggle:hover { background: var(--neon-tint); border-color: var(--neon); }
    .emoji-grid {
      position: absolute; bottom: 100%; left: 0; margin-bottom: 0.5rem;
      display: grid; grid-template-columns: repeat(8, 1fr); gap: 2px;
      padding: 0.5rem; background: var(--bg-soft); border: 1px solid var(--neon-dim);
      border-radius: 8px; max-height: 200px; overflow-y: auto;
      box-shadow: 0 4px 12px rgba(0,0,0,0.4); z-index: 100; min-width: 280px;
    }
    .emoji-item {
      background: transparent; border: none; cursor: pointer; font-size: 1.3rem;
      padding: 0.2rem; border-radius: 4px; transition: background 0.1s; text-align: center;
    }
    .emoji-item:hover { background: var(--neon-tint); }
    .emoji-grid::-webkit-scrollbar { width: 4px; }
    .emoji-grid::-webkit-scrollbar-thumb { background: var(--neon-dim); border-radius: 2px; }
  `]
})
export class EmojiPickerComponent {
  @Output() emojiSelected = new EventEmitter<string>();
  protected visible = signal(false);
  protected emojis = EMOJIS;

  toggle(): void {
    this.visible.update(v => !v);
  }

  select(emoji: string): void {
    this.emojiSelected.emit(emoji);
    this.visible.set(false);
  }
}
