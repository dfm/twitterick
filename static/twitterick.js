function like(poem_id) {
  $.getJSON("/like/"+poem_id, function (data) {
    $("#votes-"+poem_id).text(data.votes);
    $("#like-"+poem_id).attr("href", "javascript:void(0)");
  });
}
