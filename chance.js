var page = require('webpage').create();
var system = require('system');

phantom.outputEncoding = "ISO-8859-2";

if (system.args.length === 1) 
{
	console.log('Try to pass some args when invoking this script!');
	phantom.exit();
}

var page = require('webpage').create();
var url = system.args[1];

page.open(url, function (status) {
    //Page is loaded!
    console.log(page.content);
    phantom.exit();
});

