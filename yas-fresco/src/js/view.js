function View() {
  this.initialize.apply(this, _slice.call(arguments));
}
$.extend(View.prototype, {
  initialize: function(object) {
    var options = arguments[1] || {},
      data = {};

    // string -> element
    if ($.type(object) === "string") {
      // turn the string into an element
      object = { url: object };
    }

    // element -> object
    else if (object && object.nodeType === 1) {
      var element = $(object);


      object = {
        element: element[0],
        url: element.attr("href"),
          caption: element.attr("data-fresco-caption"),
	  photo_url: element.attr("data-fresco-photo-url"),
	  title: element.attr("data-fresco-title"),
	  kudu_count: element.attr("data-fresco-kudu-count"),
	  id: element.attr("data-fresco-id"),
	  
        group: element.attr("data-fresco-group"),
        extension: element.attr("data-fresco-extension"),
        type: element.attr("data-fresco-type"),
        options:
          (element.attr("data-fresco-options") &&
            eval("({" + element.attr("data-fresco-options") + "})")) ||
          {}
      };
    }

    if (object) {
      // detect type if none is set
      if (!object.extension) {
        object.extension = detectExtension(object.url);
      }

      if (!object.type) {
        data = getURIData(object.url);
        object._data = data;
        object.type = data.type;
      }
    }

    if (!object._data) {
      object._data = getURIData(object.url);
    }

    if (object && object.options) {
      object.options = $.extend(
        true,
        $.extend({}, options),
        $.extend({}, object.options)
      );
    } else {
      object.options = $.extend({}, options);
    }
    // extend the options
    object.options = Options.create(object.options, object.type, object._data);

    // extend this with data
    $.extend(this, object);

    return this;
  }
});
