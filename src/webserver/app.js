var express = require('express');
var bodyParser = require('body-parser');

var app = express();
var router = express.Router();

// pwd
var __dirname = '/home/team9/guseokguseok/src';
var path = __dirname + '/webserver/public/';

// making html code pretty
app.use(bodyParser.urlencoded({ extended: false }));
app.locals.pretty = true;

// setting pages path
router.use(function (req, res, next) {
    console.log("/" + req.method);
    next();
});

router.get("/", function(req, res){
    res.sendFile(path + "main.html");
});

router.get("/test", function(req, res){
    res.sendFile(__dirname + "/webserver/index.html");
});


// use router
app.use("/", router);
app.use(express.static(__dirname + '/webserver'));

/*
app.use("*", function(req, res){
    res.sendFile(path + "404.html");
});
*/

app.listen(8080, function(){
    console.log('Connection 8080!');
});
