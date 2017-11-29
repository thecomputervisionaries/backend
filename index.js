var express = require("express");
var http = require('http');
var app = express();

var fs = require("fs");

var multer = require("multer");
var upload = multer({dest: "./uploads"});

var mongoose = require("mongoose");

var server = http.createServer(app);

mongoose.connect('mongodb://localhost:27017/db_id');
var conn = mongoose.connection;
conn.on('error', console.error.bind(console, 'connection error:'));

var gfs;

var Grid = require("gridfs-stream");
Grid.mongo = mongoose.mongo;

var PythonShell = require('python-shell'); 

var options = {
    mode: 'text', 
    pythonPath: '', 
    pythonOptions: ['-u'], 
    scriptPath: '', 
    args: ['b737.jpg']
};

var fs = require('fs'); 

conn.once("open", function(){
	gfs = Grid(conn.db);
	app.get("/", function(req,res){
		//renders a multipart/form-data form
		res.render("home");
	});

	app.get('/i/run_classification', function(req,res) {
		PythonShell.run('classifier.py', options, function(err, results) {
			if (err) throw err; 
			fs.writeFile('predictions.json', results, 'utf-8', function(err) {
				if (err) throw err; 
				res.json(results);				
			})
		})
	});

	//second parameter is multer middleware.
	app.post("/", upload.single("avatar"), function(req, res, next){
		//create a gridfs-stream into which we pipe multer's temporary file saved in uploads. After which we delete multer's temp file.

	    var imagedata = ''

	    res.on('data', function(chunk){
	        console.log("got data");
	        imagedata += chunk
	        console.log(chunk);
	    })		
		
		//pipe multer's temp file /uploads/filename into the stream we created above. On end deletes the temporary file.
		fs.createReadStream("./uploads/" + req.file.filename)
        fs.writeFile("./uploads/"+req.file.originalname, imagedata, 'binary', function(err){
            if (err) throw err
            console.log('File saved.');
			var filename = req.file.filename;

			var address = server.address().address
			var port = server.address().port

			// res.json(options);

			fs.readFile("./uploads/"+req.file.filename, function read(err, data) {
			    if (err) throw err;
				var options = {
				    mode: 'text', 
				    pythonPath: '', 
				    pythonOptions: ['-u'], 
				    scriptPath: '', 
				    args: ["./uploads/"+req.file.filename]
				};

				console.log("about to run python script");
				PythonShell.run('classifier.py', options, function(err, results) {
					if (err) throw err; 
					res.json(results);				
				})   
			});      
        })		
	})
	

	// sends the image we saved by filename.
	app.get("/:filename", function(req, res){
		var readstream = gfs.createReadStream({filename: req.params.filename});
		readstream.on("error", function(err){
			res.send("No image found with that title");
		    });
		readstream.pipe(res);
	    });

	//delete the image
	app.get("/delete/:filename", function(req, res){
		gfs.exist({filename: req.params.filename}, function(err, found){
			if(err) return res.send("Error occured");
			if(found){
			    gfs.remove({filename: req.params.filename}, function(err){
				    if(err) return res.send("Error occured");
				    res.send("Image deleted!");
				});
			} else{
			    res.send("No image found with that title");
			}
		    });
	    });
    });

app.set("view engine", "ejs");
app.set("views", "./views");

server.listen(3000, 'localhost');
server.on('listening', function() {
    console.log('Express server started on port %s at %s', server.address().port, server.address().address);
});