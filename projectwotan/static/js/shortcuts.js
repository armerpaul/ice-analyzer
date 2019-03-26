
window.getTemplate = window.getTemplate || function(templateId) {
    var elem = document.getElementById(templateId);
    return elem.textContent;
};

/**
 * You can't set a global delimiter pair, so here's some functions to set them by default.
 * https://stackoverflow.com/questions/41523427/cant-use-vue-config-delimiters-can-only-set-delimiters-on-new-vue
 */
var VUE_DELIMITERS = ['[[', ']]']

window.VueComponent = function(componentName, config){
    config.delimiters = VUE_DELIMITERS;
    config.template = getTemplate(componentName);

    return Vue.component(componentName, config);
}

window.VueApp = function(config){
    config.delimiters = VUE_DELIMITERS;
    return new Vue(config);
}