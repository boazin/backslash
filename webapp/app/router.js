import Ember from 'ember';
import config from './config/environment';

var Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
  this.route("sessions", { path: "/sessions" });
  this.resource("session", { path: "/sessions/:session_id" });

  this.route("tests", { path: "/tests" });
  this.resource("test", { path: "/tests/:test_id" });

  this.route('search-sessions', { path: '/sessions/search/:filters' });
  this.route('search-tests', { path: '/tests/search/:filters' });
  this.resource('setup', function() {});
  this.resource('login', function() {});
});

export default Router;
