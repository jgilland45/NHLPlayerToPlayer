from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from typing import Any, List, Optional, Union, get_args, get_origin, get_type_hints
import types

import statics


def dataclass_from_dict(data: Any, target_type: Any) -> Any:
    """Build a dataclass and its nested fields from decoded API data."""
    if data is None or target_type is Any:
        return data

    origin = get_origin(target_type)
    type_args = get_args(target_type)

    if origin in (Union, types.UnionType):
        non_none_type = next((arg for arg in type_args if arg is not type(None)), Any)
        return dataclass_from_dict(data, non_none_type)
    if origin is list:
        item_type = type_args[0] if type_args else Any
        return [dataclass_from_dict(item, item_type) for item in data]
    if origin is dict:
        key_type, value_type = type_args or (Any, Any)
        return {
            dataclass_from_dict(key, key_type): dataclass_from_dict(value, value_type)
            for key, value in data.items()
        }
    if isinstance(target_type, type) and issubclass(target_type, Enum):
        return target_type(data)
    if isinstance(target_type, type) and is_dataclass(target_type):
        type_hints = get_type_hints(target_type)
        return target_type(**{
            field.name: dataclass_from_dict(data[field.name], type_hints[field.name])
            for field in fields(target_type)
            if field.name in data
        })

    return data

@dataclass
class DBGame:
    id: int
    easternStartTime: str
    gameDate: str
    gameNumber: int
    gameScheduleStateId: int
    gameStateId: int
    gameType: statics.GameType
    homeScore: int
    homeTeamId: int
    period: int
    season: int
    visitingScore: int
    visitingTeamId: int

@dataclass
class DBPlayer:
    playerId: str
    name: str
    positionCode: str
    lastTeamId: str
    lastTeamAbbrev: str
    active: bool
    height: str
    heightInInches: int
    heightInCentimeters: int
    weightInPounds: int
    weightInKilograms: int
    birthCity: str
    birthStateProvince: str
    birthCountry: str
    teamId: Optional[str] = None
    teamAbbrev: Optional[str] = None
    lastSeasonId: Optional[str] = None
    sweaterNumber: Optional[str] = None

@dataclass
class DBTeams:
    teamId: int
    teamAbbrev: str
    teamName: str

@dataclass
class TeamAPI:
    id: int
    fullName: str
    leagueId: int
    rawTricode: str
    triCode: str
    franchiseId: Optional[int] = None

@dataclass
class Venue:
    default: str

@dataclass
class VenueLocation:
    default: str

@dataclass
class TvBroadcasts:
    id: int
    market: str
    countryCode: str
    network: str
    sequenceNumber: int

@dataclass
class PeriodDescriptor:
    number: int
    periodType: str
    maxRegulationPeriods: int

@dataclass
class CommonName:
    default: str

@dataclass
class PlaceName:
    default: str

@dataclass
class PlaceNameWithPreposition:
    default: str

@dataclass
class AwayTeam:
    id: int
    commonName: CommonName
    abbrev: str
    score: int
    logo: str
    darkLogo: str
    placeName: PlaceName
    placeNameWithPreposition: PlaceNameWithPreposition
    sog: Optional[int] = None

@dataclass
class HomeTeam:
    id: int
    commonName: CommonName
    abbrev: str
    score: int
    logo: str
    darkLogo: str
    placeName: PlaceName
    placeNameWithPreposition: PlaceNameWithPreposition
    sog: Optional[int] = None

@dataclass
class Clock:
    timeRemaining: str
    secondsRemaining: int
    running: bool
    inIntermission: bool

@dataclass
class Name:
    default: str

@dataclass
class Forwards:
    playerId: int
    sweaterNumber: int
    name: Name
    position: str
    goals: int
    assists: int
    points: int
    plusMinus: int
    pim: int
    hits: int
    powerPlayGoals: int
    sog: int
    blockedShots: int
    shifts: int
    giveaways: Optional[int] = None
    takeaways: Optional[int] = None
    faceoffWinningPctg: Optional[float] = None
    toi: Optional[str] = None

@dataclass
class Defense:
    playerId: int
    sweaterNumber: int
    name: Name
    position: str
    goals: int
    assists: int
    points: int
    plusMinus: int
    pim: int
    hits: int
    powerPlayGoals: int
    sog: int
    blockedShots: int
    shifts: int
    giveaways: Optional[int] = None
    takeaways: Optional[int] = None
    faceoffWinningPctg: Optional[float] = None
    toi: Optional[str] = None

@dataclass
class Goalies:
    playerId: int
    sweaterNumber: int
    name: Name
    position: str
    evenStrengthGoalsAgainst: int
    powerPlayGoalsAgainst: int
    shorthandedGoalsAgainst: int
    toi: str
    goalsAgainst: Optional[int] = None
    shotsAgainst: Optional[int] = None
    pim: Optional[int] = None
    starter: Optional[bool] = None
    evenStrengthShotsAgainst: Optional[str] = None
    powerPlayShotsAgainst: Optional[str] = None
    shorthandedShotsAgainst: Optional[str] = None
    saveShotsAgainst: Optional[str] = None
    saves: Optional[int] = None

@dataclass
class TeamStats:
    forwards: List[Forwards]
    defense: List[Defense]
    goalies: List[Goalies]

@dataclass
class PlayerByGameStats:
    awayTeam: TeamStats
    homeTeam: TeamStats

