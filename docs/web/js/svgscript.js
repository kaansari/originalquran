$description = $(".description");

  $('.enabled').hover(function() {
    $(this).attr("class", "enabled heyo");
    $description.addClass('active');
    $description.html($(this).attr('description'));
  }, function() {
    $description.removeClass('active');
  });

/*
$(document).on('mousemove', function(e){
  
  $description.css({
    left:  e.pageX + 'px',
    top:   e.pageY + 'px'
  });
  
});
*/

$(document).ready(function() {
  $('svg').mousemove(function(event) {
      var offset = $(this).offset();
      var mouseX = event.pageX - offset.left;
      var mouseY = event.pageY - offset.top;

      // Adjust the position to be above the mouse pointer
      var elementHeight = $description.outerHeight();
      var elementWidth = $description.outerWidth();
      var offsetX = $description.outerWidth()*-.5; // Horizontal offset from the pointer
      var offsetY = 10; // Vertical offset above the pointer

      $description.css({
          left: (mouseX + offsetX) + 'px',
          top: (mouseY - elementHeight - offsetY) + 'px'
      });
  });
});
