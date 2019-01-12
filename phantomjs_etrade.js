
var system = require('system');
var args = system.args;

var targetUrl = args[1];
var username = args[2];
var password = args[3];

var steps = [];
var testindex = 0;
var loadInProgress = false;

var webPage = require('webpage');
var page = webPage.create();

page.settings.userAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36';
page.settings.javascriptEnabled = true;
page.settings.loadImages = true;
phantom.cookiesEnabled = true
phantom.javascriptEnabled = true;

page.onConsolMessage = function(msg) {
	//console.log(msg)
};

steps = [
	function() {
		page.open(targetUrl, function(status) {
		});
	},

	function() {
		//console.log('loggin')
		page.evaluate(function(username, password) {
			var names = document.getElementsByName("USER");
			if (names.length != 0) {
				names[0].value = username;
				var names = document.getElementsByName("PASSWORD");
				names[0].value = password;
				var names = document.getElementsByName("REMEMBER_MY_USER_ID");
				names[0].value = "true";
				document.getElementById("log-on-form").submit();
			}
		}, username, password);
	},

	function() {
		//console.log('save');
		var fs = require('fs');
		var result = page.evaluate(function() {
			return document.querySelectorAll("html")[0].outerHTML;
		});
		fs.write('test1.html', result, 'w');
	},

	function() {
		//console.log('accept')
		page.evaluate(function() {
			var names = document.getElementsByTagName("input");
			var i;
			for (i = 0; i < names.length; i++) {
				if (names[i].getAttribute('value') == "Accept") {
					names[i].click();
				}
			}
		});
	},

	function() {
		//console.log('save');
		var fs = require('fs');
		var result = page.evaluate(function() {
			return document.querySelectorAll("html")[0].outerHTML;
		});
		fs.write('test2.html', result, 'w');
	},

	function() {
		var res = page.evaluate(function() {
			var names = document.getElementsByTagName("input");
			var i;
			for (i = 0; i < names.length; i++) {
				if (names[i].getAttribute('type') == "text")
					return names[i].value
			}
		});
		console.log(res)
	},
];

interval = setInterval(executeRequestsStepByStep, 50);

function executeRequestsStepByStep(){
    if (loadInProgress == false && typeof steps[testindex] == "function") {
        //console.log("step " + (testindex + 1));
        steps[testindex]();
        testindex++;
    }
    if (typeof steps[testindex] != "function") {
        //console.log("test complete!");
        phantom.exit();
    }
}

/**
 * These listeners are very important in order to phantom work properly. Using these listeners, we control loadInProgress marker which controls, weather a page is fully loaded.
 * Without this, we will get content of the page, even a page is not fully loaded.
 */
page.onLoadStarted = function() {
    loadInProgress = true;
    //console.log('Loading started');
};
page.onLoadFinished = function() {
    loadInProgress = false;
    //console.log('Loading finished');
};
page.onConsoleMessage = function(msg) {
    //console.log(msg);
};
