Vue.component('badge-filter', {
  template: '<p @click="remove(filter)" class="text-left font-weight-light filter-border font-11">\
    <span v-if="filter.formated">\
      [[ filter.prefix ]][[ filter.formated ]]\
    </span>\
    <span v-else>\
      [[ filter.prefix ]][[ filter.value ]]\
    </span>\
    <span v-if="filter.rating">\
      <i v-for="i in filter.rating" class="fas fa-star yellow"></i> or high\
    </span>\
    <a id="selected-filter-x" class="fas fa-times pl-1"></a>\
  </p>',
  delimiters: ['[[', ']]'],
  data() {
    return {
    }
  },
  props: {
    filter: {
      type: Object,
      required: true
    },
  },
  methods: {
    remove() {
      this.$emit('remove', this.filter)
    }
  },
})

Vue.component('pagination', {
  template: '#pagination_component',
  delimiters: ['[[', ']]'],
  data() {
    return {
      max_on_page: 30,
      pages_count: null,
      pages_list: [],
      is_show_first: false,
      is_show_last: false,
      is_result_finded: true
    }
  },
  props: {
    pagination: {
      type: Object,
      default: function () {
        return {
          positions_total: null,
          positions_on_page: null,
          showing_from: null,
          showing_to: null,
        }
      }
    },
    current_page: {
      type: Number,
      default: 1
    },
    scroll_to: {
      type: String,
      default: ''
    },
  },
  methods: {
    recalc() {
      this.pages_count = Math.ceil(this.pagination.positions_total / this.max_on_page)
      this.pagination.showing_from = this.max_on_page * (this.current_page - 1) + 1
      this.pagination.showing_to = this.pagination.showing_from + this.pagination.positions_on_page - 1
      this.pages_list = []
      this.pages_list.push({
          number: 1,
          is_current: this.current_page == 1
      })
      if (this.current_page > 4) {
          this.pages_list.push({
              number: 3,
              is_space: true
          })
      }
      for (let i = this.current_page - 2; i <= this.current_page + 2; i++) {
          if (i > 1 && i < this.pages_count) {
              this.pages_list.push({
                  number: i,
                  is_current: this.current_page == i
              })
          }
      }
      if (this.current_page < this.pages_count - 3) {
          this.pages_list.push({
              number: this.pages_count - 3,
              is_space: true
          })
      }
      if (this.pages_count > 1) {
          this.pages_list.push({
              number: this.pages_count,
              is_current: this.current_page == this.pages_count
          })
      }
      if (this.pagination.positions_total) {
          this.is_show_first = this.current_page != 1
          this.is_show_last = this.current_page != this.pages_list[this.pages_list.length - 1].number
          this.is_result_finded = true
      } else {
          this.is_show_first = false
          this.is_show_last = false
          this.is_result_finded = false
      }
    },
    gotoPage(page) {
      var component = this
      page.is_current = true
      component.$emit('goto', page.number)
      Vue.nextTick(function () {
        if (component.scroll_to) {
          var block = document.querySelector(component.scroll_to)
          if (block) {
              block.scrollIntoView({
                  behavior: 'smooth',
                  block: 'end'
              })
          }
        }
      })
    },
  },
  watch: {
    'pagination.positions_total'() {
      this.recalc()
    },
    'pagination.positions_on_page'() {
      this.recalc()
    },
    current_page() {
      this.recalc()
    },
  }
})
Vue.component('operators-filter', {
  template: '#filter_component',
  delimiters: ['[[', ']]'],
  data() {
    return {
      filter_variants_country_and_park: filter_variants_country_and_park,
      tour_operator_that: tour_operator_that,
      luxury_focus: luxury_focus,
      minimum_rating: minimum_rating,
      languages: languages,
      headquarters: headquarters,
      is_inited: false
    }
  },
  props: {
    custom_filters: {
      type: Array,
      required: true
    },
    excluded_slug: {
      type: Object,
      default: null
    }
  },
  methods: {
    // Merge filter tags: remove existing and add new
    fillCustomFilters(items, filter_tag, filter_ref_component, prefix = '') {
      for (let i = this.custom_filters.length - 1; i >= 0; i--) {
        if (filter_tag.includes(this.custom_filters[i].tag)) {
          this.custom_filters.splice(i, 1)
        }
      }
      for (let i = 0; i < items.length; i++) {
        if (items[i].value || items[i].rating) {
          let filter = {
            id: items[i].id,
            value: items[i].value,
            rating: items[i].rating,
            formated: items[i].formated,
            tag: items[i].tag ? items[i].tag : filter_tag[0],
            ref: filter_ref_component,
            prefix: prefix
          }
          this.custom_filters.push(filter)
        }
      }
      this.$emit('change')
    },
    removeFilterInComponent(filter) {
      if (filter.ref) {
        let ref = this.$refs[filter.ref]
        if (ref) {
          if (ref.removeByValue) {
            ref.removeByValue(filter.value)
          } else if (ref.removeByTag) {
            ref.removeByTag(filter.tag)
          } else if (ref.remove) {
            ref.remove()
          }
        }
        if (this[filter.ref]) {
          this[filter.ref] = ''
        }
      }
      this.$emit('change')
    },
    synchronize(filter) {
      let ref = this.$refs[filter.ref]
      ref.synchronize(filter)
    },
    init() {
      this.is_inited = true
    },
    removeSlug() {
      this.$emit('remove-slug')
    },
    changeSlug(slug) {
      this.$emit('change-slug', slug)
    }
  },
  watch: {
    excluded_slug() {
      let ref = this.$refs.placesFilter
      Vue.nextTick(() => {
        ref.uniqueVariantsFilter()
        if (this.excluded_slug) {
          ref.removeByValue(this.excluded_slug.value)
        }
      })
    }
  }
})
Vue.component('packages-filter', {
  template: '#filter_component',
  delimiters: ['[[', ']]'],
  data() {
    return {
      filter_variants_country_and_park: filter_variants_country_and_park,
      adult_traveler: '',
      main_focus_activities: main_focus_activities,
      second_focus_activities: second_focus_activities,
      itinerary_types: itinerary_types,
      activity_levels: [
          { id: 1, value: 'Easy' },
          { id: 2, value: 'Moderate' },
          { id: 3, value: 'Strenuous' },
      ],
      is_inited: false
    }
  },
  props: {
    custom_filters: {
      type: Array,
      required: true
    },
    excluded_slug: {
      type: Object,
      default: null
    }
  },
  methods: {
    // Merge filter tags: remove existing and add new
    fillCustomFilters(items, filter_tag, filter_ref_component, prefix = '') {
      for (let i = this.custom_filters.length - 1; i >= 0; i--) {
        if (filter_tag.includes(this.custom_filters[i].tag)) {
          this.custom_filters.splice(i, 1)
        }
      }
      for (let i = 0; i < items.length; i++) {
        if (items[i].value) {
          let filter = {
            id: items[i].id,
            value: items[i].value,
            formated: items[i].formated,
            tag: items[i].tag ? items[i].tag : filter_tag[0],
            ref: filter_ref_component,
            prefix: prefix
          }
          this.custom_filters.push(filter)
        }
      }
      this.$emit('change')
    },
    removeFilterInComponent(filter) {
      if (filter.ref) {
        let ref = this.$refs[filter.ref]
        if (ref) {
          if (ref.removeByValue) {
            ref.removeByValue(filter.value)
          } else if (ref.removeByTag) {
            ref.removeByTag(filter.tag)
          } else if (ref.remove) {
            ref.remove()
          }
        }
        if (this[filter.ref]) {
          this[filter.ref] = ''
        }
      }
      this.$emit('change')
    },
    synchronize(filter) {
      let ref = this.$refs[filter.ref]
      ref.synchronize(filter)
    },
    init() {
      this.is_inited = true
    },
    removeSlug() {
      this.$emit('remove-slug')
    },
    changeSlug(slug) {
      this.$emit('change-slug', slug)
    }
  },
  watch: {
    excluded_slug() {
      let ref = this.$refs.placesFilter
      Vue.nextTick(() => {
        ref.uniqueVariantsFilter()
        if (this.excluded_slug) {
          ref.removeByValue(this.excluded_slug.value)
        }
      })
    }
  }
})

