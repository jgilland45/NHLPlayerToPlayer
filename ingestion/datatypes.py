from dataclasses import dataclass
from typing import Optional, List, Any

@dataclass
class GameShort:
    id: int
    easternStartTime: str
    gameDate: str
    gameNumber: int
    gameScheduleStateId: int
    gameStateId: int
    gameType: int
    homeScore: int
    homeTeamId: int
    period: int
    season: int
    visitingScore: int
    visitingTeamId: int

@dataclass
class PlayerShort:
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
    fr: str

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
    faceoffWinningPctg: int
    blockedShots: int
    shifts: int
    giveaways: int
    takeaways: int
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
    faceoffWinningPctg: int
    blockedShots: int
    shifts: int
    giveaways: int
    takeaways: int
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
    pim: int
    goalsAgainst: int
    toi: str
    starter: bool
    shotsAgainst: int
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
    otPeriods: int

@dataclass
class GameLong:
    id: int
    season: int
    gameType: int
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

@dataclass
class FullTeamName:
    default: str
    fr: str

@dataclass
class TeamCommonName:
    default: str

@dataclass
class TeamPlaceNameWithPreposition:
    default: str
    fr: str

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
    gameTypeId: int
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
    gameTypeId: int
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
    fr: str

@dataclass
class Seasons:
    assists: int
    blockedShots: int
    gameTypeId: int
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