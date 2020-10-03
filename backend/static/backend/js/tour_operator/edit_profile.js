
$("input[name=country_indexes]").change(function (e) {
    update()
})

$("input[name=parks]").change(function (e) {
    update()
})

function compare_parks(a, b) {
    const park_a = parks_json.find(o => parseInt(o['id']) == parseInt(a.value));
    const park_b = parks_json.find(o => parseInt(o['id']) == parseInt(b.value));
    if (park_a['name'] < park_b['name']) {
        return -1;
    }
    if (park_a['name'] > park_b['name']) {
        return 1;
    }
    // a must be equal to b
    return 0;
}

function update() {
    var actives = []
    $("input[name=country_indexes]:checked").each(function () {
        actives.push($(this).val())
    });
    if (actives.length == 0) {
        $("#div_id_parks").addClass("d-none")
        $('.select2_parks option').remove()
        return
    }

    $("#div_id_parks").removeClass("d-none")
    var all_selected_parks = []
    for (i = 0; i < actives.length; i++) {
        parks = countries_json.filter(
            function (country) {
                return country.id == actives[i]
            })[0]['parks'];
        all_selected_parks.push(...parks)
    }

    for (i = 0; i < parks_json.length; i++) {
        const park = parks_json[i]
        const id = park['id']
        const name = park['name']

        if (all_selected_parks.includes(id)) {
            //add it to the checkboxes

            $("input[name=parks][value=" + id + "]").parents('.form-check').removeClass('d-none')
            //add it to the select2 s
            //var newOption = new Option(name, id, false, false);
            //$('.select2_parks').append(newOption)
        } else {
            //remove it from the checkboxes
            $("input[name=parks][value=" + id + "]").parents('.form-check').addClass('d-none')
            $("input[name=parks][value=" + id + "]").parents('.form-check').find('input').prop('checked', false)
            //remove it from the select2 s
            ///$('.select2_parks option[value=' + id + ']').remove()
        }
    }

    //select2
    var items = $('input[name=parks]:checked')
    items_sorted = items.sort(compare_parks)

    var selects = $('.select2_parks')
    selects.each(function (k, select) {
        var select = $(this)
        var options = select.find('option')
        if (items_sorted.length != 0) {
            items_sorted.each(function (k, item) {
                var exists = false
                options.each(function (k, option) {
                    if (option.value == item.value) {
                        exists = true
                    }
                });
                if (!exists) {
                    const park = parks_json.find(o => parseInt(o['id']) == parseInt(item.value));
                    var newOption = new Option(park['name'], item.value, false, false);
                    select.append(newOption)
                }
            });
            options.each(function (k, option) {
                var exists = false
                items.each(function (k, item) {
                    if (option.value == item.value) {
                        exists = true
                    }
                });
                if (!exists) {
                    select.find('option[value=' + option.value + ']').remove()
                }
            });
        }
    });

}
$('.maxlen').maxlength({
    threshold: 1,
    showOnReady: true,
    zIndex: 1,
    appendToParent: true,
    alwaysShow: true,
    warningClass: "badge bg-transparent-50 bg-army-green badge-success",
    limitReachedClass: "badge badge-danger"
});

$(document).ready(function () {
    update();

    //loading
    $(".loading").addClass('d-none')
    $(".loaded").removeClass('d-none')
    $('.maxlen').trigger('maxlength.reposition');
    $(".profileform").validate({
        highlight: function (element, errorClass, validClass) {
            $(element).addClass("is-invalid");
        }, unhighlight: function (element, errorClass, validClass) {
            $(element).removeClass("is-invalid");
        },

    });
})


$("input, textarea").keydown(function () {
    clearError($(this))
});
$("input, textarea").change(function () {
    clearError($(this))
});
function clearError(ele) {
    ele.parents(".form-group").find(".desc_error").remove()
    ele.parents(".form-group").removeClass('error')
    ele.removeClass("input-error")
}


$(".profileform").submit(function (e) {
    var errors = false
    $(".alert-form").addClass('d-none')
    $(".form-group").removeClass('error')
    $(".desc_error").remove()
    $("div").removeClass('error')
    $("input").removeClass("input-error")

    //parks
    var item = $('input[name=parks]:checked')
    if (item.length == 0) {
        errors = 'Please select at least a park'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_parks").append(error_div)
        $("#div_id_parks").addClass('error')
    }
    //country
    var item = $('input[name=country_indexes]:checked')
    if (item.length == 0) {
        errors = 'Please select at least a country'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_country_indexes").append(error_div)
        $("#div_id_country_indexes").addClass('error')
    }

    if (errors) {
        $(".alert-form").html('Please check the errors')
        $(".alert-form").removeClass('d-none')
        e.preventDefault()
        return false
    }
    return true
})
