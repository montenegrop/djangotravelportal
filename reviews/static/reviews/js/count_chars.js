$(document).ready(function(){

    //count-characters
    (function( $ ){

        $.fn.countChars = function( options ) {  

          var settings = $.extend( {
            'location'         : 'top',
            'background-color' : 'blue'
          }, options);
          return this.each(function() {
              var main = {};
              main.elm = $(this);
              main.textarea = main.elm.find('textarea');
              main.elm_n_max = main.elm.find('.n_max');
              main.elm_n_chars = main.elm.find('.n_chars');

              main.max_chars = main.elm.attr('data-n_max');
              
              var tlength = main.textarea.val().length;
              main.elm_n_chars.text(tlength);

              main.textarea.on('keyup', function(){

              tlength = main.textarea.val().length;

                main.textarea.val(main.textarea.val().substring(0, main.max_chars));
                tlength = main.textarea.val().length;
                main.elm_n_chars.text(tlength);

              });            

          });

        };
      })( jQuery );

      $('.count-chars').countChars();

});//document ready