Vue.component('places-filter', {
  template: '<div class="places-filter">\
    <div v-if="local_slug" class="filter-item">\
      <v-select\
        label="name_short"\
        v-model="local_slug"\
        :options="variants"\
        :clearable="true"\
        :searchable="true"\
      >\
        <template slot="option" slot-scope="option">\
          <div class="place-item">\
            <label>[[ option.name_short ]]</label>\
            <span>[[ option.mini_description ]]</span>\
          </div>\
        </template>\
      </v-select>\
    </div>\
    <div v-for="(item, index) in places_blocks" :key="item.index" class="filter-item">\
      <v-select\
        label="name_short"\
        v-model="item.place"\
        :options="unique_variants"\
        :clearable="true"\
        :searchable="true"\
        :placeholder="placeholder(index)"\
        @input="tryRemove(item, index)"\
      >\
        <template slot="option" slot-scope="option">\
          <div class="place-item">\
            <label>[[ option.name_short ]]</label>\
            <span>[[ option.mini_description ]]</span>\
          </div>\
        </template>\
      </v-select>\
    </div>\
    <a @click="add">Add Place +</a>\
  </div>',
  delimiters: ['[[', ']]'],
  components: {
    'v-select': VueSelect.VueSelect
  },
  data() {
    return {
      unique_variants: [],
      places_blocks: [],
      indexator: 0,
      selected_names: [],
      local_slug: null,
      is_init: false
    }
  },
  props: {
    value: {
      type: String,
      default: ''
    },
    variants: {
      type: Array,
      default() {
        return []
      }
    },
    is_inited: {
      type: Boolean,
      required: true
    },
    excluded_slug: {
      type: Object,
        default() {
          return null
        }
    }
  },
  methods: {
    add() {
      // console.log('add')
      this.indexator++
      let block = {
        index: this.indexator,
        place: null
      }
      this.places_blocks.push(block)
      return block
    },
    tryRemove(item, index) {
      if (!item.place && this.places_blocks.length > 1) {
        this.places_blocks.splice(index, 1)
      }
    },
    removeByValue(value) {
      for (let i = this.places_blocks.length - 1; i >= 0; i--) {
        if (this.places_blocks[i].place) {
          if (this.places_blocks[i].place.name_short == value) {
            this.places_blocks[i].place = null
            if (this.places_blocks.length > 1) {
              this.places_blocks.splice(i, 1)
            }
          }
        }
      }
    },
    init() {
      if (!this.places_blocks.length) {
        this.add()
      }
    },
    change(event) {
      // console.log('change', event)
    },
    opened() { },
    placeholder(index) {
      return index ? 'And ...' : 'Where to ...'
    },
    uniqueVariantsFilter() {
      this.unique_variants = this.variants.slice()
      for (let i = 0; i < this.places_blocks.length; i++) {
        if (this.places_blocks[i].place) {
          for (let l = 0; l < this.unique_variants.length; l++) {
            if (this.places_blocks[i].place.name_short == this.unique_variants[l].name_short) {
              let k = this.unique_variants.splice(l, 1)
              break
            }
          }
        }
      }
      if (this.excluded_slug && (
          this.excluded_slug.model == 'CountryIndex' || 
          this.excluded_slug.model == 'Park')) {
        let l = this.unique_variants.findIndex(x => x.name_short == this.excluded_slug.value)
        if (l > -1) {
          this.unique_variants.splice(l, 1)
        }
      }
    },
    synchronize(filter) {
      if (!this.unique_variants.length) this.uniqueVariantsFilter()

      let is_exists = this.places_blocks.some(x => 
        x.place != null
        && x.place.base_id == filter.id
        && x.place.tag == filter.tag
      )

      if (is_exists) return

      let block = this.places_blocks[this.places_blocks.length - 1]
      if (block.place != null) {
        block = this.add()
      }
      for (let i = 0; i < this.unique_variants.length; i++) {
        let variant = this.unique_variants[i]
        if (variant.base_id == filter.id && variant.tag == filter.tag) {
          block.place = variant
          break
        }
      }
    }, selected () {
        this.selected_names = []
        for (let i = 0; i < this.places_blocks.length; i++) {
          let block = this.places_blocks[i]
          // let is_exists = this.selected_names.some(x => 
          //   x.value == block.place.name_short
          //   && x.tag == block.place.tag
          // )
          if (block.place) {
            this.selected_names.push({
              id: block.place.base_id,
              value: block.place.name_short,
              tag: block.place.tag
            })
          }
        }
        if (this.is_inited) {
          this.$emit('selected', this.selected_names)
        }
        this.uniqueVariantsFilter()
    },
    updateSlug() {
      if (!this.excluded_slug) {
        this.local_slug = null
      } else {
        if (this.excluded_slug.model == 'CountryIndex' || this.excluded_slug.model == 'Park') {
          this.local_slug = this.variants.find(x => x.name_short == this.excluded_slug.value)
        }
      }
    }
  },
  watch: {
    places_blocks: {
      handler: function () {
        this.selected()
      },
      deep: true
    },
    is_inited (value) {
      if (value) {
        this.selected()
      }
    },
    excluded_slug() {
      this.updateSlug()
    },
    local_slug: {
      handler: function(value, old) {
        if (!this.local_slug) {
          this.$emit('remove-slug')
        } else {
          // if select other place
          if (!!old && value.name_short != old.name_short) {
            let slug = slugByPlace(value)
            this.$emit('change-slug', slug)
          }
        }
      },
      deep: true,
    }
  },
  mounted() {
    this.init()
    this.updateSlug()
  }

})

