$(".navbar-blog").addClass("active");
$("#query").keydown(function (event) {
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode == '13') {
        search();
    }
});

$("#mobile-submit-btn").click(function (e) {
    e.preventDefault();
    search();
    return false;
});

function search() {
    var query = $("#query").val().toLowerCase();
    if (query == "") {
        return false;
    }
    redirect("/blog/search/" + encodeURI(query));
}