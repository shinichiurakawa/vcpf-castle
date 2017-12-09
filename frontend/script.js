var reload_me = function(){
  setTimeout(() => {
    window.location.reload();
  }, 10000);
}

var main = function(){
  console.log("main");
  $(".sky").css("background-image", 'url("images/1_1.png")');
  $(".castle").css("background-image", 'url("images/2_1.png")');
  $(".wall").css("background-image", 'url("images/3_1.png")');
  $(".garden").css("background-image", 'url("images/4_1.png")');
  // debugger;
}

$(function () {
  main();

  reload_me();
})