Vue.component('datepicker-filter', {
  template: '<div class="card-body px-0 py-1 font-weight-lighter text-light-grey row">\
  <div class="form-group col-md-6 col-sm-12">\
    <date-picker \
      v-model="from_date"\
      format="MM/DD/YYYY"\
      lang="en"\
      :disabled-date="disabledDateFrom"\
      placeholder="Arrival"\
      :editable="false"\
      :clearable="true"\
      :first-day-of-week="1"\
      style="max-width: 100%;"\
      input-class="form-control datepicker font-12"\
    >\
      <template slot="footer">\
          <p></p>\
      </template>\
    </date-picker>\
  </div>\
  <div class="form-group col-md-6 col-sm-12">\
    <date-picker \
      v-model="to_date"\
      format="MM/DD/YYYY"\
      lang="en"\
      :disabled-date="disabledDateTo"\
      placeholder="Departure"\
      :editable="false"\
      :clearable="true"\
      :first-day-of-week="1"\
      style="max-width: 100%;"\
      input-class="form-control datepicker font-12"\
    >\
      <template slot="footer">\
          <p></p>\
      </template>\
    </date-picker>\
  </div>\
</div>',
  delimiters: ['[[', ']]'],
  data() {
    return {
      from_date: '',
      from_date_valid: '',
      to_date: '',
      to_date_valid: '',
      selected_names: [],
      format: 'MM/DD/YYYY',
    }
  },
  watch: {
    from_date(value) {
      let date = moment(value, this.format)
      if (date.isValid()) {
        this.from_date_valid = date.format(this.format)
      } else {
        this.from_date_valid = ''
      }
      this.$emit('selected', {
        id: null,
        value: this.from_date_valid,
        prefix: 'From: ',
        tag: 'from-date'
      })
      var to_date = moment(this.to_date)
      if (to_date.isBefore(date)) {
        this.to_date = date.toDate()
      }
    },
    to_date(value) {
      let date = moment(value, this.format)
      if (date.isValid()) {
        this.to_date_valid = date.format(this.format)
      } else {
        this.to_date_valid = ''
      }
      this.$emit('selected', {
        id: null,
        value: this.to_date_valid,
        prefix: 'To: ',
        tag: 'to-date'
      })
    },
  },
  methods: {
    removeByTag(tag) {
      if (tag == 'from-date') {
        this.from_date = ''
        this.from_date_valid = ''
      }
      if (tag == 'to-date') {
        this.to_date = ''
        this.to_date_valid = ''
      }
    },
    disabledDateFrom(date) {
      var today = moment()
      var date = moment(date)
      if (date.isBefore(today, 'day')) {
        return true
      }
      return false
    },
    disabledDateTo(date) {
      var today = moment()
      var from_date = moment(this.from_date)
      var date = moment(date)
      if (date.isBefore(today, 'day') || date.isBefore(from_date, 'day')) {
        return true
      }
      return false
    },
    synchronize(filter) {
      if (filter.tag == 'from-date') {
        this.from_date = moment(filter.value, this.format).toDate()
      }
      if (filter.tag == 'to-date') {
        this.to_date = moment(filter.value, this.format).toDate()
      }
    }
  }
})


