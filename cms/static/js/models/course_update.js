define(["backbone", "jquery", "jquery.ui"], function(Backbone, $) {
    // course update -- biggest kludge here is the lack of a real id to map updates to originals
    var CourseUpdate = Backbone.Model.extend({
        defaults: {
            "date" : $.datepicker.formatDate('yy年mm月dd日', new Date()),
            "content" : ""
        }
    });
    return CourseUpdate;
}); // end define()
