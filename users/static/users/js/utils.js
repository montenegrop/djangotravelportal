$(document).ready(function () {

    $(".recent-see-more").click(function () {
        var el = $(this).parent().find('.see_more_hidden_container');

        if (el && el.length) {
            if (el.is(":visible")) {
                el.fadeOut();
                $(this).html("<span>See more</span>");
            } else {
                el.fadeIn();
                $(this).html("<span>See less</span>");
            }
        }
    });

    $(".parks-show-more").click(function () {
        $(".parks-show-more").each(function (i, obj) {
            console.log(obj)
            if ($(obj).hasClass("d-block")) {
                $(obj).removeClass("d-block")
                $(obj).hide();
            } else {
                $(obj).addClass("d-block")
            }
        })

    });

    $(".countries-show-more").click(function () {
        $(".countries-show-more").each(function (i, obj) {
            console.log(obj)
            if ($(obj).hasClass("d-block")) {
                $(obj).removeClass("d-block")
                $(obj).hide();
            } else {
                $(obj).addClass("d-block")
            }
        })

    });


});