@dataclass
class GameOutcome:
    lastPeriodType: str
    otPeriods: Optional[int] = None

@dataclass
class GameLong:
    id: int
    season: int
    gameType: statics.GameType
    limitedScoring: bool
    gameDate: str
    venue: Venue
    venueLocation: VenueLocation
    startTimeUTC: str
    easternUTCOffset: str
    venueUTCOffset: str
    tvBroadcasts: List[TvBroadcasts]
    gameState: str
    gameScheduleState: str
    periodDescriptor: PeriodDescriptor
    regPeriods: int
    awayTeam: AwayTeam
    homeTeam: HomeTeam
    clock: Clock
    playerByGameStats: PlayerByGameStats
    gameOutcome: GameOutcome
    specialEvent: Optional[str] = None

@dataclass
class FullTeamName:
    default: str

@dataclass
class TeamCommonName:
    default: str

@dataclass
class TeamPlaceNameWithPreposition:
    default: str

@dataclass
class FirstName:
    default: str

@dataclass
class LastName:
    default: str

@dataclass
class BirthCity:
    default: str

@dataclass
class BirthStateProvince:
    default: str

@dataclass
class DraftDetails:
    year: int
    teamAbbrev: str
    round: int
    pickInRound: int
    overallPick: int

@dataclass
class SubSeason:
    assists: int
    gameWinningGoals: int
    gamesPlayed: int
    goals: int
    otGoals: int
    pim: int
    plusMinus: int
    points: int
    powerPlayGoals: int
    powerPlayPoints: int
    shootingPctg: float
    shorthandedGoals: int
    shorthandedPoints: int
    shots: int

@dataclass
class Career:
    assists: int
    gameWinningGoals: int
    gamesPlayed: int
    goals: int
    otGoals: int
    pim: int
    plusMinus: int
    points: int
    powerPlayGoals: int
    powerPlayPoints: int
    shootingPctg: float
    shorthandedGoals: int
    shorthandedPoints: int
    shots: int

@dataclass
class RegularSeason:
    subSeason: SubSeason
    career: Career

@dataclass
class Playoffs:
    subSeason: SubSeason
    career: Career

@dataclass
class FeaturedStats:
    season: int
    regularSeason: RegularSeason
    playoffs: Playoffs

@dataclass
class CareerTotals:
    regularSeason: RegularSeason
    playoffs: Playoffs

@dataclass
class Last5Games:
    assists: int
    gameDate: str
    gameId: int
    gameTypeId: statics.GameType
    goals: int
    homeRoadFlag: str
    opponentAbbrev: str
    pim: int
    plusMinus: int
    points: int
    powerPlayGoals: int
    shifts: int
    shorthandedGoals: int
    shots: int
    teamAbbrev: str
    toi: str

@dataclass
class TeamName:
    default: str

@dataclass
class SeasonTotals:
    assists: int
    gameTypeId: statics.GameType
    gamesPlayed: int
    goals: int
    leagueAbbrev: str
    pim: int
    points: int
    season: int
    sequence: int
    teamName: TeamName

@dataclass
class Trophy:
    default: str

@dataclass
class Seasons:
    assists: int
    blockedShots: int
    gameTypeId: statics.GameType
    gamesPlayed: int
    goals: int
    hits: int
    pim: int
    plusMinus: int
    points: int
    seasonId: int

@dataclass
class Awards:
    trophy: Trophy
    seasons: List[Seasons]

@dataclass
class CurrentTeamRoster:
    playerId: int
    lastName: LastName
    firstName: FirstName
    playerSlug: str

@dataclass
class PlayerLong:
    playerId: int
    isActive: bool
    firstName: FirstName
    lastName: LastName
    badges: List[Any]
    position: str
    headshot: str
    heroImage: str
    heightInInches: int
    heightInCentimeters: int
    weightInPounds: int
    weightInKilograms: int
    birthDate: str
    birthCity: BirthCity
    birthStateProvince: BirthStateProvince
    birthCountry: str
    shootsCatches: str
    playerSlug: str
    inTop100AllTime: int
    inHHOF: int
    shopLink: str
    twitterLink: str
    watchLink: str
    seasonTotals: List[SeasonTotals]
    currentTeamId: Optional[int] = None
    currentTeamAbbrev: Optional[str] = None
    fullTeamName: Optional[FullTeamName] = None
    teamCommonName: Optional[TeamCommonName] = None
    teamPlaceNameWithPreposition: Optional[TeamPlaceNameWithPreposition] = None
    teamLogo: Optional[str] = None
    sweaterNumber: Optional[str] = None
    draftDetails: Optional[DraftDetails] = None
    featuredStats: Optional[FeaturedStats] = None
    careerTotals: Optional[CareerTotals] = None
    last5Games: Optional[List[Last5Games]] = None
    awards: Optional[List[Awards]] = None
    currentTeamRoster: Optional[List[CurrentTeamRoster]] = None

@dataclass
class GameStorage:
    gameId: int
    season: int
    playerId: int
    gameType: statics.GameType
    teamId: Optional[int] = None

@dataclass
class OptionalGameStorage:
    gameId: Optional[int] = None
    season: Optional[int] = None
    playerId: Optional[int] = None
    gameType: Optional[statics.GameType] = None
    teamId: Optional[int] = None

@dataclass
class TeammateRelationship:
    player1Id: int
    player2Id: int
    season: int
    gameType: statics.GameType
    teamId: Optional[int] = None

