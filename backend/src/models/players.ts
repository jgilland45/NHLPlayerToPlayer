export type PlayerInput = {
    playerId: string;
    name: string;
    positionCode: string;
    teamId?: string;
    teamAbbrev?: string;
    lastTeamId?: string;
    lastTeamAbbrev?: string;
    lastSeasonId?: string;
    sweaterNumber?: number;
    active: boolean;
    height: string;
    heightInInches: number;
    heightInCentimeters: number;
    weightInPounds: number;
    weightInKilograms: number;
    birthCity: string;
    birthStateProvince?: string;
    birthCountry: string;
}

export type PlayerOutput = {
    playerId: string;
    name: string;
}