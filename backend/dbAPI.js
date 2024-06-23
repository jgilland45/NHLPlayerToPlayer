// video: https://www.youtube.com/watch?v=mnH_1YGR2PM&ab_channel=ByteMyke
const express = require("express");
const bodyParser = require("body-parser");

const app = express();
const sqlite = require("sqlite3").verbose();
const url = require("url");
const cors = require("cors");

let sql;
const db = new sqlite.Database("nhlPlayers.db", sqlite.OPEN_READWRITE, (err) => {
  if (err) return console.error(err);
});

app.use(cors());
app.use(bodyParser.json());

// // post request
// app.post("/quote", (req, res) => {
//   try {
//     const { movie, quote, character } = req.body;
//     sql = "INSERT INTO quote(movie, quote, character) VALUES (?,?,?)";
//     db.run(sql, [movie, quote, character], (err) => {
//       if (err) return res.json({ status: 300, success: false, error: err });

//       console.log("successful input ", movie, quote, character);
//     });
//     return res.json({
//       status: 200,
//       success: true,
//     });
//   } catch (error) {
//     return res.json({
//       status: 400,
//       success: false,
//     });
//   }
// });

// get requests
// get all player names urls
app.get("/players", (req, res) => {
  sql = "SELECT * FROM PLAYERS";
  try {
    // const queryObject = url.parse(req.url, true).query; // query parameters
    // if (queryObject.field && queryObject.type) sql += ` WHERE ${queryObject.field} LIKE '%${queryObject.type}%'`
    db.all(sql, [], (err, rows) => {
      if (err) return res.json({ status: 300, success: false, error: err });

      if (rows.length < 1) return res.json({ status: 300, success: false, error: "No match" });
      console.log('returned all players!');
      return res.json({
        status: 200,
        data: rows,
        success: true,
      });
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});

// get all teams
app.get("/teams", (req, res) => {
  sql = "SELECT * FROM TEAMS";
  try {
    // const queryObject = url.parse(req.url, true).query; // query parameters
    // if (queryObject.field && queryObject.type) sql += ` WHERE ${queryObject.field} LIKE '%${queryObject.type}%'`
    db.all(sql, [], (err, rows) => {
      if (err) return res.json({ status: 300, success: false, error: err });

      if (rows.length < 1) return res.json({ status: 300, success: false, error: "No match" });
      console.log('returned all teams!');
      return res.json({
        status: 200,
        data: rows,
        success: true,
      });
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});

// get all player team data
app.get("/playersteams", (req, res) => {
  sql = "SELECT * FROM PLAYER_TEAMS";
  try {
    // const queryObject = url.parse(req.url, true).query; // query parameters
    // if (queryObject.field && queryObject.type) sql += ` WHERE ${queryObject.field} LIKE '%${queryObject.type}%'`
    db.all(sql, [], (err, rows) => {
      if (err) return res.json({ status: 300, success: false, error: err });

      if (rows.length < 1) return res.json({ status: 300, success: false, error: "No match" });
      console.log('returned all players teams!');
      return res.json({
        status: 200,
        data: rows,
        success: true,
      });
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});

// get all player teammate data
app.get("/playersteammates", (req, res) => {
  sql = "SELECT * FROM PLAYER_TEAMMATES_TEAMS";
  try {
    // const queryObject = url.parse(req.url, true).query; // query parameters
    // if (queryObject.field && queryObject.type) sql += ` WHERE ${queryObject.field} LIKE '%${queryObject.type}%'`
    db.all(sql, [], (err, rows) => {
      if (err) return res.json({ status: 300, success: false, error: err });

      if (rows.length < 1) return res.json({ status: 300, success: false, error: "No match" });
      console.log('returned all players teammates!');
      return res.json({
        status: 200,
        data: rows,
        success: true,
      });
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});

// get player from playerUrl
app.get("/*players/:letter/:playerURL", (req, res) => {
  sql = "SELECT * FROM PLAYERS";
  if (req.params) {
    sql += ` WHERE URL="/players/${req.params.letter}/${req.params.playerURL}"`;
  }
  try {
    // const queryObject = url.parse(req.url, true).query; // query parameters
    // if (queryObject.field && queryObject.type) sql += ` WHERE ${queryObject.field} LIKE '%${queryObject.type}%'`
    db.all(sql, [], (err, rows) => {
      if (err) return res.json({ status: 300, success: false, error: err });

      if (rows.length < 1) return res.json({ status: 300, success: false, error: "No match" });
      console.log(req.params);
      return res.json({
        status: 200,
        data: rows,
        success: true,
      });
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});


// get teams from player
app.get("/*players/:letter/:playerURL/teams", (req, res) => {
  sql = "SELECT TEAMNAME FROM PLAYER_TEAMS";
  if (req.params) {
    sql += ` WHERE PLAYERURL="/players/${req.params.letter}/${req.params.playerURL}"`;
  }
  try {
    // const queryObject = url.parse(req.url, true).query; // query parameters
    // if (queryObject.field && queryObject.type) sql += ` WHERE ${queryObject.field} LIKE '%${queryObject.type}%'`
    db.all(sql, [], (err, rows) => {
      if (err) return res.json({ status: 300, success: false, error: err });

      if (rows.length < 1) return res.json({ status: 300, success: false, error: "No match" });
      console.log(req.params);
      return res.json({
        status: 200,
        data: rows,
        success: true,
      });
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});

// get teammates from player
app.get("/*players/:letter/:playerURL/teammates", (req, res) => {
  sql = "SELECT TEAMMATEURL, TEAMNAME FROM PLAYER_TEAMMATES_TEAMS";
  if (req.params) {
    sql += ` WHERE PLAYERURL="/players/${req.params.letter}/${req.params.playerURL}"`;
  }
  try {
    // const queryObject = url.parse(req.url, true).query; // query parameters
    // if (queryObject.field && queryObject.type) sql += ` WHERE ${queryObject.field} LIKE '%${queryObject.type}%'`
    db.all(sql, [], (err, rows) => {
      if (err) return res.json({ status: 300, success: false, error: err });

      if (rows.length < 1) return res.json({ status: 300, success: false, error: "No match" });
      console.log(req.params);
      return res.json({
        status: 200,
        data: rows,
        success: true,
      });
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});

// get teammates from team and certain player
app.get("/*players/:letter/:playerURL/:team", (req, res) => {
  sql = "SELECT TEAMMATEURL FROM PLAYER_TEAMMATES_TEAMS";
  if (req.params) {
    sql += ` WHERE PLAYERURL="/players/${req.params.letter}/${req.params.playerURL}"`;
    sql += ` AND TEAMNAME="${req.params.team}"`
  }
  try {
    // const queryObject = url.parse(req.url, true).query; // query parameters
    // if (queryObject.field && queryObject.type) sql += ` WHERE ${queryObject.field} LIKE '%${queryObject.type}%'`
    db.all(sql, [], (err, rows) => {
      if (err) return res.json({ status: 300, success: false, error: err });

      if (rows.length < 1) return res.json({ status: 300, success: false, error: "No match" });
      console.log(req.params);
      return res.json({
        status: 200,
        data: rows,
        success: true,
      });
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});

// NHL API requests

// ping api
app.get("/nhl/api/ping", async (req, res) => {
  try {
    const response = await (await fetch('https://api.nhle.com/stats/rest/ping')).json();
    console.log('ping', response);
    return res.json({
      status: 200,
      data: response,
      success: true,
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});

// get all games
app.get("/nhl/api/games", async (req, res) => {
  try {
    const response = await (await fetch('https://api.nhle.com/stats/rest/en/game')).json();
    console.log('Getting all games');
    return res.json({
      status: 200,
      data: response,
      success: true,
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});

// get data from game
app.get("/nhl/api/games/:game", async (req, res) => {
  try {
    const response = await (await fetch(`https://api-web.nhle.com/v1/gamecenter/${req.params.game}/boxscore`)).json();
    console.log('Getting data from game ', req.params.game);
    return res.json({
      status: 200,
      data: response,
      success: true,
    });
  }
  catch (error) {
    return res.json({
      status: 400,
      success: false,
    });
  }
});

// opens server to requests
app.listen(3000);
