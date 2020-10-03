//form validation

$("input, textarea").keydown(function () {
    clearError($(this))
});
$("input, textarea").change(function () {
    clearError($(this))
});
function clearError(ele) {
    ele.parents(".form-group").find(".desc_error").remove()
    ele.parents(".card").find(".desc_error").remove()
    ele.parents(".error").find(".desc_error").remove()
    ele.parents(".form-group").removeClass('error')
    ele.parents(".form-check").removeClass('error')
    ele.parents(".error").removeClass('error')
    ele.removeClass("input-error")
}

$('.submit').click(function (e) {
    $('.submit').addClass('disabled')
    $('.submit').html('loading...')
    var errors = false
    var is_edit = $('input[name=slug]').length == 1;
    $(".alert-form").addClass('d-none')
    $(".form-group").removeClass('error')
    $(".desc_error").remove()
    $("div").removeClass('error')
    $("input").removeClass("input-error")
    e.preventDefault()
    // error validation

    //itinerary type
    var itinerary_type = $('input[name=itinerary_type]:checked').val()
    if (!itinerary_type) {
        errors = 'Please select an itinerary type'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_itinerary_type").append(error_div)
        $("#div_id_itinerary_type").addClass('error')
    }

    //primary focus
    var itinerary_type = $('input[name=safari_focus_activity]:checked').val()
    if (!itinerary_type) {
        errors = 'Please select a safari primary focus type'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_safari_focus_activity").append(error_div)
        $("#div_id_safari_focus_activity").addClass('error')
    }

    //secondary focus
    var item = $('input[name=secondary_focus_activity]:checked')
    /**
    if (item.length == 0) {
        errors = 'Please select at least a higlight focus type'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_secondary_focus_activity").append(error_div)
        $("#div_id_secondary_focus_activity").addClass('error')
    } */
    if (item.length > 3) {
        errors = 'Please select no more than 3 highlights'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_secondary_focus_activity").append(error_div)
        $("#div_id_secondary_focus_activity").addClass('error')
    }

    //country
    var item = $('input[name=country_indexes]:checked')
    if (item.length == 0) {
        errors = 'Please select at least a country'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_country_indexes").append(error_div)
        $("#div_id_country_indexes").addClass('error')
    }
    //parks
    var item = $('input[name=parks]:checked')
    if (item.length == 0) {
        errors = 'Please select at least a park'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_parks").append(error_div)
        $("#div_id_parks").addClass('error')
    }
    //title
    var item = $('input[name=title]').val()
    if (!item) {
        errors = 'Please insert a title'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_title").append(error_div)
        $("#div_id_title").addClass('error')
    }

    //short title
    var item = $('input[name=title_short]').val()
    if (!item) {
        errors = 'Please insert a short title'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_title_short").append(error_div)
        $("#div_id_title_short").addClass('error')
    }

    /*header
    var item = $('textarea[name=header]').val()
    if (!item) {
        errors = 'Please insert a header'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_header").append(error_div)
        $("#div_id_header").addClass('error')
    }*/

    //summary
    var item = $('textarea[name=summary]').val()
    if (!item) {
        errors = 'Please insert a summary'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_summary").append(error_div)
        $("#div_id_summary").addClass('error')
    }

    var item = $('input[name=min_price]').val()
    if (!item | item.trim() == '$') {
        errors = 'Please insert a minimum price'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_min_price").append(error_div)
        $("#div_id_min_price").addClass('error')
    }

    var item = $('input[name=max_price]').val()
    if (!item | item.trim() == '$') {
        //errors = 'Please insert a maximum price'
        //var error_div = $('<div />').addClass('desc_error').html(errors);
        //$("#div_id_max_price").append(error_div)
        //$("#div_id_max_price").addClass('error')
    }

    // min max price validation
    var item_min = $('input[name=min_price]').val()
    var item_max = $('input[name=max_price]').val()
    item_min = item_min.replace('$', '').replace(',', '');
    item_max = item_max.replace('$', '').replace(',', '');
    item_min = parseFloat(item_min)
    item_max = parseFloat(item_max)
    if (item_min && item_max && item_min >= item_max) {
        errors = 'Minimum price must be greater than maximum price'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_after_price").append(error_div)
        $("#div_id_after_price").addClass('error')
    }

    if (item_min < 100) {
        errors = 'Minimum price must be greater than 100'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_after_price").append(error_div)
        $("#div_id_after_price").addClass('error')
    }

    //days

    for (i = 1; i <= $("#id_days").val(); i++) {
        const day_val = $("input[name=day_" + i + "_title]").val()
        if (!day_val) {
            $("input[name=day_" + i + "_title]").addClass('input-error')
        }
        const day_description = $("textarea[name=day_" + i + "_description]").val()
        if (!day_description) {
            $("textarea[name=day_" + i + "_description]").addClass('input-error')
        } else {
            if (day_description.length > 300) {
                errors = 'Day-by-day description to be less than 300 characters. Please modify. '
                var error_div = $('<div />').addClass('desc_error').html(errors);
                $(".day_" + i).append(error_div)
                $(".day_" + i).addClass('error')
            }
        }


        //const day_lodges = $("textarea[name=day_" + i + "_lodges]").val()
        //if (!day_lodges) {
        //    $("textarea[name=day_" + i + "_lodges]").addClass('input-error')
        // }

        /*const day_parks = $("select[name=day_" + i + "_parks] option:selected").val()
        if (!day_parks) {
            $("select[name=day_" + i + "_parks]").addClass('input-error')
        }*/
        if (!day_val | !day_description) {
            errors = 'Please complete all required fields'
            var error_div = $('<div />').addClass('desc_error').html(errors);
            $(".day_" + i).append(error_div)
            $(".day_" + i).addClass('error')
        }
    }

    /*
    //international flights
    var item = $('input[name=flight]:checked').val()
    if (!item) {
        errors = 'Please select an option'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_flight").append(error_div)
        $("#div_id_flight").addClass('error')
    }*/


    //single sumplement

    var item = $('input[name=single_supplement]:checked').val()
    if (!item) {
        errors = 'Please select an option'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_single_supplement").append(error_div)
        $("#div_id_single_supplement").addClass('error')
    }
    /*
    var item = $('input[name=single_supplement]:checked').val()
    if (item == "True") {
        var item = $('input[name=single_supplement_price]').val()
        if (!item) {
            errors = 'Please insert a single sumplement price'
            var error_div = $('<div />').addClass('desc_error').html(errors);
            $("#div_id_single_supplement_price").append(error_div)
            $("#div_id_single_supplement_price").addClass('error')
        }
    }*/

    //inclusions
    // select one inclusion or tick other + input sth in the other text field
    var item = $('input[name=inclusions]:checked').val()
    var item_other_incl = $('input[name=other_inclusion]:checked').val()
    var item_other_incl_text = $('input[name=other_inclusion_text]').val()
    if (!item & !(item_other_incl == 'on' & item_other_incl_text != "")) {
        errors = 'Please select at least one inclusion or complete the "other" field'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $(".div_all_inclusions").append(error_div)
        $(".div_all_inclusions").addClass('error')
    }

    //months
    var item = $('input[name=months]:checked')
    if (item.length == 0) {
        errors = 'Please select at least a month'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $("#div_id_months").append(error_div)
        $("#div_id_months").addClass('error')
    }

    //accept_terms
    var item = $('input[name=accept_terms]:checked')
    if (item.length == 0) {
        errors = 'Please accept the terms'
        var error_div = $('<div />').addClass('desc_error').html(errors);
        $(".id_accept_terms_cont").append(error_div)
        $(".id_accept_terms_cont").addClass('error')
    }


    if (!is_edit) {
        //image
        var item = $('input[name=image]').val()
        if (!item) {
            errors = 'Please select an image'
            var error_div = $('<div />').addClass('desc_error').html(errors);
            $("#div_id_image").append(error_div)
            $("#div_id_image").addClass('error')
        }
    }

    if (errors) {
        $(".alert-form").html('Please check the errors')
        $(".alert-form").removeClass('d-none')
        e.preventDefault()
        $('.submit').removeClass('disabled')
        $('.submit').html('Save')
        return false
    }
    $(".form").submit()
    return true
});

