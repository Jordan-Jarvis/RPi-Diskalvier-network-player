
	var istouch = 'ontouchstart' in document.documentElement; // true if touch browser
	
	var eleCtrl = gebi('ctrl');
	var eleList = gebi('list');
	var eleOvr = gebi('ovr');
	var eleOvrCon = gebi('ovrcon');
	
	var eleKbd = gebi('kbd');
	var kbdInp;
	
	var eleNbDisk = gebi('nbdisk');
	var eleButPly = gebi('but_ply');
	var eleButRec = gebi('but_rec');
	var eleButSta = gebi('but_sta');
	var eleButCon = gebi('but_con');
	var eleButRep = gebi('but_rep');
	var eleButDel = gebi('but_del');
	var eleButRen = gebi('but_ren');
	var eleProg = gebi('prog');
	var eleProgWrp = gebi('progwrp');
	var eleRating = gebi('rating');
	var eleBpm = gebi('bpm');
	var eleBpmP = gebi('bpmp');
	var eleBpmM = gebi('bpmm');
	var eleTimeCur = gebi('time_cur');
	var eleTimeTot = gebi('time_tot');
	
	var bpm = 120; // bpm of current song
	var lastBpmClick = 0; // last time we clicked +/- to change bpm so we dont force it while we adjust
	var duration = 0; // duration of current song in seconds
	var elapsed = 0; // COUNTER of elapsed seconds in current song
	var elapsedCompensation = 0; // when making a request to update player status, add half the time of the request to elasped
	var timerStatus = 0; // 1=playing ; 2=recording ; so that we update elapsed/duration and progress bar
	
	var updateIn = 0; // count down timer so we update entire interface content every N/10 seconds
	
	
	// ==================== SHORTCUT FUNCTIONS : ====================
	
	// Shortcut to function getElementById
	function gebi(d){
		return document.getElementById(d);
	}
	
	// Substitute of function addEventListener for browsers that dont support it
	function ael(ele, evt, func){
		if(!ele) return;
		if( ele.addEventListener ){
			ele.addEventListener(evt, func, true);
		}else{
			ele.attachEvent('on'+evt, func);
		}
	}

	function parseResponse(r) {
		// Parse an AJAX response and call other functions to update the interface
		// r : response body

		try{
			var json = JSON.parse(r); 
			for (obj in json)
			{
				console.log(json[obj][0])
				// PLAYER STATUS :
				if( json[obj][0] == 'PLAYER' ){
					updatePlayer(json[obj]);
					updateIn = 30;
					
				// PLAYLIST CONTENT :
				}else if( json[obj][0] == 'PLAYLIST' ){
					updatePlayList(json[obj]);
					updateIn = 30;
					
				// PUT SOME CONTENT IN THE OVERLAY & OPEN IT :
				}else if( json[obj][0] == 'OVERLAY' ){

					openOverlay(data[1]);
					
				// PUT AN ELEMENT IN FOCUS (typically input when renaming) :
				}else if( json[obj][0] == 'FOCUS' ){
					
					var ele = document.getElementById(data[1]);
					if(ele) setTimeout( function(e){ e.focus() }, 100, ele );
					
				// OPEN THE KEYBOARD TO TYPE IN AN INPUT :
				}else if( json[obj][0] == 'KEYBOARD' ){
					
					setTimeout( function(id){ openKeyboard(id) }, 100, data[1] );
					
				}
			}
		}
		catch{

			var lines = r.split('\n');

			for( var i=0, imax=lines.length ; i<imax ; i++ ){
				
				var data = lines[i].split('\t');
				console.log(lines);
				// PLAYER STATUS :
				if( data[0] == 'PLAYER' ){
					updatePlayer(data);
					updateIn = 30;
					
				// PLAYLIST CONTENT :
				}else if( data[0] == 'PLAYLIST' ){
					updatePlayList(data);
					updateIn = 30;
					
				// PUT SOME CONTENT IN THE OVERLAY & OPEN IT :
				}else if( data[0] == 'OVERLAY' ){
					console.log(lines[1]);
					openOverlay(lines[1]);
					
				// PUT AN ELEMENT IN FOCUS (typically input when renaming) :
				}else if( data[0] == 'FOCUS' ){
					
					var ele = gebi(data[1]);
					if(ele) setTimeout( function(e){ e.focus() }, 100, ele );
					
				// OPEN THE KEYBOARD TO TYPE IN AN INPUT :
				}else if( data[0] == 'KEYBOARD' ){
					
					setTimeout( function(id){ openKeyboard(id) }, 100, data[1] );
					
				}
				
			}
		}
		// Each line wants to update a certain thing in the interface (e.g. player status, progress bar, playlist)

			
			
		}
		
	
	// Create an AJAX object
	function newAjax(){
		if( window.XMLHttpRequest ){ // IE7+, Firefox, Chrome, Opera, Safari
			return new XMLHttpRequest();
		}else{ // IE6, IE5
			return new ActiveXObject('Microsoft.XMLHTTP');
		}
	}
	
	// ==================== SEND REQUEST TO BACK-END : ====================
	function sendRequest(cmd, e, s){
		// cmd : command string to send (e.g. 'play-stop')
		// e : OPTIONAL element to put loading icon into and restore as soon as request received
		// s : make sync request (wait for response)
		
		var ajax = newAjax();
		if( ajax ){
			
			var eClass;
			var eColor;
			if(e){
				eClass = e.className;
				e.className += ' loading';
				eColor = e.style.color;
				e.style.color = 'rgba(255,255,255,0)';
				if( eClass == 'loading' ) eClass = '';
			}
			
			var requestStart = ( new Date() ).getTime();
			
			// Syncronous :
			if( s ){
				
				ajax.open('GET', '/ajax/'+cmd, false);
				ajax.send();
				
				if(typeof eClass !== 'undefined'){
					e.className = eClass;
					e.style.color = eColor;
				}
				
				// SUCCESS :
				if( ajax.status==200 ){
					
					var requestEnd = ( new Date() ).getTime();
					elapsedCompensation = (requestEnd - requestStart) / 2000;
					if( elapsedCompensation > 3 ) elapsedCompensation = 0.15; // to fix a potential bug
					
					// Each line in response updates something.
					// e.g. 'PLAYER	but_rec=stop' updates element 'but_rec' to set class to 'stop'
					//      the next line may update the play list content e.g. in this same response.
					
					parseResponse(ajax.responseText);
					
				// FAILED :
				}else if( ajax.responseText != '' ){
					
					alert(ajax.responseText);
					
				}
				
			// Asyncronous :
			}else{
				
				ajax.open('GET', '/ajax/'+cmd, true);
				ajax.send();
				
				ajax.onreadystatechange=function(){
					if( ajax.readyState==4 ){
						
						if(typeof eClass !== 'undefined'){
							e.className = eClass;
							e.style.color = eColor;
						}
						
						// SUCCESS :
						if( ajax.status==200 ){
							
							var requestEnd = ( new Date() ).getTime();
							elapsedCompensation = (requestEnd - requestStart) / 2000;
							if( elapsedCompensation > 3 ) elapsedCompensation = 0.15; // to fix a potential bug
							
							// Each line in response updates something.
							// e.g. 'PLAYER	but_rec=stop' updates element 'but_rec' to set class to 'stop'
							//      the next line may update the play list content e.g. in this same response.
							
							parseResponse(ajax.responseText);
							
						// FAILED :
						}else if( ajax.responseText != '' ){
							
							alert(ajax.responseText);
							
						}
						
					}
				}
				
			}
			
		}
	}
	
	
	// ==================== UPDATE INTERFACE FROM AJAX RESPONSE : ====================
	
	function updatePlayList(data){
		// data : array of playlist new content
		// NOTE: only updated when the list has changed (e.g. after recording or delete)
		//       because we loose the selection and scrolling position
		var playlistHtml = '';


		// Each tab-seperated element is a song :
		for( var i=1; i < data.length; i++ )
		{
			

			// [0] : base filename 'YYYYMMDD-HHMMSS'
			// [1] : date 'YYYY-MM-DD'
			// [2] : time of day 'H.MM pm'
			// [3] : duration in seconds
			// [4] : bpm original
			// [5] : bpm new
			// [6] : Song Title
			// [7] : Rating (0-5, 0 means not-rated)
			// [8] : 1 if selected
			// [9] : 1 if MIDI file download
			
			playlistHtml += '<div class='+( data[i][8] == '1' ? '\"song sel\"' : 'song' )+' id=\"'+data[i][0]+'\" onclick=\"songSelect(this)\" data-d=\"'+data[i][3]+'\" data-bo=\"'+data[i][4]+'\" data-bn=\"'+data[i][5]+'\" data-t=\"'+data[i][6]+'\" data-r=\"'+data[i][7]+'\"><div>'+data[i][1]+'</div><div>'+data[i][2]+'</div><div>'+secToTime(data[i][3])+'</div><div>'+data[i][4]+(data[i][5] != data[i][4] ? ' > '+data[i][5] : '')+' bpm</div><div>'+data[i][6]+'</div><div class=star'+data[i][7]+'></div>';
			
			if( data[i][9] == '1' ) playlistHtml += '<a href=\"/dl/'+data[i][6]+'\" target=_blank>MIDI file</a>';
			
			playlistHtml += '</div>';
			
		}
		
		eleList.innerHTML = playlistHtml;
		
	}
	
	
	// ==================== PLAYER STATUS : ====================
	
	function updatePlayer(data){
		// data : array of things to update
		// [1] : setIdClass : array of ids to change classes and therefore styles for.
		// [2] : progress
		// [3] : timeElapsed
		// [4] : bpm
		// [5] : total Time of song
		// [6] : timer enable
		// [7] : folder available
		if (data[1].length > 0)
		{
			for (var i = 0; i < data[1].length; i++)
			{
				var id = data[1][i][0];
				var cls = data[1][i][1];
				var ele = gebi(id);
				if(ele && ele.className != cls)
				{
					ele.className = cls;
				}
			}
		}
		if (data[2] != 0)
		{
			if(timerStatus == 0)
			{
				console.log(data[2]);
				eleProg.style.width = data[2];
			}
		}
		eleTimeCur.innerHTML = data[3];
		elapsed = data[3];
		duration = data[5];
		if (data[4] > 0)
		{
			if( lastBpmClick < new Date().getTime() - 5000 ){
				eleBpm.innerHTML = data[4];
			}
		}
		if( data[5] == 0 ){
			eleTimeTot.innerHTML = '';
		}else{
			eleTimeTot.innerHTML = secToTime(data[5]);
		}
		timerStatus = data[6];
		eleNbDisk.innerHTML = data[7];		
	}
	
	
	// ==================== PLAYLIST : ====================
	

	
	// ==================== OVERLAY : ====================
	
	function openOverlay(data){
		// data : html content to put in #ovrcon

		ovrcon.innerHTML = data;
		ovr.className = 'visible';
		
	}
	
	// ==================== KEYBOARD : ====================
	
	function openKeyboard(input_id){
		// input_id : element id of the input to type in
		
		kbdInp = gebi(input_id);
		if( !kbdInp ) return;
		
		var inpLength = kbdInp.value.length;
		kbdInp.selectionStart = inpLength;
		kbdInp.selectionEnd = inpLength;
		
		eleKbd.className = 'visible';
		
	}
	
	function songSelect(e){
		// Clicking a song in the playlist
		// e : element clicked
		
		lastBpmClick = 0;
		
		var ds = e.dataset;
		var fn = songToFilename(e.id, ds.t, ds.bo, ds.bn, ds.r);
		
		sendRequest('selectsong-'+e.id);
		
		return 1;
	}
	
	function songToFilename(b,t,bo,bn,r){
		// Return a MIDI filename for a song
		// b  : base filename 'YYYYMMDD-HHMMSS'
		// t  : song title
		// bo : bpm original
		// bn : bpm new
		// r  : rating
		
		return b
			+'-'+t.toLowerCase().replace(/ /g,'-')
			+'-'+( bn != '' ? bn : bo )
			+'-'+r+'.mid';
		
	}
	
	function secToTime(s){
		// Return a time '1:59' from seconds 119
		
		s = Math.round( parseFloat(s) );
		var min = Math.floor(s / 60);
		var sec = s - min*60;
		if(sec < 10) sec = '0'+sec;
		
		return(min+':'+sec);
		
	}
	
	
	if( istouch ){
		
		ael( eleButPly, 'touchstart', pressPlay );
		ael( eleButRec, 'touchstart', pressRec );
		ael( eleButSta, 'touchstart', pressStart );
		ael( eleButRep, 'touchstart', setconfRepeat );
		ael( eleButCon, 'touchstart', setconfContinue );
		ael( eleButDel, 'touchstart', pressDel );
		ael( eleButRen, 'touchstart', pressRen );
		
		ael( eleBpmP, 'touchstart', function(){ bpmClick(1) });
		ael( eleBpmM, 'touchstart', function(){ bpmClick(-1) });
		ael( eleBpm, 'touchstart', function(){ bpmClick(0) });
		
		ael( eleRating, 'touchstart', ratingClick);
		ael( eleProgWrp, 'touchstart', barClick );
		
	}else{
		
		ael( eleButPly, 'mousedown', pressPlay );
		ael( eleButRec, 'mousedown', pressRec );
		ael( eleButSta, 'mousedown', pressStart );
		ael( eleButRep, 'mousedown', setconfRepeat );
		ael( eleButCon, 'mousedown', setconfContinue );
		ael( eleButDel, 'mousedown', pressDel );
		ael( eleButRen, 'mousedown', pressRen );
		
		ael( eleBpmP, 'mousedown', function(){ bpmClick(1) });
		ael( eleBpmM, 'mousedown', function(){ bpmClick(-1) });
		ael( eleBpm, 'mousedown', function(){ bpmClick(0) });
		
		ael( eleRating, 'mousedown', ratingClick);
		ael( eleProgWrp, 'mousedown', barClick );
		
	}
	
	ael( eleKbd, 'click', kbdPress );
	
	function pressPlay(){
		bpmSend();
		if( eleButPly.className == 'pause' ){
			sendRequest('play-stop', eleButPly);
		}else{
			sendRequest('play-start', eleButPly);
		}
	}
	
	function pressRec(){
		if( eleButRec.className == 'stop' ){
			sendRequest('rec-stop', eleButRec);
		}else{
			sendRequest('rec-start-'+bpm, eleButRec);
		}
	}
	
	function pressStart(){
		bpmSend();
		sendRequest('start', eleButSta);
	}
	
	function setconfRepeat(){
		if( eleButRep.className == 'ena' ){
			sendRequest('setconf/repeat/0', eleButRep);
		}else{
			sendRequest('setconf/repeat/1', eleButRep);
		}
	}
	
	function setconfContinue(){
		if( eleButCon.className == 'ena' ){
			sendRequest('setconf/continue/0', eleButCon);
		}else{
			sendRequest('setconf/continue/1', eleButCon);
		}
	}
	
	function pressDel(){
		sendRequest('del-open', eleButDel);
	}
	
	function pressRen(){
		sendRequest('ren-open', eleButRen);
	}
	
	function bpmClick(x){
		// Clicking + or - to change bpm
		// x : 1=plus -1=minus 0=reset to original
		
		if( x == 0 ){
			bpm = 0;
			lastBpmClick = 0;
			bpmSend(1);
		}else{
			bpm += x;
			eleBpm.innerHTML = bpm;
			lastBpmClick = new Date().getTime();
		}
		
	}
	
	function bpmSend(f){
		// Send BPM to back-end
		// f : force to send right now
		
		// if( lastBpmClick == 0 || !f && new Date().getTime() < lastBpmClick + 1500 ) return; // not time to send yet
		if( !f && lastBpmClick == 0 ) return;
		
		lastBpmClick = 0;
		sendRequest('bpm-'+bpm, false, true);
		
	}
	
	function ratingClick(e){
		
		var clkx = e.pageX || e.touches[0].pageX;
		var clkLeft = clkx - eleRating.getBoundingClientRect().left; // X position in stars png
		var clkWidth = eleRating.clientWidth; // Total width of all 5 stars
		var clkRating = Math.ceil( 5 * clkLeft / clkWidth ); // From 1 to 5
		
		sendRequest('rate-'+clkRating);
		
	}
	
	function barClick(e) {
		// Click/Touch the progress bar so relocate player
		
		var clkx = e.pageX || e.touches[0].pageX;
		var barw = eleProgWrp.clientWidth;
		
		sendRequest('prog-'+clkx+'-'+barw );
		
	}
	
	function kbdPress(v){
		// Pressing a key on the keyboard
		// v : event on #kbd (NOT on the <a> tag of the key)
		
		var e = v.target || v.toElement || v.relatedTarget; // Element clicked
		
		if( e.tagName.toLowerCase() != 'a' ) return false;
		v.preventDefault();
		
		if( !kbdInp ) return false;
		
		var inpVal = kbdInp.value;
		var inpBefore = inpVal.substring(0, kbdInp.selectionStart);
		var inpAfter = inpVal.substring(kbdInp.selectionEnd);
		
		var letter = e.innerHTML;
		
		if( letter == 'SPACE' ){
			letter = ' ';
			
		}else if( letter == 'CLEAR' ){
			letter = '';
			inpBefore = '';
			inpAfter = '';
			
		// Backspace :
		}else if( !letter.match(/^[a-z\d]$/i) ){
			
			if( kbdInp.selectionStart == kbdInp.selectionEnd )
				inpBefore = inpBefore.substring(0, inpBefore.length - 1);
			
			letter = '';
		}
		
		kbdInp.value = inpBefore + letter + inpAfter;
		var pos = (inpBefore + letter).length;
		kbdInp.selectionStart = pos;
		kbdInp.selectionEnd = pos;
		kbdInp.focus();
		
	}
	
	function playerTimer(){
		// Executed by timer to update progress bar position
		
		if( timerStatus == 0 ) return(1);
		
		elapsed += 0.1;
		// Reached end of song :
		if( timerStatus == 1 && elapsed > duration ){
			timerStatus = 0;
			elapsed = 0;
			eleButPly.className = '';
			eleButRec.className = '';
			updateIn = 15;
		}
		
		// Recording :
		if( timerStatus == 2 ){
			eleProg.style.width = '100%';
			
		// Playing :
		}else if( duration > 0 ){
			eleProg.style.width = (100 * elapsed / duration) + '%';
		}else{
			eleProg.style.width = 0;
		}
		
		eleTimeCur.innerHTML = secToTime(elapsed);
		
	}
	setInterval( playerTimer, 100);
	
	
	function updateInterface(){
		// Executed by timer to request interface content regularily.
		// Timer is pushed whenever we receive the content from a request,
		// e.g. pressing play sends a request which get the content in the response so we wont request it again before a while.
		
		updateIn--;
		if( updateIn > 0 ) return;
		
		updateIn = 30;
		sendRequest('get-int');
		
	}
	setInterval( updateInterface, 99);
	
	
	var ww = 0; // Window width
	var wh = 0; // Window height
	var wwPrev = 0; // Previous ww read so we can compare
	var whPrev = 0; // ... wh
	
	function updwin(){
		// Update what depends on window size
		
		ww = window.innerWidth || (document.documentElement && document.documentElement.clientWidth) || document.body.clientWidth;
		wh = window.innerHeight || (document.documentElement && document.documentElement.clientHeight) || document.body.clientHeight;
		if( ww == wwPrev && wh == whPrev ) return;
		
		eleCtrl.style.fontSize = Math.round( (ww + 3.7*wh) / 55 )+'px';
		eleList.style.fontSize = Math.round( (ww + 2.5*wh) / 45 )+'px';
		eleOvr.style.fontSize = Math.round( (ww + 3*wh) / 50 )+'px';
		eleKbd.style.fontSize = Math.round( (ww + 6*wh) / 60 )+'px';
		
		wwPrev = ww;
		whPrev = wh;
		return;
	}
	
	setInterval( updwin, 50);

