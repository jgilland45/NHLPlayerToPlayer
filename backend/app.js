// video: https://www.youtube.com/watch?v=mnH_1YGR2PM&ab_channel=ByteMyke
const express = require("express");
const bodyParser = require("body-parser");

const app = express();
const sqlite = require("sqlite3").verbose();
const url = require("url");

let sql;
const db = new sqlite.Database("nhlPlayers.db", sqlite.OPEN_READWRITE, (err) => {
  if (err) return console.error(err);
});

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

// opens server to requests
app.listen(3000);
