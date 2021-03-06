import DS from 'ember-data';

export default DS.Model.extend({
  integerId: function() {
    return +this.get('id');
  }.property('id'),

  logicalId: DS.attr('string'),
  startTime: DS.attr('date'),
  endTime: DS.attr('date'),
  duration: DS.attr('number'),
  status: DS.attr('string'),
  testConclusion: DS.attr('string'),
  name: DS.attr('string'),
  editedStatus: DS.attr('string'),
  testMetadata: DS.attr(),
  testErrors: DS.attr(),
  numErrors: DS.attr('number'),
  numFailures: DS.attr('number'),
  interrupted: DS.attr('boolean'),
  skipped: DS.attr('boolean'),
  session: DS.belongsTo('session', {async: true}, {inverse:'tests'}),
  apiPath: DS.attr('string'),
  type: DS.attr('string'),

  //ember date needs the wrong units
  properStartTime: function() {
    var d = new Date(0);
    d.setUTCSeconds(this.get('startTime'));
    return d;
  }.property('startTime'),
  properEndTime: function() {
    if (this.get('endTime') == null)
    {
      return null;
    }
    var d = new Date(0);
    d.setUTCSeconds(this.get('endTime'));
    return d;
  }.property('endTime'),

  isError: function() {
    return (this.get('status') === 'ERROR');
  }.property('status'),

  isFailure: function() {
    return (this.get('status') === 'FAILURE');
  }.property('status'),

  isSuccess: function() {
    return (this.get('status') === 'SUCCESS');
  }.property('status'),

  isRunning: function() {
    return (this.get('status') === 'RUNNING');
  }.property('status'),

  isInterrupted: function() {
    return (this.get('status') === 'INTERRUPTED');
  }.property('status'),

  isSkipped: function() {
    return (this.get('status') === 'SKIPPED');
  }.property('status'),

  noErrors: function() {
    return (this.get('numErrors') === 0);
  }.property('numErrors'),

  isEditedStatus: function() {
    if(this.get('editedStatus'))
    {
      return true;
    }
    return false;
  }.property('editedStatus'),

  noFailures: function() {
    return (this.get('numFailures') === 0);
  }.property('numFailures')

});
