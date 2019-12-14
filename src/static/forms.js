$("#collapseDocumentForm")
  .on("show.bs.collapse", function() {
    Cookies.set("form-collapse__show", true);
  })
  .on("hide.bs.collapse", function() {
    Cookies.set("form-collapse__show", false);
  });

$("#collapseTagList")
  .on("show.bs.collapse", function() {
    Cookies.set("tags-collapse__show", true);
  })
  .on("hide.bs.collapse", function() {
    Cookies.set("tags-collapse__show", false);
  });

// Based on this example: https://jqueryui.com/autocomplete/#multiple
function split( val ) {
  return val.split( /\s+/ );
}
function extractLast( term ) {
  return split( term ).pop();
}

function configureAutocompleteWith(availableTags) {
  $( "#form__tags" )
    // don't navigate away from the field on tab when selecting an item
    .on( "keydown", function( event ) {
      if ( event.keyCode === $.ui.keyCode.TAB &&
          $( this ).autocomplete( "instance" ).menu.active ) {
        event.preventDefault();
      }
    })
    .autocomplete({
      minLength: 0,
      source: function( request, response ) {
        // delegate back to autocomplete, but extract the last term
        response( $.ui.autocomplete.filter(
          availableTags, extractLast( request.term ) ) );
      },
      focus: function() {
        // prevent value inserted on focus
        return false;
      },
      select: function( event, ui ) {
        var terms = split( this.value );
        // remove the current input
        terms.pop();
        // add the selected item
        terms.push( ui.item.value );
        // add placeholder to get the space at the end
        terms.push( "" );
        this.value = terms.join( " " );
        return false;
      }
    });
  }

function enableDeleteDocuments() {
  $(".document__delete button").css("display", "block");
}

function deleteDocument(documentId, title) {
  if (title !== "") {
    confirmation = window.confirm("Are you sure you want to delete " + title + "?");
  } else {
    confirmation = window.confirm("Are you sure you want to delete this document?");
  }

  if (!confirmation) {
    return;
  }

  $.ajax({
    type: "DELETE",
  	url: "documents/" + documentId,

  	success: function(_) {
  		$("#document__" + documentId).remove()
  	},

  	error: function(jqXHR, textStatus, errorThrown) {
  		console.log("Error trying to delete document " + documentId);
  		console.log("jqXHR=" + jqXHR + "; textStatus=" + textStatus + "; errorThrown=" + errorThrown);
  		alert("Something went wrong trying to delete the document!");
  	}
  })
}
