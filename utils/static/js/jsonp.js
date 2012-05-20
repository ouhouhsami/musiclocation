// jsonp.js
//
// for using jsonp - it dynamically generates and injects script tags for
// JSONP requests.
//
// Tue, 28 Feb 2012  09:45
//


(function(globalContext) {
  // "Static" script ID counter
  var scriptTagCounter = 1, head;

  function invokeJsonp(fullUrl, cacheOk) {
    var c = cacheOk || true; // false  ... default
    script = buildScriptTag(fullUrl, c);

    if (typeof head != 'object') {
      head = document.getElementsByTagName("head").item(0);
    }
    head.appendChild(script);
    return script;
  }

  function removeTag(tag)  {
    if (typeof head != 'object') {
      head = document.getElementsByTagName("head").item(0);
    }
    head.removeChild(script);
  }

  function buildScriptTag(url, cacheOk)  {
    // Create the script tag
    var element = document.createElement("script"),
      additionalQueryParams, conjunction,
      actualUrl = url,
      elementId = 'jsonp-script-' + scriptTagCounter++;

    if (!cacheOk) {
      additionalQueryParams = '_=' + (new Date()).getTime();
      conjunction = (url.indexOf('?') == -1) ? '?' : '&';
      actualUrl = url + conjunction + additionalQueryParams;
    }

    // Set attributes on the script element
    element.setAttribute("type", "text/javascript");
    element.setAttribute("src", actualUrl);
    element.setAttribute("id", elementId);
    return element;
  }

  globalContext.Jsonp = {invoke : invokeJsonp, removeTag: removeTag};

}(this));


// example usage:
//
//  var scr1;
//
//  function cbFunc(data) {
//    // This is a jsonp callback. It gets invoked when the
//    // injected script tag gets executed by the browser.
//    if (data === null) { return; }
//    populateSelect(data.names, s3);
//    Jsonp.removeTag(scr1);
//  }
//
//  function retrieveChildNames(geonameId, cbName) {
//    var restUrl = 'http://api.example.com/children/187/alpha?cb=cbFunc';
//    scr1 = Jsonp.invoke(restUrl);
//  }
//