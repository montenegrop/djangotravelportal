var container = [];
$('#gallery').find('figure').each(function () {
    var $link = $(this).find('.gallery_a'),
        item = {
            src: $link.attr('href'),
            w: $link.data('width'),
            h: $link.data('height'),
            title: $link.data('caption')
        };
    container.push(item);
});

// Define click event on gallery item
$('.gallery_a').click(function (event) {
    // Prevent location change
    event.preventDefault();
    // Define object and gallery options
    var $pswp = $('.pswp')[0],
        options = {
            index: $(this).data('index'),
            bgOpacity: 0.99,
            showHideOpacity: true
        };
    // Initialize PhotoSwipe
    this.gallery = new PhotoSwipe($pswp, PhotoSwipeUI_Default, container, options);
    this.gallery.init();
});