Vue.component('price-filter', {
  // https://nightcatsama.github.io/vue-slider-component/
  components: {
    'vueSlider': window['vue-slider-component'],
  },
  template: '<div style="padding: 0 10px;"><vue-slider \
    v-if="price_range"\
    ref="slider"\
    v-model="price_range"\
    :min="min_price_limit"\
    :max="max_price_limit"\
    :interval="real_interval"\
    :tooltip-formatter="formatter"\
    :lazy="true"\
    :enable-cross="false"\
    :marks="marks"\
  ></vue-slider></div>',
  delimiters: ['[[', ']]'],
  data() {
    return {
      is_init: false,
      min_price: 1,
      max_price: 1001,
      min_price_limit: 1,
      max_price_limit: 1001,
      selected_names: [],
      price_range: null,
      real_interval: 1,
      route_values: {},
      formatter: v => '$' + this.format(v, this.ratio),
    }
  },
  props: {
    min: {
      type: Number,
      default: 1
    },
    max: {
      type: Number,
      default: 1001
    },
    interval: {
      type: Number,
      default: 1
    },
    tag: {
      type: String,
      default: ''
    },
    min_label: {
      type: String,
      default: ''
    },
    max_label: {
      type: String,
      default: ''
    },
    ratio: {
      type: Number,
      default: 1
    }
  },
  computed: {
    marks() {
      if (!this.price_range) return {}
      let json = `{
        "${this.min_price_limit}": {
          "label": "$${this.format(this.min_price_limit, this.ratio)}",
          "style": {
            "width": "10px",
            "height": "10px",
            "display": "block",
            "backgroundColor": "#999",
            "transform": "translate(-3px, -3px)"
          }
        },
        "${this.max_price_limit}": {
          "label": "$${this.format(this.max_price_limit, this.ratio)}",
          "style": {
            "width": "10px",
            "height": "10px",
            "display": "block",
            "backgroundColor": "#999",
            "transform": "translate(-3px, -3px)"
          }
        }
      }`
      return JSON.parse(json)
    }
  },
  watch: {
    price_range: {
      handler: function (val, oldVal) {
        if (!this.is_init) {
          return
        }

        if (oldVal == null) {
          oldVal = [-1, -1]
        }

        if (val[0] != oldVal[0]) {
          if (this.price_range[0] > this.min_price_limit) {
            this.min_price = this.price_range[0]
          } else {
            this.min_price = ''
          }
          this.$emit('selected', {
            id: null,
            value: this.min_price,
            formated: this.format(this.min_price, this.ratio),
            prefix: this.min_label + ' $',
            tag: 'min-' + this.tag
          })              
        }
        if (val[1] != oldVal[1]) {
          if (this.price_range[1] < this.max_price_limit) {
            this.max_price = this.price_range[1]
          } else {
            this.max_price = ''
          }
          this.$emit('selected', {
            id: null,
            value: this.max_price,
            formated: this.format(this.max_price, this.ratio),
            prefix: this.max_label + ' $',
            tag: 'max-' + this.tag
          })
        }
      },
      deep: true
    }
  },
  methods: {
    format(value, ratio) {
      return (value * ratio).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    },
    removeByTag(tag) {
      let min = this.price_range[0]
      let max = this.price_range[1]
      if (tag == 'min-' + this.tag) {
        this.min_price = ''
        min = this.min_price_limit
      }
      if (tag == 'max-' + this.tag) {
        this.max_price = ''
        max = this.max_price_limit
      }
      this.$refs.slider.setValue([min, max])
    },
    synchronize(filter) {
      if (filter.tag == 'min-' + this.tag) {
        this.route_values.min = filter.value
      }
      if (filter.tag == 'max-' + this.tag) {
        this.route_values.max = filter.value
      }
    },
    init() {
      this.min_price = this.min
      this.min_price_limit = this.min
      if (this.interval == 1) {
        this.max_price = this.max
        this.max_price_limit = this.max
      } else {
        let more_max = (this.max - this.min) - ((this.max - this.min) % this.interval) + this.interval + this.min
        this.real_interval = this.interval
        this.max_price = more_max
        this.max_price_limit = more_max
      }
      var _vm = this
      Vue.nextTick(function () {
        _vm.is_init = true
        let min = _vm.min_price_limit
        let max = _vm.max_price_limit
        if (_vm.route_values.min) {
          min = _vm.route_values.min
        }
        if (_vm.route_values.max) {
          max = _vm.route_values.max
        }
        _vm.price_range = [min, max]
      })
    }

  },
  mounted() {
    this.init()
  }
})
Vue.component('radio-filter', {
  template: '<div class="card-body py-1 pl-1 font-weight-lighter text-light-grey">\
    <div v-for="item in items" :key="item.id" class="form-check pb-2">\
      <label class="form-check-label font-13">\
        <input v-model="local_value" type="radio" :name="this.tag" :id="radioId(item.id)" :value="item" class="form-check-input m-top-03">\
        [[ item[value_property] ]]\
        <span v-if="item.rating" class="yellow h6">\
          <i v-for="i in 5" class="fa-star" :class="i <= item.rating ? \'fas\' : \'far\'"></i>\
        </span>\
        <span v-if="item.count" class="font-9">([[item.count]])</span>\
      </label>\
    </div>\
    <div>\
    <a v-if="local_value" @click="local_value=null;">Clear all</a>\
    </div>\
  </div>',
  delimiters: ['[[', ']]'],
  data() {
    return {
      local_value: null,
    }
  },
  props: {
    items: {
      type: Array,
      default() {
        return []
      }
    },
    tag: {
      type: String,
      required: true
    },
    value_property: {
      type: String,
      default: 'value'
    }
  },
  watch: {
    local_value: {
      handler: function (value) {
        if (this.local_value) {
          this.$emit('selected', {
            id: this.local_value.id,
            value: this.local_value[this.value_property],
            rating: this.local_value.rating,
          })
        } else {
          this.$emit('selected', {
            id: null,
            value: '',
            rating: null
          })
        }
      },
      deep: false
    }
  },
  methods: {
    remove() {
      this.local_value = null
    },
    radioId(id) {
      return this.tag + id
    },
    synchronize(filter) {
      for (var i = 0; i < this.items.length; i++) {
        if (this.items[i].id == filter.value) {
          this.local_value = this.items[i]
          break
        }
      }
    }
  }
})

