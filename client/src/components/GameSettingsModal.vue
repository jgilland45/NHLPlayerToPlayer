<template>
  <div
    v-if="open"
    class="settings-backdrop"
    @click.self="emit('close')"
  >
    <div class="settings-modal">
      <header class="modal-header">
        <h2>{{ title }}</h2>
        <button
          class="close-btn"
          type="button"
          @click="emit('close')"
        >
          Close
        </button>
      </header>

      <div
        v-if="!options"
        class="loading-state"
      >
        Loading settings...
      </div>

      <div
        v-else
        class="modal-content"
      >
        <section class="settings-section">
          <div class="section-head">
            <h3>Allowed Game Types</h3>
            <button
              class="mini-btn"
              type="button"
              @click="toggleAllGameTypes"
            >
              {{ allGameTypesSelected ? 'Deselect All' : 'Select All' }}
            </button>
          </div>
          <p class="hint">
            Selected: {{ draft.game_types.length }} / {{ options.game_types.length }}
          </p>
          <div class="checkbox-grid">
            <label
              v-for="gameType in options.game_types"
              :key="gameType.id"
              class="check-item"
            >
              <input
                :checked="draft.game_types.includes(gameType.id)"
                type="checkbox"
                @change="toggleGameType(gameType.id)"
              >
              <span>{{ gameType.label }}</span>
            </label>
          </div>
        </section>

        <section class="settings-section">
          <div class="section-head">
            <h3>Allowed Teams</h3>
            <button
              class="mini-btn"
              type="button"
              @click="toggleAllTeams"
            >
              {{ allTeamsSelected ? 'Deselect All' : 'Select All' }}
            </button>
          </div>
          <p class="hint">
            Selected: {{ draft.teams.length }} / {{ options.teams.length }}
          </p>
          <div class="team-list">
            <label
              v-for="team in options.teams"
              :key="team"
              class="check-item"
            >
              <input
                :checked="draft.teams.includes(team)"
                type="checkbox"
                @change="toggleTeam(team)"
              >
              <span>{{ team }}</span>
            </label>
          </div>
        </section>

        <section class="settings-section">
          <h3>Allowed Seasons</h3>
          <p class="hint">
            Use slider or type years directly.
          </p>
          <div class="season-inputs">
            <label class="year-input">
              <span>From</span>
              <input
                v-model.number="draft.start_year"
                :min="options.min_year"
                :max="options.max_year"
                type="number"
                @change="normalizeYearRange"
              >
            </label>
            <label class="year-input">
              <span>To</span>
              <input
                v-model.number="draft.end_year"
                :min="options.min_year"
                :max="options.max_year"
                type="number"
                @change="normalizeYearRange"
              >
            </label>
          </div>
          <div class="slider-stack">
            <input
              v-model.number="draft.start_year"
              :min="options.min_year"
              :max="options.max_year"
              class="slider"
              type="range"
              @input="onStartSliderInput"
            >
            <input
              v-model.number="draft.end_year"
              :min="options.min_year"
              :max="options.max_year"
              class="slider"
              type="range"
              @input="onEndSliderInput"
            >
          </div>
          <p class="range-caption">
            {{ draft.start_year }} to {{ draft.end_year }}
          </p>
        </section>
      </div>

      <footer class="modal-footer">
        <p
          v-if="saveDisabled"
          class="validation"
        >
          Select at least one game type and one team.
        </p>
        <div class="footer-actions">
          <button
            class="action-btn secondary"
            type="button"
            @click="emit('close')"
          >
            Cancel
          </button>
          <button
            class="action-btn"
            :disabled="saveDisabled || saving"
            type="button"
            @click="saveSettings"
          >
            {{ saving ? 'Saving...' : 'Apply Settings' }}
          </button>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';

import type { ConnectionSettings, ConnectionSettingsOptions } from '@/types/gameSettings';

const props = withDefaults(
  defineProps<{
    open: boolean;
    options: ConnectionSettingsOptions | null;
    initialSettings: ConnectionSettings | null;
    saving?: boolean;
    title?: string;
  }>(),
  {
    saving: false,
    title: 'Game Settings',
  },
);

