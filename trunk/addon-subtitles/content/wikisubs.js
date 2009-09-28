/* ***** BEGIN LICENSE BLOCK *****
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is mozilla.org code.
 *
 * The Initial Developer of the Original Code is Mozilla Corporation.
 * Portions created by the Initial Developer are Copyright (C) 2009
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *  Justin Dolske <dolske@mozilla.com> (original author)
 *  Felipe C. da S. Sanches <jucablues@users.sourceforge.net>
 *
 * Alternatively, the contents of this file may be used under the terms of
 * either the GNU General Public License Version 2 or later (the "GPL"), or
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
 * in which case the provisions of the GPL or the LGPL are applicable instead
 * of those above. If you wish to allow use of your version of this file only
 * under the terms of either the GPL or the LGPL, and not to allow others to
 * use your version of this file under the terms of the MPL, indicate your
 * decision by deleting the provisions above and replace them with the notice
 * and other provisions required by the GPL or the LGPL. If you do not delete
 * the provisions above, a recipient may use your version of this file under
 * the terms of any one of the MPL, the GPL or the LGPL.
 *
 * ***** END LICENSE BLOCK ***** */

var Wikisubs = {

    /*
     * init
     *
     */
    init : function () {
        let ios = Cc["@mozilla.org/network/io-service;1"].
                  getService(Ci.nsIIOService);
        let sheetURI = ios.newURI("chrome://wikisubs/skin/wikisubsHookup.css", null, null);
        let sss = Cc["@mozilla.org/content/style-sheet-service;1"].
                  getService(Ci.nsIStyleSheetService);
        if (!sss.sheetRegistered(sheetURI, sss.AGENT_SHEET))
            sss.loadAndRegisterSheet(sheetURI, sss.AGENT_SHEET);
    },

    loadMediawikiPage : function(servername, pagename, callback){

      var parse_response = function(text){
//TODO: remove this alert
//        alert("response:\n" + text);

        //this could be better:
        var content = text.split("<text xml:space=\"preserve\">")
        if (content.length == 1) return; //failed to load
        content = content[1].split("</text>")
        if (content.length == 1) return; //failed to load
        content = content[0];

//TODO: remove this alert
//        alert("content:\n" + content);
        callback(content);
      }
        
      this.sendRequest("POST", servername + "index.php?title=Special:Export/" + pagename, null, parse_response);
    },

    loadSubList: function(evt){
      var video = evt.target.parentNode;

      var parse_sub_list = function(data){
        var lines = data.split("\n");
        for (i in lines){
          //TODO try: catch:
          var string = lines[i].split("[[")[1];
          string = string.split("]]")[0];
          string = string.split("|");
          var src = string[0].trim();
          var title = string[1].trim();

alert(src);
alert(title);

          itext_node = document.createElement("itext");
          itext_node.setAttribute("src", src);
          itext_node.setAttribute("id", title);
          //itext_node.setAttribute("cat", "");
//          itext_node.setAttribute("lang", lang);
          video.appendChild(itext_node);
        }
      }

      var src = video.getElementsByTagName("source")[0].src;  //todo: improve it

      this.loadMediawikiPage("http://www.wstr.org/subs/", "Subtitles/URL/" + src, parse_sub_list);
    },

    loadSub: function(evt){
      var set_current_subtitle = function(subtitle_raw){
//        evt.target.innerHTML  = subtitle_raw;
//        var response_evt = document.createEvent("Events");
//        response_evt.initEvent("updatesubs", true, false);
//        evt.target.dispatchEvent(response_evt);

          var video = evt.target.parentNode;
          video.setSubtitle(subtitle_raw);

      }

      var wikipage = evt.target.getAttribute("wikipage");
      this.loadMediawikiPage("http://www.wstr.org/subs/", wikipage, set_current_subtitle);
    },

    sendRequest : function(method, url, data, callback) {

     	var xhr = new XMLHttpRequest();
	    var ajaxDataReader = function () {
		    if (xhr.readyState == 4) {
          callback(xhr.responseText);
		    }
	    }

	    xhr.onreadystatechange = ajaxDataReader;
	    try {
	        xhr.open(method,url, true);
	        xhr.send(data);
        }
	    catch(e){
		    alert("bad request");
	    }

    }
}

window.addEventListener("load", function() { Wikisubs.init(); }, false);
document.addEventListener("WikiSubsLoadSubList", function(e) { Wikisubs.loadSubList(e); }, false, true);
document.addEventListener("WikiSubsLoadSub", function(e) { Wikisubs.loadSub(e); }, false, true);

