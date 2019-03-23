var MAIN_DATA_KEY = '_'

window.http = window.http || {
    queryParams: function(params) {
        return Object.keys(params)
            .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k]))
            .join('&');
    },
    get: function(url, params) {
        if (params) {
            var paramString = http.queryParams(params);

            if (paramString) {
                url += "?" + paramString;
            }
        }

        return fetch(url).then(function(response){
            if (response.ok) {
                return response.data;
            }

            throw "Error getting resource at " + url;
        });
    }
};