const emit = defineEmits<{
  (event: 'close'): void;
  (event: 'save', payload: ConnectionSettings): void;
}>();

const draft = ref<ConnectionSettings>({
  game_types: [],
  teams: [],
  start_year: 1917,
  end_year: 2025,
});
const initializedForCurrentOpen = ref(false);

const getNormalizedSettings = (raw: ConnectionSettings | null): ConnectionSettings => {
  if (!props.options) {
    return { ...draft.value };
  }

  const defaults = props.options.defaults;
  const requested = raw ?? defaults;

  const allowedGameTypes = props.options.game_types.map((entry) => entry.id);
  const allowedGameTypeSet = new Set(allowedGameTypes);
  const requestedGameTypes = (requested.game_types ?? []).filter((item) => allowedGameTypeSet.has(item));
  const selectedGameTypeSet = new Set(
    (requestedGameTypes.length > 0 ? requestedGameTypes : defaults.game_types).filter((item) => allowedGameTypeSet.has(item)),
  );
  const game_types = allowedGameTypes.filter((item) => selectedGameTypeSet.has(item));

  const allowedTeams = props.options.teams;
  const allowedTeamSet = new Set(allowedTeams);
  const requestedTeams = (requested.teams ?? []).filter((item) => allowedTeamSet.has(item));
  const selectedTeamSet = new Set(
    (requestedTeams.length > 0 ? requestedTeams : defaults.teams).filter((item) => allowedTeamSet.has(item)),
  );
  const teams = allowedTeams.filter((item) => selectedTeamSet.has(item));

  const startCandidate = Number(requested.start_year ?? defaults.start_year);
  const endCandidate = Number(requested.end_year ?? defaults.end_year);
  const boundedStart = Math.min(Math.max(startCandidate, props.options.min_year), props.options.max_year);
  const boundedEnd = Math.min(Math.max(endCandidate, props.options.min_year), props.options.max_year);

  return {
    game_types,
    teams,
    start_year: Math.min(boundedStart, boundedEnd),
    end_year: Math.max(boundedStart, boundedEnd),
  };
};

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) {
      initializedForCurrentOpen.value = false;
      return;
    }
    if (!props.options) {
      return;
    }
    draft.value = getNormalizedSettings(props.initialSettings);
    initializedForCurrentOpen.value = true;
  },
  { immediate: true },
);

const allGameTypesSelected = computed(() => {
  if (!props.options) {
    return false;
  }
  return draft.value.game_types.length === props.options.game_types.length;
});

const allTeamsSelected = computed(() => {
  if (!props.options) {
    return false;
  }
  return draft.value.teams.length === props.options.teams.length;
});

const saveDisabled = computed(() => {
  return !props.options || draft.value.game_types.length === 0 || draft.value.teams.length === 0;
});

const toggleGameType = (id: string) => {
  const selected = new Set(draft.value.game_types);
  if (selected.has(id)) {
    selected.delete(id);
  } else {
    selected.add(id);
  }
  if (!props.options) {
    draft.value.game_types = Array.from(selected);
    return;
  }
  draft.value.game_types = props.options.game_types.map((item) => item.id).filter((item) => selected.has(item));
};

const toggleAllGameTypes = () => {
  if (!props.options) {
    return;
  }
  draft.value.game_types = allGameTypesSelected.value ? [] : props.options.game_types.map((entry) => entry.id);
};

const toggleTeam = (team: string) => {
  const selected = new Set(draft.value.teams);
  if (selected.has(team)) {
    selected.delete(team);
  } else {
    selected.add(team);
  }
  if (!props.options) {
    draft.value.teams = Array.from(selected);
    return;
  }
  draft.value.teams = props.options.teams.filter((item) => selected.has(item));
};

const toggleAllTeams = () => {
  if (!props.options) {
    return;
  }
  draft.value.teams = allTeamsSelected.value ? [] : [...props.options.teams];
};

