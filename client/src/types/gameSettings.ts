export type ConnectionSettings = {
  game_types: string[];
  teams: string[];
  start_year: number;
  end_year: number;
};

export type ConnectionGameTypeOption = {
  id: string;
  label: string;
};

export type ConnectionSettingsOptions = {
  game_types: ConnectionGameTypeOption[];
  teams: string[];
  min_year: number;
  max_year: number;
  defaults: ConnectionSettings;
};

export type ConnectionSettingsOptionsResponse = {
  options: ConnectionSettingsOptions;
};