Vue.component('checkboxes-filter', {
  template: '<div class="card-body px-0 py-1 font-weight-lighter text-light-grey">\
    <div v-for="item in items" :key="item.id" class="form-check pb-2">\
      <label class="form-check-label font-13">\
        <input v-model="local_value" type="checkbox" :name="this.tag" :id="checkboxId(item.id)" :value="item" class="form-check-input m-top-03">\
        [[ item[value_property] ]]\
        <span v-if="item.count" class="font-9">([[item.count]])</span>\
      </label>\
    </div>\
    <div>\
    <a v-if="local_value" @click="local_value=[];">Clear all</a>\
    </div>\
  </div>',
  delimiters: ['[[', ']]'],
  data() {
    return {
      local_value: [],
    }
  },
  props: {
    items: {
      type: Array,
      default() {
        return []
      }
    },
    tag: {
      type: String,
      required: true
    },
    value_property: {
      type: String,
      default: 'value'
    }
  },
  watch: {
    local_value: {
      handler: function () {
        this.$emit('selected', this.local_value)
      },
      deep: true
    }
  },
  methods: {
    removeByValue(value) {
      for (let i = this.local_value.length - 1; i >= 0; i--) {
        if (this.local_value[i][this.value_property] == value) {
          this.local_value.splice(i, 1)
        }
      }
    },
    checkboxId(id) {
      return this.tag + id
    },
    synchronize(filter) {
      if (filter.ids) {
        for (let i = 0; i < this.items.length; i++) {
          if (filter.ids.includes(this.items[i].id)) {
            this.local_value.push(this.items[i])
          }
        }
      }
      if (filter.values) {
        for (let i = 0; i < this.items.length; i++) {
          if (filter.values.includes(this.items[i][this.value_property])) {
            this.local_value.push(this.items[i])
          }
        }
      }
    }
  },
  mounted() {
    if (this.value_property != 'value') {
      for (let i = 0; i < this.items.length; i++) {
        this.items[i].value = this.items[i][this.value_property]
      }
    }
  }
})