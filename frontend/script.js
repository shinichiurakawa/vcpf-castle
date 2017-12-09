var reload_me = function () {
  setTimeout(() => {
    window.location.reload();
  }, 10000);
};

var setCastle = function (castle, wall, garden) {
  $(".castle").css("background-image", 'url("images/1_' + castle + '.png")');
  $(".wall").css("background-image", 'url("images/2_' + wall + '.png")');
  $(".garden").css("background-image", 'url("images/3_' + garden + '.png")');
};

var rand = function (min, max) {
  return Math.floor(Math.random() * (max + 1 - min)) + min;
};

var wait_one_sec = function(){
  return new Promise(function(resolve, reject){
    setTimeout(() => {
      resolve();
    }, 1000);
  });
}

var main = function () {
  console.log("main");
  // setInterval(() => {
  //   setCastle(rand(1, 3), rand(1, 3), rand(1, 3));
  // }, 1000);
  setCastle(1, 1, 1);
  wait_one_sec()
    .then(function () {
      setCastle(1, 1, 2);
    })
    .then(wait_one_sec)
    .then(function () {
      setCastle(1, 2, 1);
    })
    .then(wait_one_sec)
    .then(function () {
      setCastle(1, 2, 2);
    })
    .then(wait_one_sec)
    .then(function () {
      setCastle(2, 2, 2);
    })
    .then(wait_one_sec)
    .then(function () {
      setCastle(2, 3, 2);
    })
    .then(wait_one_sec)
    .then(function () {
      setCastle(3, 3, 3);
    })
    .then(wait_one_sec)
};

$(function () {
  main();

  reload_me();
});