const normalizeYearRange = () => {
  if (!props.options) {
    return;
  }
  const start = Number.isFinite(draft.value.start_year) ? Number(draft.value.start_year) : props.options.min_year;
  const end = Number.isFinite(draft.value.end_year) ? Number(draft.value.end_year) : props.options.max_year;

  const boundedStart = Math.min(Math.max(start, props.options.min_year), props.options.max_year);
  const boundedEnd = Math.min(Math.max(end, props.options.min_year), props.options.max_year);

  draft.value.start_year = Math.min(boundedStart, boundedEnd);
  draft.value.end_year = Math.max(boundedStart, boundedEnd);
};

const onStartSliderInput = () => {
  if (draft.value.start_year > draft.value.end_year) {
    draft.value.end_year = draft.value.start_year;
  }
  normalizeYearRange();
};

const onEndSliderInput = () => {
  if (draft.value.end_year < draft.value.start_year) {
    draft.value.start_year = draft.value.end_year;
  }
  normalizeYearRange();
};

const saveSettings = () => {
  if (saveDisabled.value) {
    return;
  }
  normalizeYearRange();
  emit('save', getNormalizedSettings(draft.value));
};
</script>

<style scoped lang="postcss">
.settings-backdrop {
  @apply fixed inset-0 z-40 flex items-center justify-center bg-slate-950/80 p-4;
}

.settings-modal {
  @apply flex max-h-[92vh] w-full max-w-4xl flex-col overflow-hidden rounded-xl border border-slate-700 bg-slate-900 text-white shadow-xl;
}

.modal-header {
  @apply flex items-center justify-between border-b border-slate-700 px-4 py-3;

  h2 {
    @apply text-xl font-semibold;
  }
}

.close-btn {
  @apply rounded bg-slate-700 px-3 py-1 text-sm text-slate-100 hover:bg-slate-600;
}

.loading-state {
  @apply p-6 text-slate-300;
}

.modal-content {
  @apply flex-1 overflow-y-auto p-4;
}

.settings-section {
  @apply mb-4 rounded border border-slate-700 bg-slate-800 p-3;

  h3 {
    @apply text-base font-semibold;
  }
}

.section-head {
  @apply flex items-center justify-between gap-2;
}

.hint {
  @apply mt-1 text-xs text-slate-300;
}

.mini-btn {
  @apply rounded bg-slate-700 px-2 py-1 text-xs text-slate-100 hover:bg-slate-600;
}

.checkbox-grid {
  @apply mt-2 grid grid-cols-1 gap-2 md:grid-cols-2;
}

.team-list {
  @apply mt-2 grid max-h-56 grid-cols-2 gap-2 overflow-y-auto pr-1 sm:grid-cols-4;
}

.check-item {
  @apply flex items-center gap-2 rounded bg-slate-900 px-2 py-1 text-sm text-slate-100;
}

.season-inputs {
  @apply mt-2 flex flex-col gap-2 sm:flex-row;
}

.year-input {
  @apply flex flex-col gap-1 text-sm text-slate-200;

  input {
    @apply rounded border border-slate-600 bg-slate-900 px-3 py-2 text-white;
  }
}

.slider-stack {
  @apply relative mt-4 h-8;
}

.slider {
  @apply pointer-events-none absolute left-0 top-0 h-8 w-full appearance-none bg-transparent;
}

.slider::-webkit-slider-thumb {
  @apply pointer-events-auto h-4 w-4 cursor-pointer appearance-none rounded-full bg-emerald-500;
}

.slider::-moz-range-thumb {
  @apply pointer-events-auto h-4 w-4 cursor-pointer appearance-none rounded-full border-0 bg-emerald-500;
}

.range-caption {
  @apply mt-1 text-xs text-slate-300;
}

.modal-footer {
  @apply border-t border-slate-700 px-4 py-3;
}

.validation {
  @apply text-xs text-red-300;
}

.footer-actions {
  @apply mt-2 flex justify-end gap-2;
}

.action-btn {
  @apply rounded bg-emerald-600 px-4 py-2 font-semibold text-white;

  &:disabled {
    @apply cursor-not-allowed bg-slate-500;
  }

  &.secondary {
    @apply bg-slate-600;
  }
}
</style>
