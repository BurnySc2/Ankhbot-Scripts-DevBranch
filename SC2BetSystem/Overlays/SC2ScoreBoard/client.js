/*
###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
*/

if (window.WebSocket) {
  //---------------------------------
  //  Variables
  //---------------------------------
  //  Connection Information
  var serviceUrl = 'ws://127.0.0.1:3337/streamlabs';
  socket = null;
  var reconnectIntervalMs = 10000;

  var hideOverlayAfterClosing = false;
  var showWinnerForSec = 3000;
  var setShowWinnerDuration = false;
  var betHidden = false;

  var player1Race;
  var player2Race;

  var audioStart;
  var audioVictory;
  var audioDefeat;

  if (typeof API_Key === 'undefined') {
    $('body').html(
      'ERROR: No API Key found!<br/>Rightclick on the SC2BetSystem script in Chatbot and select "Insert API Key"'
    );
    $('body').css({
      'font-size': '20px',
      color: '#ff8080',
      'text-align': 'center'
    });
  }

  function Connect() {
    socket = new WebSocket(serviceUrl);

    socket.onopen = function() {
      var auth = {
        author: 'Brain',
        website: 'http://www.twitch.tv/wellbrained',
        api_key: API_Key,
        events: [
          'EVENT_BET_START',
          'EVENT_BET_END',
          'EVENT_BET_UPDATE',
          'EVENT_BET_ABORT',
          'EVENT_BET_WIN',
          'EVENT_BET_LOSE',
          'EVENT_INIT_THEME',
          'EVENT_BET_SHOW'
        ]
      };
      socket.send(JSON.stringify(auth));
      console.log("Theme 'SC2ScoreBoard' Connected");
    };

    socket.onmessage = function(message) {
      var jsonObject = JSON.parse(message.data);

      if (jsonObject.event == 'EVENT_BET_START') {
        StartBet(jsonObject.data);
      } else if (jsonObject.event == 'EVENT_BET_END') {
        if (hideOverlayAfterClosing) {
          HideBet();
        }
      } else if (jsonObject.event == 'EVENT_BET_UPDATE') {
        UpdateBet(jsonObject.data);
      } else if (jsonObject.event == 'EVENT_BET_ABORT') {
        CloseBet();
      } else if (jsonObject.event == 'EVENT_BET_WIN') {
        StreamerWins();
      } else if (jsonObject.event == 'EVENT_BET_LOSE') {
        StreamerLoses();
      } else if (jsonObject.event == 'EVENT_BET_SHOW') {
        console.log('DevEvent - Showing Bet');
        ShowBet();
      }
    };
    socket.onerror = function(error) {
      console.log('Error: ' + error);
    };

    socket.onclose = function() {
      console.log('Connection Closed!');
      HideBet();
      socket = null;
      setTimeout(function() {
        connectWebsocket();
      }, 5000);
    };
  }

  Connect();

  function StartBet(data) {
    var jsonObject = JSON.parse(data);
    console.log('Start new Bet');
    console.log(jsonObject);

    if (jsonObject.enabledSounds) {
      SetSounds(jsonObject);
    } else {
      audioStart = null;
      audioVictory = null;
      audioDefeat = null;
    }

    hideOverlayAfterClosing = jsonObject.hideAfterBetClosed;
    if (!setShowWinnerDuration) {
      // Set duration timer for winner
      setShowWinnerDuration = true;
      showWinnerForSec = jsonObject.durationShowWinner;
    }

    player1Race = jsonObject.race1;
    player2Race = jsonObject.race2;

    $('#player1').addClass(jsonObject.race1);
    $('#player2').addClass(jsonObject.race2);

    $('#player1').html(`<div id="p1Name">${jsonObject.player1}</div>`);
    $('#player2').html(`<div id="p2Name">${jsonObject.player2}</div>`);

    if (jsonObject.capitalizeNames) {
      $('#p1Name').css('text-transform', 'uppercase');
      $('#p2Name').css('text-transform', 'uppercase');
    }

    $('#p1Label').text(`${jsonObject.chatCmdWin}`);
    $('#p2Label').text(`${jsonObject.chatCmdLose}`);

    if (jsonObject.isPercentageBased) {
      $('#p1BetBox').html(`${jsonObject.totalWin} %`);
      $('#p2BetBox').html(`${jsonObject.totalLose} %`);
    } else {
      $('#p1BetBox').html(`${jsonObject.totalWin}`);
      $('#p2BetBox').html(`${jsonObject.totalLose}`);
    }

    if (audioStart != null) {
      audioStart.play();
      console.log('Start sound played');
    }
    ShowBet();
  }

  function UpdateBet(data) {
    var jsonObject = JSON.parse(data);
    console.log('Bet was updated');
    console.log(jsonObject);

    if (jsonObject.isPercentageBased) {
      $('#p1BetBox').html(`${jsonObject.totalWin} %`);
      $('#p2BetBox').html(`${jsonObject.totalLose} %`);
    } else {
      $('#p1BetBox').html(`${jsonObject.totalWin}`);
      $('#p2BetBox').html(`${jsonObject.totalLose}`);
    }
  }

  function StreamerWins() {
    console.log('Streamer won');
    // When hidden add a second for the FadeIn Animation
    if (betHidden) {
      ShowBet();
      showWinnerForSec = showWinnerForSec + 1000;
    }

    if (audioVictory != null) {
      audioVictory.play();
      console.log('Victory sound played');
    }

    $('#p1Name').addClass('winner animated pulse infinite');
    setTimeout(function() {
      CloseBet();
    }, showWinnerForSec);
  }

  function StreamerLoses() {
    console.log('Streamer lost');
    // When hidden add a second for the FadeIn Animation
    if (betHidden) {
      ShowBet();
      showWinnerForSec = showWinnerForSec + 1000;
    }

    if (audioDefeat != null) {
      audioDefeat.play();
      console.log('Defeat sound played');
    }

    $('#p2Name').addClass('winner animated pulse infinite');
    setTimeout(function() {
      CloseBet();
    }, showWinnerForSec);
  }

  function ShowBet() {
    console.log('Show Bet');
    var tl = new TimelineLite();
    tl.fromTo('#container', 2, { top: -75 }, { top: 0 });
  }

  function HideBet() {
    console.log('Hide Bet');
    var tl = new TimelineLite();
    tl.fromTo('#container', 2, { top: 0 }, { top: -75 });
    betHidden = true;
  }

  function CloseBet() {
    console.log('Close Bet completely');

    HideBet();

    setShowWinnerDuration = false;

    $('#p1Name').removeClass('winner animated pulse infinite');
    $('#p2Name').removeClass('winner animated pulse infinite');

    $('#player1').removeClass(player1Race);
    $('#player2').removeClass(player2Race);
  }

  function SetSounds(data) {
    var audioPath = '../../Sounds/';
    console.log('SetSounds' + data);

    if (data.soundStart != '') {
      audioStart = new Audio(audioPath + data.soundStart);
      console.log(data.volumeStart * 0.01);
      audioStart.volume = data.volumeStart * 0.01;
    }
    if (data.soundVictory != '') {
      audioVictory = new Audio(audioPath + data.soundVictory);
      audioVictory.volume = data.volumeVictory * 0.01;
    }
    if (data.soundDefeat != '') {
      audioDefeat = new Audio(audioPath + data.soundDefeat);
      audioDefeat.volume = data.volumeDefeat * 0.01;
    }
    console.log('Sounds set');
  }
}
