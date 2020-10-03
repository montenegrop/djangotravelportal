<template>
    <div class="row max-width-admin" id="member_photos">
        <div class="col-12">
            <div class="card main container-fluid">
                <div class="card-header">
                    <div class="row d-flex justify-content-between px-2">
                        <h4>Manage your photos</h4>
                        <a :href="url" type="submit" role="button"
                           class="btn btn-green-secondary">Upload a new photo</a>
                    </div>
                </div>
                <div class="card-body">
                    <div v-if="photosCount == 0" class="col-12 noresults text-center">
                        You don't have any photos yet. Click the upload button to add new photos
                    </div>
                    <div id="gallery" class="gallery" itemscope itemtype="http://schema.org/ImageGallery">
                        <template>
                            <div class="vld-parent">
                                <loading :active.sync="isLoading"></loading>
                            </div>
                        </template>
                        <div class="row">
                            <div class="col-md-6 col-lg-4 col-sm-6 col-xs-1"
                                 v-for="(photo, index) in photosJson">
                                <figure class="position-relative" itemprop="associatedMedia" itemscope
                                        itemtype="http://schema.org/ImageObject">
                                    <a :data-width=photo.width class="gallery_a fresco" :data-height=photo.height
                                       :href=photo.image_url
                                       :data-fresco-caption=photo.get_description :data-fresco-id=photo.id
                                       :data-fresco-photo-url=photo.photo_url
                                       :data-fresco-title=photo.title :data-fresco-kudu-count=photo.kudu_count
                                       data-fresco-options="ui: 'inside'"
                                       :data-caption='photo.get_description' :data-index=index target="_blank"
                                       data-fresco-group="unique_name">
                                        <div id="animal-img-wrapper">
                                            <div v-bind:style="{ backgroundImage: 'url(' + photo.thumbnail_url + ')' }"
                                                 :data-photo_url=photo.thumbnail_url class="animal-photo img__wrap"
                                                 :data-href=photo.image_url
                                                 :data-caption="photo.get_description"
                                            >
                                                <div class="img__description">
                                                    <strong class="mb-2" v-html="photo.title">
                                                    </strong>
                                                    <h5>{{ photo.country_index }}</h5>
                                                    <p class="mb-0" v-for="animal in photo.animals">{{ animal }}</p>
                                                </div>

                                            </div>
                                        </div>
                                    </a>
                                    <a class="btn btn-sm btn-green-primary position-absolute edit-photo"
                                       :href="url + '&photo=' + photo.id">
                                        Edit photo </a>
                                </figure>
                            </div>
                        </div>
                        <div v-if="pageCount > 1" class="row">
                            <div class="margin-auto">
                                <paginate v-model="current_page" :page-count="pageCount"
                                          :click-handler="changePage" :prev-text="'Prev'"
                                          :next-text="'Next'" :container-class="'pagination'"
                                          :page-class="'page-item'" :page-link-class="'page-link'"
                                          :prev-class="'page-link'" :next-class="'page-link'">
                                </paginate>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

    export default {
        name: "yas-member-photos",
        props: ['url', 'photosCount', 'photosJson', 'pageCount'],

        data() {
            return {
                isLoading: false,
                current_page: 1,
                no_results: false,
                has_results: true,
            }
        },
        methods: {
            changePage(current_page) {
                document.location.href = this.update_url_parameter(document.location.href, "page", current_page);
            },
            update_url_parameter: function (url, param, paramVal) {
                var newAdditionalURL = "";
                var tempArray = url.split("?");
                var baseURL = tempArray[0];
                var additionalURL = tempArray[1];
                var temp = "";
                if (additionalURL) {
                    tempArray = additionalURL.split("&");
                    for (var i = 0; i < tempArray.length; i++) {
                        if (tempArray[i].split('=')[0] != param) {
                            newAdditionalURL += temp + tempArray[i];
                            temp = "&";
                        }
                    }
                }
                var rows_txt = temp + "" + param + "=" + paramVal;
                return baseURL + "?" + newAdditionalURL + rows_txt;
            },
        },
    }
</script>




