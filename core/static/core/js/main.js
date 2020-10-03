//navbar fading
$(document).ready(function () {
  /*
  // Transition effect for navbar 
  $(window).scroll(function () {
    // checks if window is scrolled more than 500px, adds/removes solid class
    if ($(this).scrollTop() > 100) {
      $('.navbar').addClass('transparent');
    } else {
      $('.navbar').removeClass('transparent');
    }
  });
  */


  $(".ask").on('click', function () {
    var what = $(this).data("what");
    var href = $(this).data("href");
    bootbox.confirm({
      message: what,
      buttons: {
        cancel: {
          label: "No"
        },
        confirm: {
          label: "Yes"
        }
      },
      callback: function (result) {
        if (result) {
          window.location.href = href;
        }
      }
    });
  });




  //social buttons for sharing photos

  $(".facebook").click(function () {
    window.location = "https://www.facebook.com/sharer/sharer.php?u=" + pathname;
  });

  $(".twitter").click(function () {
    window.location = "https://twitter.com/intent/tweet?text=Check out this photo on Your African Safari! "
      + pathname;
  });

  $(".pinterest").click(function () {
    window.location = "//pinterest.com/pin/create/link/?url=" + pathname
      + "&description=Next%20stop%3A%20Pinterest";
  });

  $(".reddit").click(function () {
    window.location = "https://www.reddit.com/submit?url=" + pathname
      + "&title=Amazing picture from Your African Safari";
  });


  //shadow to animal cards
  $(".card.animal").hover(
    function () {
      $(this).addClass('shadow-lg').css('cursor', 'pointer');
    }, function () {
      $(this).removeClass('shadow-lg');
    }
  );
  //adds carousel
  (function ($) {
    "use strict";
    // manual carousel controls
    $('.next').click(function () { $('.carousel').carousel('next'); return false; });
    $('.prev').click(function () { $('.carousel').carousel('prev'); return false; });
  })(jQuery);
  $(".top-search-button").click(function (e) {
    $(".search-toggle").toggleClass("d-none");
    $(".form-search").toggleClass("form-search-expanded");
    $(".search-text").focus();
    return false;
  });
  $(".search-text").blur(function () {
    $(".search-toggle").toggleClass("d-none");
    $(".form-search").toggleClass("form-search-expanded");
  });
  $(".btn-close-search").click(function () {
    $(".search-hide").removeClass("d-none");
    $(".search-show").addClass("d-none");
  });
});

var pathname = window.location.href


$(".dropdown-menu").hover(function () {
  if ($(window).width() >= 768) {
    $('.dropdown-item.carat-hover').not(this).removeClass('dropdown-toggle');
    $(this).prev('a').addClass('dropdown-toggle');
  }
});

$('.carat-hover').hover(function () {
  if ($(window).width() >= 768) {
    $('.dropdown-item.carat-hover').not(this).removeClass('dropdown-toggle');
    $(this).addClass('dropdown-toggle');
  }
});



function lockScroll() {
  if ($('body').hasClass('lock-scroll')) {
    $('body').removeClass('lock-scroll');
  }
  else {
    $('body').addClass('lock-scroll');
  }
}
function redirect(url) {
  window.location = url;
}

$("#top-search").keydown(function (event) {
  var keycode = (event.keyCode ? event.keyCode : event.which);
  if (keycode == '13') {
    event.preventDefault();
    search();
    return false;
  }
});

function search() {
  var query = $("#top-search").val().toLowerCase();
  if (query == "") {
    return false;
  }
  redirect("/search/" + encodeURI(query));
}

$(function () {
  $('[data-toggle="popover"]').popover()
})
$(document).ready(function () {
  $('[data-toggle="tooltip"]').tooltip();
});


function countChar(val, target, total) {

};

$(".countchars").keydown(function (e) {
  const len = $(this).val().length;
  const total = $(this).data('total')

  if (len >= total) {
    $($(this).data('target')).text(total - len);
    $(this).val($(this).val().substring(0, total));
    e.preventDefault();
    return false
  } else {
    $($(this).data('target')).text(total - len);
    return true
  }
})


$(".close_cookie").click(function () {
  Cookielaw.createCookielawCookie();
  $("#cookie-alert").alert('close')
  return true
});

// $(".datatable").dataTable();


$.validator.addMethod('validUrl', function (value, element) {
  var url = $.validator.methods.url.bind(this);
  return url(value, element) || url('http://' + value, element);
}, 'Please enter a valid URL');


$(".int").keydown(function (event) {
  console.log(event.keyCode)
  // Allow only backspace and delete
  if (event.keyCode == 46 || event.keyCode == 8) {
    // let it happen, don't do anything
  }
  else {
    // Ensure that it is a number and stop the keypress
    if (event.keyCode < 48 || event.keyCode > 57) {
      event.preventDefault();
    }
  }
});



$(".phone").keydown(function (event) {
  console.log(event.keyCode)
  // Allow only backspace and delete
  if (event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 187) {
    // let it happen, don't do anything
  }
  else {
    // Ensure that it is a number and stop the keypress
    if (event.keyCode < 48 || event.keyCode > 57) {
      event.preventDefault();
    }
  }
});




function page(page_num) {
  // Construct URLSearchParams object instance from current URL querystring.
  var queryParams = new URLSearchParams(window.location.search);
  // Set new or modify existing parameter value. 
  queryParams.set("page", page_num);
  // Replace current querystring with the new one.
  location.href = "?" + queryParams.toString()
  return false
}

const animated = document.querySelector('.fa-nav-heart');
animated.onanimationend = () => {
  animated.classList.remove('fa-beat');
};


function add_fav(element, id, where){
  var add_url = '';
  var delete_url = '';
  if(where == 'operator'){
    add_url = '/add_operator_fav/'
    delete_url = '/delete_operator_fav/'
  }else{
    add_url = '/add_itinerary_fav/'
    delete_url = '/delete_itinerary_fav/'
  }
  var $counter = $('.far.fa-stack-1x.counter.fav-counter')
  const ele = $(element)
  const is_fav = ele.hasClass('fas')
  if (!is_fav) {
    $(".fa-nav-heart").addClass('fa-beat')
    $.get(add_url + id + '/', null, function (res) {
      if (res['status'] == 'ok') {
        $counter.text(res['count'])
        ele.addClass('fas')
      } else {
        $.notify({
          message: res['message']
        }, {
          placement: {
            from: "top",
            align: "right"
          },
          type: 'danger'
        });
      }

    })
  } else {
    $(".fa-nav-heart").addClass('fa-beat');
    $.get(delete_url + id + '/', null, function (res) {
      if (res['status'] == 'ok') {
        $counter.text(res['count'])
        ele.removeClass('fas')
      } else {
        $.notify({
          message: res['message']
        }, {
          placement: {
            from: "top",
            align: "right"
          },
          type: 'danger'
        });
      }
    })
  }
}

function add_tour_operator_fav(element, idTP) {
  add_fav(element, idTP, 'operator');
  return false
}


function add_tour_package_fav(element, idTP) {
  add_fav(element, idTP, 'package');
  return false
}

