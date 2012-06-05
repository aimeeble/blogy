$('body').ready(function() {
   /* Cache some elements */
   var win = $(window);
   var elSide = $('#sidebar_div');
   var elBar = $('#fixedbar');
   var elTitle = $('#blog_title');
   var elPadTitle = $('#padtitle');
   var debug = $('#debug');
   var elPadBar = $('#pad1');

   var elBarTop = elBar.offset().top;
   var elTitleTop = elTitle.offset().top;

   win.resize(function() {
      if (win.width() < 950) {
         elSide.hide();
      } else {
         elSide.show();
      }
   });

   win.scroll(function() {
      var windowTop = win.scrollTop();
      txt  = 'scrollTop: ' + windowTop + '<br>';
      txt += 'titleTop: ' + elTitleTop + '<br>';
      txt += 'barTop:' + elBarTop + '<br>';
      debug.html(txt);

      elBar.toggleClass('sticky', windowTop > elBarTop);
      elPadBar.toggleClass('sticky', windowTop > elBarTop);

      elTitle.toggleClass('sticky', windowTop > elTitleTop);
      elPadTitle.toggleClass('sticky', windowTop > elTitleTop);
   });
});