//end form validation



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

$('.maxlen').trigger('maxlength.reposition');

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


    //single supplement
    /*
    $("input[name='single_supplement']").change(function () {
        if ($("input[name='single_supplement']:checked").val() == "True") {
            $(".single_supplement_price").removeClass("d-none")
            return
        }
        $(".single_supplement_price").addClass("d-none")
    })
    $("input[name='single_supplement']").trigger('change')
    */


    // bold Game drives

    $(".form-check-input[name=safari_focus_activity][value=" + game_drive_id + "]").parent().wrapInner("<strong />");

    $('.select2_parks').select2({
        width: '100%',
        placeholder: 'Parks and game reserves. Leave blank if not applicable.',
        language: {
            noResults: function (params) {
                return "Please select countries and parks from the checkboxes above";
            }
        }

    });

    // Select country if there's only one
    if ($('.form-check-input.country').length == 1) {
        $('.form-check-input.country').prop('checked', true);
        update()
    }

    //days switch
    $("#id_days").change(function (e) {
        $(".day").addClass("d-none")
        for (i = 1; i <= $(this).val(); i++) {
            $(".day_" + i).removeClass("d-none")
        }
        $('.maxlen').trigger('maxlength.reposition');
    });
    $('#id_days').trigger('change');
    $('.maxlen').trigger('maxlength.reposition');

    //select all months

    $("#select_all").change(function (f) {
        if ($(this).is(':checked')) {
            $("input[name=months]").prop("checked", true)
        } else {
            $("input[name=months]").prop("checked", false)
        }
    })

    //other inclusions
    $("#id_other_inclusion").change(function (f) {
        if ($(this).is(':checked')) {
            $(".other_inclusion_text").removeClass("d-none")
        } else {
            $(".other_inclusion_text").addClass("d-none")
        }
        $('.maxlen').trigger('maxlength.reposition');
    })
    $('#id_other_inclusion').trigger('change');

    //other exclusion
    $("#id_other_exclusion").change(function (f) {
        if ($(this).is(':checked')) {
            $(".other_exclusion_text").removeClass("d-none")
        } else {
            $(".other_exclusion_text").addClass("d-none")
        }
        $('.maxlen').trigger('maxlength.reposition');
    })

    //exclusion inclusion - mutually exclusive items
    $("input[name=exclusions]").change(function () {

    })

    // max highlights
    $("[name='secondary_focus_activity']").click(function (e) {
        var items = $("input[name=secondary_focus_activity]:checked")
        if (items.length >= 3) {
            $("input[name=secondary_focus_activity]:not(:checked)").attr('disabled', 'disabled')
        } else {
            $("input[name=secondary_focus_activity]:not(:checked)").attr('disabled', false)
        }
    });


    new AutoNumeric("input[name='min_price']", {
        alwaysAllowDecimalCharacter: false,
        decimalPlaces: 0,
        maximumValue: 500000,
    });
    new AutoNumeric("input[name='max_price']", {
        alwaysAllowDecimalCharacter: false,
        decimalPlaces: 0,
        maximumValue: 500000
    });
    new AutoNumeric("input[name='single_supplement_price']", {
        alwaysAllowDecimalCharacter: false,
        decimalPlaces: 0,
        minimumValue: 0,
        maximumValue: 500000
    });
    update()


    //loading
    $(".loading").addClass('d-none')
    $(".loaded").removeClass('d-none')
    $('#id_other_exclusion').trigger('change');

});
