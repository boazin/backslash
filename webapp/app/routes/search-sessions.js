import Ember from 'ember';
import RouteMixin from 'ember-cli-pagination/remote/route-mixin';

Ember.$.extend({

  getQueryParameters : function(str) {
    return (str).replace(/(^\?)/,'').split("&").map(function(n){return n = n.split("="),this[n[0]] = decodeURIComponent(n[1]),this;}.bind({}))[0];
  }

});

export default Ember.Route.extend(RouteMixin, {
    model: function(params) {
      var new_params = Ember.$.getQueryParameters(params.filters);
      new_params.paramMapping = {page: "page",
        perPage: "page_size",
        total_pages: "total_num_pages"};
      return this.findPaged('session', new_params);
    },
    controllerName: 'sessions',

    renderTemplate: function() {
      this.render('sessions');


    }
  });
