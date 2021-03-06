#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def template(abstract_dir):

    html="""
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>NIPS 2016 Accepted Papers</title>

<style>
/* CSS */

body {
	margin: 0;
	padding: 0;
	font-family: arial;
	background-color: #F6F3E5;
}
.as {
	font-size: 12px;
	color: #900;
}
.ts {
	font-weight: bold;
	font-size: 14px;
}
.tt {
	color: #009;
	font-size: 13px;
}
h1 {
	font-size: 20px;
	padding: 0;
	margin: 0;
}
#titdiv {
	width: 100%;
	height: 90px;
	background-color: #840000;
	color: white;

	padding-top: 20px;
	padding-left: 20px;

	border-bottom: 1px solid #540000;
}

#maindiv {
	width: 90%;
	padding: 15px;
	margin-left: auto;
	margin-right: auto;

	border-left: solid 1px #D6D3C5;
	border-right: solid 1px #D6D3C5;

	background-color: white;
}

.apaper {
	margin-top: 25px;
	min-height: 300px;
}

.paperdesc {
	float: left;
}

.dllinks {
	float: right;
	text-align: right;
}

#titdiv a:link{ color: white; }
#titdiv a:visited{ color: white; }

#maindiv a:link{ color: #666; }
#maindiv a:visited{ color: #600; }

.t0 { color: #000;}
.t1 { color: #C00;}
.t2 { color: #0C0;}
.t3 { color: #00C;}
.t4 { color: #AA0;}
.t5 { color: #C0C;}
.t6 { color: #0CC;}

.topicchoice {
	border: 2px solid black;
	border-radius: 10px;
	padding: 4px;
	cursor: pointer;
	text-decoration: underline;
}

#explanation {
	background-color: #CFC;
	border-radius: 5px;
	color: black;
	padding: 5px;
	text-align: center;
}

#sortoptions {
	text-align: center;
	padding: 10px;
}

.sim {
	cursor: pointer;
	text-decoration: underline;
}

.abstr {
	cursor: pointer;
	text-decoration: underline;
}

.abstrholder {
	background-color: #DFD;
	border: 1px solid #BDB;
	font-size: 12px;
	padding: 10px;
	border-radius: 5px;
	display: none; /* so that these are hidden initially */
	margin-bottom: 5px;
}

</style>

<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
<script>

// this line below will get filled in with database of LDA topic distributions for top words
// for every paper
LOADDISTS

// this will be filled with pairwise scores between papers
PAIRDISTS

var choices = [0, 0, 0, 1, 1, 0, 0]; // default choices, random...
var similarityMode = 0; // is the user currently looking at papers similar to some one paper?
var similarTo = 0; // the index of query paper

// given choices of topics to sort by, handle user interface stuff (i.e. show selection)
function colorChoices() {
	for(var i=0;i<choices.length;i++) {
		if(choices[i] == 1) {
			$("#tc"+i).css("background-color", "#EFE");
			$("#tc"+i).css("border-color", "#575");
		} else {
			$("#tc"+i).css("background-color", "#FFF");
			$("#tc"+i).css("border-color", "#FFF");
		}
	}
}

// this permutes the divs (that contian 1 paper each) based on a custom sorting function
// in our case, this sort is done as dot product based on the choices[] array
// here we are guaranteed ldadist[] already sums to 1 for every paper
function arrangeDivs() {
	var rtable = $("#rtable");
	var paperdivs = rtable.children(".apaper");

	// normalize choices to sum to 1
	var nn = choices.slice(0); // copy the array
	var ss = 0.0;
	for(var j=0;j<choices.length;j++) { ss += choices[j]; }
	for(var j=0;j<choices.length;j++) { nn[j] = nn[j]/ss; }

	paperdivs.detach().sort(function(a,b) {
		var ixa = parseInt($(a).attr('id').substring(3));
		var ixb = parseInt($(b).attr('id').substring(3));

		if(similarityMode === 1) {
			return pairdists[ixa][similarTo] < pairdists[ixb][similarTo] ? 1 : -1;
		}

		if(similarityMode === 0) {

			// chi-squared kernel for the two histograms
			var accuma = 0;
			var accumb = 0;
			for(var i=0;i<7;i++) {
				var ai= ldadist[ixa][i];
				var bi= ldadist[ixb][i];
				var ci= choices[i];
				accuma += (ai-ci)*(ai-ci)/(ai+ci);
				accumb += (bi-ci)*(bi-ci)/(bi+ci);
			}
			return accuma > accumb ? 1 : -1;

			/*
			// vector distance. These are histograms... but lets pretend they arent
			var accuma = 0;
			var accumb = 0;
			for(var i=0;i<7;i++) {
				var ai= ldadist[ixa][i];
				var bi= ldadist[ixb][i];
				var ci= nn[i];
				accuma += (ai-ci)*(ai-ci);
				accumb += (bi-ci)*(bi-ci);
			}
			return accuma > accumb ? 1 : -1;
			*/

			/*
			// inner product distance
			var accuma = 0;
			var accumb = 0;
			for(var i=0;i<7;i++) {
				accuma += ldadist[ixa][i] * choices[i];
				accumb += ldadist[ixb][i] * choices[i];
			}
			return accuma < accumb ? 1 : -1;
			*/
		}

	});
	rtable.append(paperdivs);
}

// when page loads...
$(document).ready(function(){

	arrangeDivs();
	colorChoices();

	// user clicks on one of the Topic buttons
	$(".topicchoice").click(function() {
		similarityMode = 0; // make sure this is off
		var tcid = parseInt($(this).attr('id').substring(2));
		choices[tcid] = 1 - choices[tcid]; // toggle!

		colorChoices();
		arrangeDivs();
	});

	// user clicks on "rank by tf-idf similarity to this" button for some paper
	$(".sim").click(function() {
		similarityMode = 1; // turn on similarity mode
		for(var i=0;i<choices.length;i++) { choices[i] = 0; } // zero out choices
		similarTo = parseInt($(this).attr('id').substring(3)); // store id of the paper clicked

		colorChoices();
		arrangeDivs();

		// also scroll to top
		$('html, body').animate({ scrollTop: 0 }, 'fast');
	});

	// user clicks on "abstract button for some paper
	$(".abstr").click(function() {
		var pid = parseInt($(this).attr('id').substring(2)); // id of the paper clicked
		var aurl = """ + '"' + abstract_dir + """/" + pid + ".txt";
		var holderdiv = "#abholder" + pid;

		if($(holderdiv).is(':visible')) {

			$(holderdiv).slideUp(); // hide the abstract away

		} else {

			// do ajax request and fill the abstract div with the result
			$.ajax({
	            url : aurl,
	            dataType: "text",
	            success : function (data) {
	                $(holderdiv).html(data);
	                $(holderdiv).slideDown();
	            }
	        });
		}
	});
});

</script>

</head>

<body>

<div id ="titdiv">
<h1>NIPS 2016 papers</h1>
Originally by <a href="https://twitter.com/karpathy">@karpathy</a> updated by <a href="http://finlaymagui.re">Finlay Maguire</a><br/>
Source available on <a href="https://github.com/fmaguire/nipspreview">github</a>
</div>

<div id="maindiv">
<div id="explanation">Below every paper are TOP 100 most-occuring words in that paper and their color is based on LDA topic model with k = 7.<br />
	<div style="font-size: 12px;">(It looks like 0 = ?, 1 = ?, 2 = ?, 3 = ?, 4 = ?, 5 = ?, 6 = ? etc.) </div>
</div>
<div id="sortoptions">
Toggle LDA topics to sort by:
<span class="topicchoice t0" id="tc0">TOPIC0</span>
<span class="topicchoice t1" id="tc1">TOPIC1</span>
<span class="topicchoice t2" id="tc2">TOPIC2</span>
<span class="topicchoice t3" id="tc3">TOPIC3</span>
<span class="topicchoice t4" id="tc4">TOPIC4</span>
<span class="topicchoice t5" id="tc5">TOPIC5</span>
<span class="topicchoice t6" id="tc6">TOPIC6</span>
</div>

<!-- the keyword below will be replaced by content from the python script generatenice.py -->
<div id="rtable">
RESULTTABLE
</div>

</div>

<br /><br /><br /><br /><br /><br />
</body>

</html>"""
    return html
