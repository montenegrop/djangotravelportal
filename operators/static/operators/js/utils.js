// Create slug similar for server by CountryIndex/Park model
function slugByPlace(place) {
  return {
    model: place.tag == 'country' ? 'CountryIndex' : 'Park',
    id: place.base_id,
    value: place.name_short,
    slug: place.slug
  }
}

function findPlaceFromSlug(slug) {
  for (let i = 0; i < filter_variants_country_and_park.length; i++) {
    if (filter_variants_country_and_park[i].slug == slug) {
      return filter_variants_country_and_park[i]
    }
  }
  return null
}

// resore slug model
function restoreSlug(slug_value) {
  // server_slug is taken from global context
  if (server_slug && server_slug.slug == slug_value) {
    return server_slug
  } else {
    let place = findPlaceFromSlug(slug_value)
    if (place) {
      return slugByPlace(place)
    }
  }
  return null
}

// Navigate to slug url
// Attention! Vue context is required! Use ".bind()"
function slugRoutePush(slug) {
  this.current_page = 1
  let query = JSON.parse(JSON.stringify(this.$route.query))
  let path = '/african-safari-tour-packages/'
  if (slug) {
    path = path + slug.slug
  }
  this.$router.push({
      path: path,
      query: query
  }).catch(function (error) {
    if (!error.message.includes('Avoided redundant navigation to current location')) {
      console.error(error)
    }
  })
  this.lazyLoad()
}